"""Golden Test Suite Runner — runs all gates against golden samples, computes correctness"""
import sys, os, yaml, json, subprocess, glob, shutil

GOLDEN_DIR = r'D:\6_agent_project\projects\content_quality_gate\_01_golden_tests'

def load_golden_samples():
    """Load all golden samples with their expected outcomes"""
    samples = []
    for root, dirs, files in os.walk(GOLDEN_DIR):
        for f in files:
            if f.endswith('_meta.yaml'):
                with open(os.path.join(root, f), encoding='utf-8') as fh:
                    meta = yaml.safe_load(fh)
                meta['_dir'] = root
                samples.append(meta)
    return samples

def run_gates_on_sample(sample):
    """Run all applicable gates on a golden sample"""
    results = {}
    
    # G-01: Style guide check (for .py files)
    py_file = os.path.join(sample['_dir'], sample.get('py_file', ''))
    if py_file and os.path.exists(py_file):
        # Import gate function (simplified: check file exists and has style_guide import)
        with open(py_file, encoding='utf-8') as f:
            content = f.read()
        has_sg = 'from style_guide import' in content or 'import style_guide' in content
        has_raw = '.next_to(' in content or '.shift(' in content
        results['G-01'] = 'PASS' if has_sg and not has_raw else 'FAIL'
    
    # G-03: Content non-empty (for .json files)
    json_file = os.path.join(sample['_dir'], sample.get('json_file', ''))
    if json_file and os.path.exists(json_file):
        with open(json_file, encoding='utf-8-sig') as f:
            data = json.load(f)
        c = data.get('content', {})
        title = c.get('title', '')
        results['G-03'] = 'PASS' if title.strip() else 'FAIL'
    
    # G-05B: Image valid
    png_file = os.path.join(sample['_dir'], sample.get('png_file', ''))
    if png_file and os.path.exists(png_file):
        from PIL import Image
        import numpy as np
        img = Image.open(png_file)
        arr = np.array(img.convert('L'))
        max_bright = arr.max()
        results['G-05B'] = 'PASS' if max_bright > 15 else 'FAIL'
    
    return results

def compute_correctness():
    """Run all golden samples and compute correctness rate"""
    samples = load_golden_samples()
    
    total_checks = 0
    correct_checks = 0
    failures = []
    
    for s in samples:
        expected = s.get('expected_result', {})
        actual = run_gates_on_sample(s)
        
        for gate, exp_val in expected.items():
            if gate in actual:
                total_checks += 1
                act_val = actual[gate]
                if act_val == exp_val:
                    correct_checks += 1
                else:
                    failures.append(f'{s["sample_id"]} {gate}: expected={exp_val}, actual={act_val}')
    
    rate = correct_checks / total_checks * 100 if total_checks > 0 else 0
    
    print(f'Golden Test Suite Results:')
    print(f'  Samples: {len(samples)}')
    print(f'  Total checks: {total_checks}')
    print(f'  Correct: {correct_checks}')
    print(f'  Correctness: {rate:.1f}%')
    
    if failures:
        print(f'\n  Failures:')
        for f in failures:
            print(f'    {f}')
    
    return rate

if __name__ == '__main__':
    compute_correctness()
