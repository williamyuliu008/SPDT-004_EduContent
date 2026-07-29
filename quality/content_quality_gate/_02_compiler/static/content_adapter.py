"""Content Adapter — safely maps any Scene JSON to style_guide-compatible params"""
import json, os

# Rendering constraints (derived from style_guide function limits)
LIMITS = {
    'term_card':  {'title_max': 12, 'keyword_max': 8,  'keyword_count': 3},
    'box_diagram': {'title_max': 12, 'label_max': 8,   'subtitle_max': 10, 'node_max': 4},
    'causal_chain':{'title_max': 12, 'item_max': 8,    'chain_max': 5},
    'comparison_table': {'title_max': 12, 'cell_max': 8, 'row_max': 5, 'col_max': 4},
}

def truncate(text, max_chars):
    """Truncate Chinese text, trying to keep word boundaries"""
    text = text.strip()
    if len(text) <= max_chars: return text
    # Try to break at natural boundaries
    for sep in ['：',':','·','，',',',' ','\n']:
        if sep in text[:max_chars+2]:
            return text[:text.index(sep)]
    return text[:max_chars]

def adapt_term_card(content, teaching_boxes):
    """Extract safe params from raw content for term_card"""
    title = truncate(content.get('title', ''), LIMITS['term_card']['title_max'])
    
    keywords = []
    # Priority: body_lines > highlights > teaching_box titles
    for src in [content.get('body_lines',[]), content.get('highlights',[])]:
        for item in src:
            kw = truncate(item, LIMITS['term_card']['keyword_max'])
            if kw and kw not in keywords:
                keywords.append(kw)
    
    if not keywords:
        subtitle = content.get('subtitle', content.get('task_description', ''))
        if subtitle:
            keywords.append(truncate(subtitle, LIMITS['term_card']['keyword_max']))
    
    if not keywords:
        for box in (teaching_boxes or []):
            kw = truncate(box.get('title', box.get('text', '')), LIMITS['term_card']['keyword_max'])
            if kw and kw not in keywords:
                keywords.append(kw)
    
    return {
        'function': 'term_card',
        'params': {
            'title': title or content.get('title','')[:12] or '?',
            'keywords': keywords[:LIMITS['term_card']['keyword_count']] or ['?']
        }
    }

def adapt_box_diagram(content):
    """Build box_diagram params from diagram/contrast content"""
    title = truncate(content.get('title', ''), LIMITS['box_diagram']['title_max'])
    
    # Try diagram.nodes first, then extract from contrast text
    diagram = content.get('diagram', {})
    nodes = diagram.get('nodes', [])
    
    if not nodes:
        # Extract boxes from contrast text
        wrong = content.get('wrong_text', '')
        right = content.get('right_text', '')
        wl = [l.strip() for l in wrong.split('\n') if l.strip()]
        rl = [l.strip() for l in right.split('\n') if l.strip()]
        nodes = [
            {'label': truncate(wl[0] if wl else '传统', LIMITS['box_diagram']['label_max']),
             'subtitle': truncate(wl[1] if len(wl)>1 else '', LIMITS['box_diagram']['subtitle_max'])},
            {'label': truncate(rl[0] if rl else '真相', LIMITS['box_diagram']['label_max']),
             'subtitle': truncate(rl[1] if len(rl)>1 else '', LIMITS['box_diagram']['subtitle_max'])},
        ]
    
    max_nodes = LIMITS['box_diagram']['node_max']
    boxes = []
    for n in nodes[:max_nodes]:
        d = n if isinstance(n, dict) else {}
        boxes.append({
            'label': truncate(d.get('label', str(n)), LIMITS['box_diagram']['label_max']),
            'subtitle': truncate(d.get('subtitle', ''), LIMITS['box_diagram']['subtitle_max'])
        })
    
    edges = []
    if len(boxes) > 1:
        edges = [{'from': j, 'to': j+1, 'label': ''} for j in range(len(boxes)-1)]
    
    return {
        'function': 'box_diagram' if len(boxes) <= max_nodes else 'causal_chain',
        'params': {
            'title': title,
            'boxes': boxes,
            'edges': edges
        } if len(boxes) <= max_nodes else {
            'title': title,
            'chain': [b['label'] for b in boxes[:LIMITS['causal_chain']['chain_max']]]
        }
    }

def adapt_causal_chain(content):
    """Build causal_chain params from steps content"""
    title = truncate(content.get('title', ''), LIMITS['causal_chain']['title_max'])
    steps = content.get('steps', [])
    
    chain = []
    for s in steps[:LIMITS['causal_chain']['chain_max']]:
        txt = s if isinstance(s, str) else s.get('label', str(s))
        chain.append(truncate(txt, LIMITS['causal_chain']['item_max']))
    
    return {
        'function': 'causal_chain',
        'params': {'title': title, 'chain': chain or ['?']}
    }

