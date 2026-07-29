"""Layout Discretization — Complete input-output mapping for all 4 style_guide functions

Design elements: title, keyword, label, subtitle, chain_item, cell, header
Text length tiers: S(≤4), M(5-8), L(9-12), XL(13+)
Item count tiers: 1, 2, 3, 4, 5+

Each function analyzed for: safe params, boundary conditions, downgrade paths
"""
from itertools import product

# ====== Design Element Constraints (empirically validated) ======
ELEMENTS = {
    'title':       {'max_chars': 12, 'tiers': {'S':(1,4), 'M':(5,8), 'L':(9,12), 'XL':(13,999)}},
    'keyword':     {'max_chars': 8,  'max_count': 3, 'tiers': {'S':(1,3), 'M':(4,6), 'L':(7,8), 'XL':(9,999)}},
    'label':       {'max_chars': 8,  'max_count': 4, 'tiers': {'S':(1,3), 'M':(4,6), 'L':(7,8), 'XL':(9,999)}},
    'subtitle':    {'max_chars': 10, 'tiers': {'S':(1,4), 'M':(5,8), 'L':(9,10), 'XL':(11,999)}},
    'chain_item':  {'max_chars': 8,  'max_count': 5, 'tiers': {'S':(1,3), 'M':(4,6), 'L':(7,8), 'XL':(9,999)}},
    'cell':        {'max_chars': 8,  'max_rows': 5, 'max_cols': 4, 'tiers': {'S':(1,3), 'M':(4,6), 'L':(7,8), 'XL':(9,999)}},
    'header':      {'max_chars': 8,  'max_count': 4},
}

# ====== Function-specific mapping ======
# Each: (function, safe limits, overflow behaviors, downgrade paths)

FUNCTION_MAP = {
    'term_card': {
        'elements': ['title', 'keyword'],
        'safe': {'title':'M', 'keyword':['M','M','S']},  # title≤8, 3 keywords≤8/8/6
        'overflow': {
            'title_XL': 'TRUNCATE to 12 chars',
            'keyword_XL': 'TRUNCATE to 8 chars',
            'keyword_count_4+': 'TRUNCATE to 3 keywords',
        },
        'best_for': ['single concept', 'simple definition', 'call to action'],
    },
    'box_diagram': {
        'elements': ['title', 'label', 'subtitle'],
        'safe': {'title':'M', 'label':'M', 'subtitle':'S', 'count':4},
        'overflow': {
            'label_XL': 'TRUNCATE to 8 chars',
            'subtitle_XL': 'TRUNCATE to 10 chars',
            'count_5+': 'DOWNGRADE to causal_chain',
        },
        'best_for': ['dual comparison', 'parallel concepts', 'small node sets'],
    },
    'causal_chain': {
        'elements': ['title', 'chain_item'],
        'safe': {'title':'M', 'chain_item':'M', 'count':5},
        'overflow': {
            'chain_item_XL': 'TRUNCATE to 8 chars',
            'count_6+': 'TRUNCATE to 5 items',
        },
        'best_for': ['sequential steps', 'ordered flow', 'timeline'],
    },
    'comparison_table': {
        'elements': ['title', 'header', 'cell'],
        'safe': {'title':'M', 'header':'M', 'cell':'M', 'rows':4, 'cols':4},
        'overflow': {
            'cell_XL': 'TRUNCATE to 8 chars',
            'rows_6+': 'TRUNCATE to 5 rows',
            'cols_5+': 'TRUNCATE to 4 cols',
        },
        'best_for': ['multi-row comparison', 'structured data', 'features table'],
    },
}

# ====== Scene type → best function selection ======
SCENE_FUNCTION = {
    ('concept',  'S','S'): ('term_card', 'PASS'),
    ('concept',  'M','M'): ('term_card', 'PASS'),
    ('concept',  'L','M'): ('term_card', 'WARN_title'),
    ('concept',  'XL','M'): ('term_card', 'WARN_title'),
    ('contrast', 'S','S'): ('box_diagram', 'PASS'),
    ('contrast', 'M','L'): ('comparison_table', 'PASS'),
    ('contrast', 'M','XL'): ('comparison_table', 'WARN_cell'),
    ('diagram',  'S','S'): ('box_diagram', 'PASS'),
    ('diagram',  'M','M'): ('box_diagram', 'PASS'),  
    ('diagram',  'L','M'): ('causal_chain', 'DOWNGRADE_count'),
    ('diagram',  'XL','XL'): ('causal_chain', 'DOWNGRADE_count'),
    ('steps',    'S','S'): ('causal_chain', 'PASS'),
    ('steps',    'M','M'): ('causal_chain', 'PASS'),
    ('steps',    'L','M'): ('causal_chain', 'WARN_item'),
    ('steps',    'XL','L'): ('causal_chain', 'DOWNGRADE_truncate'),
}

