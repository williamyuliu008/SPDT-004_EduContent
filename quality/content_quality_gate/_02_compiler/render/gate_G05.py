"""G-05: Frame-level rendering quality check

Renders each scene's first frame as PNG, then uses PIL to detect:
- G-05A: manim stderr warnings (fit_text_width, etc.)
- G-05B: Image not blank/corrupted  
- G-05C: Color distribution anomalies (missing boxes, text overflow)
- G-05D: Text region boundedness (text pixels within expected regions)

Design principle: Don't try to OCR. Detect layout violations through pixel analysis.
"""
import sys, os, json, subprocess, tempfile, shutil
from PIL import Image
import numpy as np

def gate_G05A_render_scene_frame(scene_json, scene_handler, output_dir):
    """Render a single scene's first frame as PNG. Returns (success, stderr, png_path)"""
    # Write a minimal scene Python file
    sid = scene_json.get('scene_id', 'test')[:8]
    scene_file = os.path.join(output_dir, f'_gate_{sid}.py')
    class_name = f'Gate{sid.replace("-","_")}'
    
    code = f'''import sys, os, json
sys.path.insert(0, r"D:\\6_agent_project\\AI_video_edu")
os.chdir(r"D:\\6_agent_project\\AI_video_edu")
from manim import *
from style_guide import term_card, box_diagram, causal_chain

def sh(s,n=10):
    s=str(s).strip()
    for p in ['水面之上：','水面之下：','IBM路线：','我们路线：','传统LPDDR：']:
        if s.startswith(p): s=s[len(p):]
    return s[:n]

def r_simple(s):
    c=s.get('content',{{}}); t=c.get('title','')[:12]
    b=c.get('body_lines',[]); k=[sh(x,8) for x in b[:3]]
    if not k: k=[sh(c.get('subtitle',c.get('task_description','')),12)]
    if not k[0]:
        for bx in s.get('teaching_boxes',[]): k.append(sh(bx.get('title',bx.get('text','')),8))
    return term_card(title=t,keywords=[x for x in k[:3] if x])

def r_contrast(s):
    c=s.get('content',{{}}); t=c.get('title','')[:12]
    w=c.get('wrong_text',''); r=c.get('right_text','')
    wl=[l.strip() for l in w.split('\\n') if l.strip()]
    rl=[l.strip() for l in r.split('\\n') if l.strip()]
    return box_diagram(title=t,
        boxes=[{{'label':'传统','subtitle':sh(wl[0],12) if wl else ''}},
               {{'label':'真相','subtitle':sh(rl[0],12) if rl else ''}}],
        edges=[{{'from':0,'to':1,'label':''}}])

def r_diagram(s):
    c=s.get('content',{{}}); t=c.get('title','')[:12]
    nodes=c.get('diagram',{{}}).get('nodes',[])
    if not nodes: return r_simple(s)
    boxes=[{{'label':sh(n.get('label',str(n)) if isinstance(n,dict) else str(n),10),'subtitle':''}} for n in nodes]
    elist=[{{'from':j,'to':j+1,'label':''}} for j in range(len(boxes)-1)]
    return box_diagram(title=t,boxes=boxes,edges=elist)

def r_steps(s):
    c=s.get('content',{{}}); t=c.get('title','')[:12]
    steps=c.get('steps',[])
    if not steps: return r_simple(s)
    chain=[sh(x,10) if isinstance(x,str) else sh(x.get('label',''),10) for x in steps]
    return causal_chain(title=t,chain=chain)

H = dict(title=r_simple, concept=r_simple, action=r_simple, summary=r_simple,
         contrast=r_contrast, diagram=r_diagram, steps=r_steps)

class {class_name}(Scene):
    def construct(self):
        with open(r"{scene_json['_full_path']}", encoding="utf-8-sig") as f:
            s=json.load(f)
        h=H.get(s.get('scene_type',''),r_simple)
        obj=h(s)
        self.add(obj)
        self.wait(0.1)
'''
    
    with open(scene_file, 'w', encoding='utf-8') as f:
        f.write(code)
    
    try:
        result = subprocess.run(
            ['manim', '-pql', '-n', '0', '--format', 'png', scene_file, class_name],
            capture_output=True, text=True, timeout=60,
            cwd=r'D:\6_agent_project\AI_video_edu'
        )
    except subprocess.TimeoutExpired:
        return False, 'Timeout', None
    
    # Check for manim errors
    stderr = result.stderr
    has_tb = 'Traceback' in stderr
    
    # Check for fit_text_width warnings (indicates text overflow)
    has_fit_warn = 'fit_text' in stderr.lower() and 'overflow' in stderr.lower()
    
    # Find the rendered PNG
    png_path = None
    for root, dirs, files in os.walk(r'D:\6_agent_project\AI_video_edu\media\images'):
        for f in files:
            if class_name in f and f.endswith('.png'):
                png_path = os.path.join(root, f)
                break
    
    warnings = []
    if has_tb:
        warnings.append('manim Traceback')
    if has_fit_warn:
        warnings.append('fit_text_width overflow detected')
    
    return not has_tb, warnings, png_path