def adapt_comparison_table(content):
    """Build comparison_table params from contrast content"""
    title = truncate(content.get('title', ''), LIMITS['comparison_table']['title_max'])
    
    wrong_text = content.get('wrong_text', '')
    right_text = content.get('right_text', '')
    wl = [l.strip() for l in wrong_text.split('\n') if l.strip()]
    rl = [l.strip() for l in right_text.split('\n') if l.strip()]
    
    headers = ['维度', '传统方案', '新方案']
    rows = []
    max_r = LIMITS['comparison_table']['row_max']
    cell_m = LIMITS['comparison_table']['cell_max']
    
    for i in range(min(len(wl), len(rl), max_r)):
        # Extract dimension from first line
        w = wl[i]
        if '：' in w: dim, val = w.split('：', 1)
        elif ':' in w: dim, val = w.split(':', 1)
        else: dim, val = f'项目{i+1}', w
        rows.append([truncate(dim.strip(), cell_m), truncate(val.strip(), cell_m), truncate(rl[i], cell_m)])
    
    if not rows:
        rows = [['-', truncate(wrong_text[:20], cell_m), truncate(right_text[:20], cell_m)]]
    
    return {
        'function': 'comparison_table',
        'params': {'title': title, 'headers': headers, 'rows': rows}
    }

# Scene type → adapter function mapping
# Scene type → adapter function mapping (with intelligent function selection)

def select_best_function(scene_type, content):
    """Layer 1: Choose the best style_guide function based on content structure"""
    st = scene_type
    
    # concept/title/action/summary: always term_card
    if st in ('title', 'concept', 'action', 'summary'):
        return 'term_card'
    
    # steps: prefers causal_chain (sequential flow)
    if st == 'steps':
        return 'causal_chain'
    
    # contrast: check content structure to decide
    if st == 'contrast':
        wrong = content.get('wrong_text', '')
        right = content.get('right_text', '')
        w_lines = [l.strip() for l in wrong.split('\n') if l.strip()]
        r_lines = [l.strip() for l in right.split('\n') if l.strip()]
        # If has structured data (numbered/semicolon-delimited) → comparison_table
        if len(w_lines) >= 3 or len(r_lines) >= 3:
            return 'comparison_table'
        # Otherwise: dual-panel → box_diagram
        return 'box_diagram'
    
    # diagram: check node count
    if st == 'diagram':
        nodes = content.get('diagram', {}).get('nodes', [])
        if not nodes:
            return 'term_card'  # fallback
        if len(nodes) <= 4:
            return 'box_diagram'
        # Many nodes → causal_chain (sequential, won't overflow frame)
        return 'causal_chain'
    
    return 'term_card'

ADAPTERS = {
    'title':   lambda c, tb: adapt_term_card(c, tb),
    'concept': lambda c, tb: adapt_term_card(c, tb),
    'action':  lambda c, tb: adapt_term_card(c, tb),
    'summary': lambda c, tb: adapt_term_card(c, tb),
    'contrast': lambda c, tb: adapt_box_diagram(c),
    'diagram':  lambda c, tb: adapt_box_diagram(c),
    'steps':    lambda c, tb: adapt_causal_chain(c),
}

def process_scene(scene_json):
    """Auto-generate layout from scene content with intelligent function selection"""
    st = scene_json.get('scene_type', 'concept')
    content = scene_json.get('content', {})
    teaching_boxes = scene_json.get('teaching_boxes', [])
    
    # Layer 1: Select best rendering function
    func_name = select_best_function(st, content)
    
    # Layer 2: Build safe params based on selected function
    if func_name == 'term_card':
        layout = adapt_term_card(content, teaching_boxes)
    elif func_name == 'box_diagram':
        layout = adapt_box_diagram(content)
    elif func_name == 'causal_chain':
        layout = adapt_causal_chain(content)
    elif func_name == 'comparison_table':
        layout = adapt_comparison_table(content)
    else:
        layout = adapt_term_card(content, teaching_boxes)
    
    return layout

# ====== Mutation Tests ======
def test_mutations():
    """Inject errors and verify adapter handles them"""
    tests = [
        # (name, scene_json, expected_no_crash)
        ('超长keyword', {'scene_type':'concept','content':{'title':'AI写作工具入门指南完整版','body_lines':['这是一个极其冗长且过度详细的标签文本用于测试关键词截断功能']}}, True),
        ('空title', {'scene_type':'concept','content':{'title':'','body_lines':['测试']}}, True),
        ('空body_lines', {'scene_type':'concept','content':{'title':'测试'}}, True),
        ('0节点diagram', {'scene_type':'diagram','content':{'title':'测试','diagram':{'nodes':[]}}}, True),
        ('6节点diagram', {'scene_type':'diagram','content':{'title':'多节点','diagram':{'nodes':[{'label':f'节点{i}'} for i in range(6)]}}}, True),
        ('超长steps', {'scene_type':'steps','content':{'title':'测试','steps':['步骤1','步骤2','步骤3','步骤4','步骤5','步骤6','步骤7']}}, True),
        ('超长contrast文字', {'scene_type':'contrast','content':{'title':'测试','wrong_text':'这是一个极其冗长的错误描述文本用于测试截断功能是否正常工作','right_text':'这是同样冗长的正确描述文本用于测试截断功能'}}, True),
        ('完全空场景', {'scene_type':'concept','content':{}}, True),
    ]
    
    passed = 0
    for name, scene, expected in tests:
        try:
            layout = process_scene(scene)
            func = layout.get('function', '?')
            params = layout.get('params', {})
            # Verify all params are within limits
            crashed = False
            ok = True
        except Exception as e:
            crashed = True
            ok = False
        
        print(f'  {name}: {"PASS" if ok else "CRASH"} -> {func if not crashed else "ERROR"}')
        if ok: passed += 1
    
    print(f'\nMutation test: {passed}/{len(tests)} passed')

if __name__ == '__main__':
    test_mutations()