# ====== Complete discrete mapping table ======
def generate_mapping():
    print('='*70)
    print('Layout Discretization — Complete Input-Output Mapping')
    print('='*70)
    
    # For each scene_type, enumerate all (title_tier, content_tier, item_count) combos
    scene_types = ['concept', 'contrast', 'diagram', 'steps', 'action', 'summary']
    tiers = ['S', 'M', 'L', 'XL']
    counts = [1, 2, 3, 4, 5]
    
    for st in scene_types:
        print(f'\n--- {st} ---')
        print(f'{"Title":>6} {"Content":>8} {"Items":>5} {"Function":>18} {"Status":>20} {"Rule":>30}')
        print('-'*70)
        
        for t, c, n in product(tiers[:3], tiers[:3], counts[:4]):  # sample key combos
            key = (st, t, c)
            func, status = SCENE_FUNCTION.get(key, ('term_card', 'FALLBACK'))
            
            # Determine truncation/safety rule
            if status == 'PASS':
                rule = 'All params within safe limits'
            elif 'WARN' in status:
                if 'title' in status: rule = f'Title truncate to 12 chars'
                elif 'cell' in status: rule = f'Cell truncate to 8 chars'
                elif 'item' in status: rule = f'Chain item truncate to 8 chars'
                else: rule = f'Truncation applied'
            elif 'DOWNGRADE' in status:
                if 'count' in status: rule = f'Downgrade: box->chain (count={n})'
                elif 'truncate' in status: rule = f'Truncate chain to 5 items'
                else: rule = f'Function routing adjusted'
            else:
                rule = 'Default term_card fallback'
            
            print(f'{t:>6} {c:>8} {n:>5} {func:>18} {status:>20} {rule:>30}')

# ====== Adversarial boundary test ======
def adversarial_test():
    print('\n' + '='*70)
    print('Adversarial Boundary Test — Worst-case inputs for each function')
    print('='*70)
    
    # For each function, test the most extreme valid inputs
    tests = [
        ('term_card', 'title=12chars_abcdefghij', ['keyword1_abcdefgh', 'keyword2_abcdefgh', 'keyword3_abcdefgh'], 'max_all'),
        ('box_diagram', 'title_12chars_ab', [{'label':'label_8chars','subtitle':'sub_10chars'} for _ in range(4)], 'max_nodes'),
        ('causal_chain', 'title_12chars_ab', ['item_8chars' for _ in range(5)], 'max_chain'),
        ('comparison_table', 'title_12chars_ab', {'rows':[['cell_8ch' for _ in range(4)] for _ in range(5)], 'headers':['hdr_8cha' for _ in range(4)]}, 'max_table'),
    ]
    
    for func, title, content, desc in tests:
        # Simulate adapter processing
        title_len = len(title)
        title_tier = 'S' if title_len<=4 else 'M' if title_len<=8 else 'L' if title_len<=12 else 'XL'
        
        if func == 'term_card':
            kw_lens = [len(k) for k in content]
            kw_tiers = ['S' if l<=3 else 'M' if l<=6 else 'L' if l<=8 else 'XL' for l in kw_lens]
            has_overflow = any(t == 'XL' for t in [title_tier] + kw_tiers)
            result = 'WARN_TRUNCATE' if has_overflow else 'PASS'
        elif func == 'box_diagram':
            node_count = len(content)
            label_lens = [len(b['label']) for b in content]
            has_overflow = title_tier == 'XL' or node_count > 4 or any(l > 8 for l in label_lens)
            result = 'DOWNGRADE' if node_count > 4 else ('WARN' if has_overflow else 'PASS')
        elif func == 'causal_chain':
            item_count = len(content)
            item_lens = [len(i) for i in content]
            has_overflow = title_tier == 'XL' or item_count > 5 or any(l > 8 for l in item_lens)
            result = 'TRUNCATE' if item_count > 5 else ('WARN' if has_overflow else 'PASS')
        else:
            result = 'CHECK'
        
        print(f'\n{func} [{desc}]:')
        print(f'  title: {title_tier} tier ({title_len} chars)')
        print(f'  content: {len(content)} items')
        print(f'  result: {result}')

if __name__ == '__main__':
    generate_mapping()
    adversarial_test()