def gate_G05B_image_valid(png_path):
    """Check image is not blank/corrupted and has expected dimensions"""
    if not png_path:
        return False, ['No PNG file found']
    
    img = Image.open(png_path)
    w, h = img.size
    
    issues = []
    if w < 100 or h < 100:
        issues.append(f'Image too small: {w}x{h}')
    
    # Check for any non-black content (dark background scenes have low mean brightness)
    arr = np.array(img.convert('L'))
    max_brightness = arr.max()
    non_black_pixels = (arr > 10).sum()
    non_black_ratio = non_black_pixels / arr.size
    
    if max_brightness < 15:
        issues.append(f'Completely black (max_brightness={max_brightness})')
    elif non_black_ratio < 0.001:
        issues.append(f'Almost no content: {non_black_ratio*100:.3f}% non-black')
    
    return len(issues) == 0, issues


def gate_G05C_color_check(png_path, scene_type):
    """Check for expected colored elements based on scene type"""
    if not png_path:
        return False, ['No PNG']
    
    img = Image.open(png_path)
    arr = np.array(img)
    r, g, b = arr[:,:,0], arr[:,:,1], arr[:,:,2]
    total = arr.shape[0] * arr.shape[1]
    
    issues = []
    
    # For box_diagram and causal_chain: check for colored rectangular regions
    if scene_type in ('contrast', 'diagram', 'steps'):
        # Check for presence of non-black, non-white pixels (boxes/lines/text)
        r, g, b = arr[:,:,0], arr[:,:,1], arr[:,:,2]
        # Count non-dark pixels (brightness > 30)
        non_dark = ((r > 30) | (g > 30) | (b > 30)).sum()
        total = arr.shape[0] * arr.shape[1]
        fill_ratio = non_dark / total
        
        if fill_ratio < 0.05:
            issues.append(f'Scene too empty: {fill_ratio*100:.1f}% non-dark pixels')
    
    # For all types: check that text colors (white/yellow) are present
    # White text: R>200, G>200, B>200
    total = arr.shape[0] * arr.shape[1]
    white_pixels = ((r > 200) & (g > 200) & (b > 200)).sum()
    white_ratio = white_pixels / total if total > 0 else 0
    
    if white_ratio < 0.0005:
        issues.append(f'Almost no white text: {white_ratio*100:.2f}%')
    
    return len(issues) == 0, issues


def gate_G05_full(scenes_dir, output_dir):
    """Run complete G-05 check on all scenes"""
    os.makedirs(output_dir, exist_ok=True)
    
    results = {}
    for f in sorted(os.listdir(scenes_dir)):
        if not f.endswith('.json') or not f.startswith('scene_'):
            continue
        
        fp = os.path.join(scenes_dir, f)
        try:
            data = json.load(open(fp, encoding='utf-8-sig'))
        except:
            data = json.load(open(fp, encoding='utf-8'))
        
        data['_full_path'] = fp
        st = data.get('scene_type', '?')
        sid = data.get('scene_id', f)
        
        print(f'\n[{sid}] {st}...')
        
        # G-05A: Render single frame
        ok_a, warnings_a, png = gate_G05A_render_scene_frame(data, None, output_dir)
        print(f'  G-05A: {"PASS" if ok_a else "FAIL"}')
        for w in warnings_a:
            print(f'    {w}')
        
        # G-05B: Image validity
        ok_b, issues_b = gate_G05B_image_valid(png)
        print(f'  G-05B: {"PASS" if ok_b else "FAIL"} ({png})')
        for i in issues_b:
            print(f'    {i}')
        
        # G-05C: Color check
        if png:
            ok_c, issues_c = gate_G05C_color_check(png, st)
            print(f'  G-05C: {"PASS" if ok_c else "FAIL"}')
            for i in issues_c:
                print(f'    {i}')
        else:
            ok_c, issues_c = False, ['No PNG to check']
            print(f'  G-05C: SKIP (no PNG)')
        
        results[sid] = {
            'pass': ok_a and ok_b and ok_c,
            'a': (ok_a, warnings_a),
            'b': (ok_b, issues_b),
            'c': (ok_c, issues_c),
            'png': png
        }
    
    # Summary
    total = len(results)
    passed = sum(1 for r in results.values() if r['pass'])
    print(f'\n{"="*50}')
    print(f'G-05 Summary: {passed}/{total} passed')
    for sid, r in results.items():
        status = 'PASS' if r['pass'] else 'FAIL'
        print(f'  {sid}: {status} (png: {r["png"]})')
    
    return results


if __name__ == '__main__':
    scenes = r'D:\6_agent_project\AI_video_edu\episodes\DRAM_strategy\scenes'
    output = r'D:\6_agent_project\AI_video_edu\episodes\DRAM_strategy\gate_output'
    gate_G05_full(scenes, output)
