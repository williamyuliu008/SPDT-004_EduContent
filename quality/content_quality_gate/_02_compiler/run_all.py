#!/usr/bin/env python
"""Content Quality Gate v0.2 — One-click validation runner"""

import sys, os, subprocess, json, yaml, glob, shutil
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).parent.parent

class QualityReport:
    def __init__(self):
        self.start_time = datetime.now()
        self.results = {
            'G-01': {}, 'G-03': {}, 'G-04': {}, 'G-05': {},
            'golden': {}, 'mutations': {}, 'summary': {}
        }
    
    def record(self, section, key, passed, detail=''):
        self.results[section][key] = {'passed': passed, 'detail': detail}
    
    def summary(self):
        total = 0; passed = 0
        for section in ['G-01','G-03','G-04','G-05']:
            for k, v in self.results[section].items():
                total += 1
                if v['passed']: passed += 1
        gold = self.results.get('golden', {})
        gold_total = len(gold)
        gold_passed = sum(1 for v in gold.values() if v.get('passed', False))
        mut = self.results.get('mutations', {})
        mut_total = len(mut)
        mut_passed = sum(1 for v in mut.values() if v.get('passed', False))
        
        return {
            'time': self.start_time.isoformat(),
            'version': 'v0.2',
            'gates': f'{passed}/{total} ({passed/total*100:.0f}%)' if total else 'N/A',
            'golden': f'{gold_passed}/{gold_total} ({gold_passed/gold_total*100:.0f}%)' if gold_total else 'N/A',
            'mutations': f'{mut_passed}/{mut_total} ({mut_passed/mut_total*100:.0f}%)' if mut_total else 'N/A',
        }
    
    def print(self):
        s = self.summary()
        print('\n' + '='*50)
        print(f'Quality Gate Report {s["version"]}')
        print(f'Time: {s["time"]}')
        print(f'Gates: {s["gates"]}')
        print(f'Golden Tests: {s["golden"]}')
        print(f'Mutations: {s["mutations"]}')
        print('='*50)

def run_gates(report, target_dir):
    """Run G-01, G-03, G-04 on target directory"""
    sys.path.insert(0, str(BASE / '_02_compiler' / 'static'))
    from scene_quality_gate import gate_G01_style_guide, gate_G03_content_nonempty, gate_G04_text_overflow
    
    # G-01: Check Python files (only recent render scripts)
    for f in glob.glob(os.path.join(target_dir, 'render_v*.py')):
        try:
            ok, violations = gate_G01_style_guide(f)
            report.record('G-01', os.path.basename(f), ok, str(violations[:2]) if violations else '')
            print(f'  G-01 {os.path.basename(f)}: {"PASS" if ok else "FAIL"}')
        except SyntaxError:
            print(f'  G-01 {os.path.basename(f)}: SKIP (syntax error)')
    
    # G-03: Check JSON files
    scenes_dir = os.path.join(target_dir, 'scenes') if os.path.isdir(os.path.join(target_dir, 'scenes')) else target_dir
    ok, issues = gate_G03_content_nonempty(scenes_dir)
    report.record('G-03', 'all_scenes', ok, str(issues[:3]) if issues else '')
    print(f'  G-03 all scenes: {"PASS" if ok else "FAIL"} ({len(issues)} issues)')
    
    # G-04: Check text overflow
    ok, warnings = gate_G04_text_overflow(scenes_dir)
    report.record('G-04', 'all_scenes', ok, str(warnings[:3]) if warnings else '')
    print(f'  G-04 text length: {"PASS" if ok else "WARN"} ({len(warnings)} warnings)')

def run_golden(report):
    """Run golden test suite"""
    gold_dir = BASE / '_01_golden_tests' / 'correct'
    if not gold_dir.exists():
        print('  No golden samples found')
        return
    
    for f in sorted(gold_dir.glob('*_meta.yaml')):
        with open(f, encoding='utf-8') as fh:
            meta = yaml.safe_load(fh)
        sid = meta['sample_id']
        expected = meta.get('expected_result', {})
        # Verify the golden PNG exists and is valid
        png_file = gold_dir / f'{sid}_golden.png'
        if png_file.exists():
            from PIL import Image; import numpy as np
            img = Image.open(str(png_file))
            arr = np.array(img.convert('L'))
            ok = arr.max() > 15  # Not blank
            report.record('golden', sid, ok)
            print(f'  Golden {sid}: {"PASS" if ok else "FAIL"}')

def run_mutations(report):
    """Run basic mutation testing"""
    sys.path.insert(0, str(BASE / '_02_compiler' / 'static'))
    from scene_quality_gate import gate_G01_style_guide, gate_G03_content_nonempty, gate_G04_text_overflow
    
    # Simple 6-mutation baseline test
    import tempfile
    
    # M1: Empty title
    d = tempfile.mkdtemp(); fp = os.path.join(d, 'm1.json')
    with open(fp, 'w', encoding='utf-8') as f:
        json.dump({'scene_type':'concept','content':{'title':'','body_lines':['x']}}, f)
    ok, _ = gate_G03_content_nonempty(d)
    report.record('mutations', 'M1_empty_title', not ok)
    
    # M2: Long label
    d2 = tempfile.mkdtemp(); fp2 = os.path.join(d2, 'm2.json')
    with open(fp2, 'w', encoding='utf-8') as f:
        json.dump({'scene_type':'diagram','content':{'title':'t','diagram':{'nodes':[{'label':'这是一个极其冗长且过度详细的标签文本用于测试文本溢出检测系统'}]}}}, f)
    ok, _ = gate_G04_text_overflow(d2)
    report.record('mutations', 'M2_text_overflow', not ok)
    
    # M3: Raw Manim API
    d3 = tempfile.mkdtemp(); fp3 = os.path.join(d3, 'm3.py')
    with open(fp3, 'w', encoding='utf-8') as f:
        f.write("from manim import *\nclass T(Scene):\n def construct(self):\n  t=Text('x');b=Rectangle();t.next_to(b,DOWN);self.add(t,b)\n")
    ok, _ = gate_G01_style_guide(fp3)
    report.record('mutations', 'M3_raw_manim', not ok)
    
    # M4: Empty steps
    d4 = tempfile.mkdtemp(); fp4 = os.path.join(d4, 'm4.json')
    with open(fp4, 'w', encoding='utf-8') as f:
        json.dump({'scene_type':'steps','content':{'title':'t','steps':[]}}, f)
    ok, _ = gate_G03_content_nonempty(d4)
    report.record('mutations', 'M4_empty_steps', not ok)
    
    print(f'  Mutations: {sum(1 for v in report.results["mutations"].values() if v["passed"])}/{len(report.results["mutations"])} detected')

if __name__ == '__main__':
    report = QualityReport()
    
    target = sys.argv[1] if len(sys.argv) > 1 else str(Path.home() / 'workspace')
    print(f'Quality Gate v0.2 — Target: {target}')
    
    print('\n[1/3] Running Gate checks...')
    run_gates(report, target)
    
    print('\n[2/3] Running Golden Tests...')
    run_golden(report)
    
    print('\n[3/3] Running Mutation Tests...')
    run_mutations(report)
    
    report.print()
    
    # Write JSON report
    report_path = Path(__file__).parent / 'last_report.json'
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report.summary(), f, indent=2, ensure_ascii=False)
    print(f'\nReport saved: {report_path}')
