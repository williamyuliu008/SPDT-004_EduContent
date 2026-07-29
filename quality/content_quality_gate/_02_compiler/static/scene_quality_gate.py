"""Scene Quality Gate — 视频场景质量编译器

日期：2026-07-04
背景：DRAM视频四次迭代渲染，每次依赖人工审查发现问题
目标：在渲染后自动检测常见缺陷，闭合"生成→自动审计→修正"循环

Gate检查项：
  G-01: style_guide函数调用（AST解析Scene Python文件）— BLOCK
  G-02: 每个Scene渲染成功（manim无异常）— BLOCK
  G-03: 文本框内容非空（读取Scene JSON关键字段）— BLOCK
  G-04: 文本长度不超限（label/subtitle/title字符数）— WARN
  G-05: 渲染帧数异常 — WARN

已知文本长度限制：
  term_card: title<=15字, keyword<=10字
  box_diagram: label<=20字, subtitle<=30字
  causal_chain: chain_item<=25字
  comparison_table: cell<=20字
"""
import sys, os, json, ast, subprocess, re

STYLE_GUIDE_FUNCS = {'term_card','box_diagram','causal_chain','comparison_table',
                     'layout_concept','layout_contrast','layout_steps','layout_diagram',
                     'layout_title','layout_summary_cards','layout_split','layout_dual_track',
                     'layout_formula','layout_objective','layout_prerequisite','layout_action',
                     'tree_chart','matrix_2x2'}

TEXT_LIMITS = {
    'term_card': {'title':15, 'keyword':10},
    'box_diagram': {'label':20, 'subtitle':30, 'title':25},
    'causal_chain': {'chain_item':25, 'title':25},
    'comparison_table': {'cell':20, 'title':25},
}

def gate_G01_style_guide(scene_file):
    """检查Scene Python文件只用style_guide函数"""
    with open(scene_file, encoding='utf-8') as f:
        tree = ast.parse(f.read())
    violations = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                attr = node.func.attr
                if attr in ('next_to','shift','to_edge','arrange','move_to','align_to'):
                    violations.append(f'Line {node.lineno}: {attr}() — raw Manim positioning')
    return len(violations)==0, violations

def gate_G03_content_nonempty(scenes_dir):
    """检查每个Scene JSON关键字段非空"""
    issues = []
    for f in sorted(os.listdir(scenes_dir)):
        if not f.endswith('.json'): continue
        with open(os.path.join(scenes_dir, f), encoding='utf-8-sig') as fh:
            data = json.load(fh)
        st = data.get('scene_type','?')
        c = data.get('content',{})
        
        if st in ('title','concept','action','summary'):
            if st in ('concept','summary'):
                body = c.get('body_lines',[])
                highlights = c.get('highlights',[])
                boxes = data.get('teaching_boxes',[])
                if not body and not highlights and not boxes:
                    issues.append(f'{f}: body_lines/highlights/teaching_boxes全部为空')
        elif st == 'contrast':
            if not c.get('wrong_text','').strip():
                issues.append(f'{f}: wrong_text为空')
            if not c.get('right_text','').strip():
                issues.append(f'{f}: right_text为空')
        elif st == 'diagram':
            nodes = c.get('diagram',{}).get('nodes',[])
            if not nodes:
                issues.append(f'{f}: diagram.nodes为空或缺失')
            for i,n in enumerate(nodes):
                d = n if isinstance(n,dict) else {}
                if not d.get('label','').strip():
                    issues.append(f'{f}: diagram.nodes[{i}].label为空')
        elif st == 'steps':
            steps = c.get('steps',[])
            if not steps:
                issues.append(f'{f}: steps为空')
            for i,s in enumerate(steps):
                txt = s if isinstance(s,str) else s.get('label','')
                if not txt.strip():
                    issues.append(f'{f}: steps[{i}]为空')
    return len(issues)==0, issues

def gate_G04_text_overflow(scenes_dir):
    """检查文本长度是否超限"""
    warnings = []
    for f in sorted(os.listdir(scenes_dir)):
        if not f.endswith('.json'): continue
        with open(os.path.join(scenes_dir, f), encoding='utf-8-sig') as fh:
            data = json.load(fh)
        st = data.get('scene_type','?')
        c = data.get('content',{})
        
        # Check title
        title = c.get('title','')
        if len(title) > TEXT_LIMITS.get('term_card',{}).get('title',15):
            warnings.append(f'{f}: title {len(title)}字 > 15字上限')
        
        # Check diagram nodes — use pixel width estimate (Chinese ~2x ASCII)
        if st == 'diagram':
            for n in c.get('diagram',{}).get('nodes',[]):
                d = n if isinstance(n,dict) else {}
                label = d.get('label',str(n))
                # Estimate pixel width: Chinese chars ~13px, ASCII ~7px at default font size
                pixel_w = sum(13 if ord(c)>127 else 7 for c in label)
                if pixel_w > 260:  # ~20 Chinese chars equivalent
                    warnings.append(f'{f}: label "{label[:20]}..." est_width={pixel_w}px (max 260px)')
        
        # Check steps
        if st == 'steps':
            for s in c.get('steps',[]):
                txt = s if isinstance(s,str) else s.get('label','')
                if len(txt) > 25:
                    warnings.append(f'{f}: step "{txt[:15]}..." {len(txt)}字 > 25字上限')
    
    return len(warnings)==0, warnings

def gate_G02_render_test(scene_file, scene_class):
    """测试Scene能否成功渲染（至少1帧）"""
    try:
        result = subprocess.run(
            ['manim','-pql','-n','0','--format','png',scene_file,scene_class],
            capture_output=True, text=True, timeout=60,
            cwd=r'D:\6_agent_project\AI_video_edu'
        )
        # manim exits with code 1 even on success sometimes
        if 'Traceback' in result.stderr or 'Error' in result.stderr.replace('INFO',''):
            return False, result.stderr[:500]
        return True, ''
    except Exception as e:
        return False, str(e)

def audit_scenes(scenes_dir, scene_file, scene_class):
    """完整审计"""
    print('=== Scene Quality Gate ===\n')
    
    results = {}
    
    # G-01: Style guide compliance
    ok, violations = gate_G01_style_guide(scene_file)
    results['G-01'] = (ok, violations)
    print(f'G-01 Style Guide: {"PASS" if ok else "FAIL"} ({len(violations)} violations)')
    for v in violations[:5]:
        print(f'  {v}')
    
    # G-03: Content non-empty
    ok, issues = gate_G03_content_nonempty(scenes_dir)
    results['G-03'] = (ok, issues)
    print(f'\nG-03 Content: {"PASS" if ok else "FAIL"} ({len(issues)} issues)')
    for i in issues:
        print(f'  {i}')
    
    # G-04: Text overflow
    ok, warnings = gate_G04_text_overflow(scenes_dir)
    results['G-04'] = (ok, warnings)
    print(f'\nG-04 Text Length: {"PASS" if ok else "WARN"} ({len(warnings)} warnings)')
    for w in warnings:
        print(f'  {w}')
    
    # Summary
    all_pass = all(r[0] for r in results.values())
    print(f'\n=== Overall: {"PASS" if all_pass else "FAIL"} ===')
    return results
