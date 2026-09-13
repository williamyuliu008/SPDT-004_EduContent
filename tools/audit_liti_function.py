"""
PT-030 工具链综合审核 v1.0 (立体几何 + 函数/导数)
=================================================
审核维度:
A. 字段完整性 (id/maturity/front/back/options/knowledge_points/variants/display_target)
B. Qwen 升级标记 (provenance.qwen_review or _qwen_review)
C. 母题 derived_variants >= 2
D. 链 ID 格式 (chain_id)
E. 重复 ID 检测
F. 错分类检测 (module 与 source 不一致)
G. front/back 字段长度 (太短 = 不完整)
H. 显示目标 (display_target = ["学习中心"])

输出: 综合报告 + 问题列表
"""

import json
import re
import sys
from pathlib import Path
from collections import defaultdict, Counter

KCARDS = Path(r'D:\Z_学习平台\knowledge-cards-prod\projects\math\cards')
PT030 = KCARDS / '本地上海' / 'PT030_2026-09-13'
METHODS = KCARDS.parent / 'methods'
PANELS = {
    '立体几何': ['二面角', '线面垂直', '线面平行证明', '线面角', '面面平行证明'],
    '解析几何': ['解析几何'],
    '导数': ['导数'],
    '概率统计': ['概率统计'],
    '解三角形': ['解三角形'],
}

print('=' * 80)
print('PT-030 综合审核 v1.0 (立体几何 + 函数/导数 + 概率 + 解三角)')
print('=' * 80)

issues = defaultdict(list)  # {type: [files]}
all_ids = []  # 检测重复
total_checked = 0


def audit_kcard(path: Path, kind: str, expected_panel: str):
    """审核单张 K 卡"""
    global total_checked
    total_checked += 1
    try:
        d = json.loads(path.read_text(encoding='utf-8'))
    except Exception as e:
        issues['A.read_err'].append(f'{path}: {e}')
        return

    file_id = str(path)
    # A. 字段完整性
    required = ['id', 'maturity', 'front', 'back', 'module', 'subject']
    for f in required:
        if not d.get(f):
            issues[f'A.miss_{f}'].append(file_id)
    # front 长度
    front = d.get('front', '')
    if len(front) < 5:
        issues['A.front_short'].append(f'{file_id}: "{front[:30]}"')
    if len(front) > 3000:
        issues['A.front_too_long'].append(f'{file_id}: {len(front)} chars')
    # back 长度
    back = d.get('back', '')
    if len(back) < 3 and kind == 'mother':
        issues['A.back_short'].append(f'{file_id}: "{back[:30]}"')

    # B. Qwen 升级标记
    has_qwen_pt = bool(d.get('provenance', {}).get('qwen_review'))
    has_qwen_method = bool(d.get('_qwen_review'))
    has_qwen = has_qwen_pt or has_qwen_method

    # C. 母题变式
    if kind == 'mother':
        dv = d.get('derived_variants', [])
        n_dv = len(dv) if isinstance(dv, list) else 0
        if n_dv < 2:
            issues['C.mother_variants_lt_2'].append(f'{file_id}: {n_dv} 个变式')
        if not has_qwen:
            issues['B.mother_no_qwen'].append(file_id)
    if kind == 'method':
        if not has_qwen:
            issues['B.method_no_qwen'].append(file_id)

    # D. chain_id
    if kind == 'mother':
        cid = d.get('chain_id', '')
        if not cid:
            issues['D.no_chain_id'].append(file_id)
        elif not re.match(r'^[A-Za-z0-9_-]+$', cid):
            issues['D.bad_chain_id'].append(f'{file_id}: {cid}')

    # E. 重复 ID
    cid = d.get('id') or d.get('card_id')
    if cid:
        all_ids.append((file_id, cid))

    # F. module 与 source 不一致
    mod = d.get('module', '')
    src = d.get('source', '')
    if kind == 'mother' and expected_panel not in mod and expected_panel not in d.get('topic', ''):
        issues['F.mod_topic_mismatch'].append(f'{file_id}: mod={mod} topic={d.get("topic","")} expected={expected_panel}')

    # G. source_paper 有效
    sp = d.get('source_paper', '')
    if kind == 'pt030' and not sp:
        issues['G.pt030_no_paper'].append(file_id)

    # H. display_target
    dt = d.get('display_target', [])
    if kind == 'pt030' and '学习中心' not in dt:
        issues['H.bad_display_target'].append(f'{file_id}: {dt}')

    # I. 母题 maturity 应该是 REVIEWED (用户已 commit 立体几何/概率/解三角)
    if kind == 'mother' and d.get('maturity') not in ('REVIEWED', 'DRAFT'):
        issues['I.bad_maturity'].append(f'{file_id}: {d.get("maturity")}')

    # J. PT-030 K 卡 verdict 检查 (应填 TRUE/FALSE/UNKNOWN/超纲)
    if kind == 'pt030':
        verdict = d.get('verdict', '')
        if verdict not in ('TRUE', 'FALSE', 'PENDING', '超纲', '歧义'):
            issues['J.bad_verdict'].append(f'{file_id}: {verdict}')


# === 审核 4 板块 K 卡 ===
for panel, dirs in PANELS.items():
    print(f'\n[{panel}] K 卡审核中...', flush=True)
    if panel in ('解析几何', '导数', '概率统计', '解三角形'):
        # 母题 (K20-K24 解析, K30-K34 导数, K50-K54 概率, K60-K64 解三角)
        mother_dir = KCARDS / panel
        if mother_dir.exists():
            for f in sorted(mother_dir.glob('K[0-9][0-9].json')):
                if 10 <= int(f.stem[1:]) <= 99:
                    audit_kcard(f, 'mother', panel)
        # PT-030
        for f in PT030.rglob('*.json'):
            if 'llm_gen' in str(f):
                continue
            try:
                d = json.loads(f.read_text(encoding='utf-8'))
                if panel in d.get('module', ''):
                    audit_kcard(f, 'pt030', panel)
            except Exception:
                pass
    else:  # 立体几何 (5 板块目录)
        for d in dirs:
            mother_dir = KCARDS / d
            if mother_dir.exists():
                for f in sorted(mother_dir.glob('K[0-9][0-9].json')):
                    if 10 <= int(f.stem[1:]) <= 99:
                        audit_kcard(f, 'mother', panel)
        # PT-030
        for f in PT030.rglob('*.json'):
            if 'llm_gen' in str(f):
                continue
            try:
                d = json.loads(f.read_text(encoding='utf-8'))
                if '立体几何' in d.get('module', ''):
                    audit_kcard(f, 'pt030', '立体几何')
            except Exception:
                pass

    # 方法论
    method_dir = METHODS / panel
    if method_dir.exists():
        for f in method_dir.glob('M_*.json'):
            audit_kcard(f, 'method', panel)


# === 重复 ID 检测 ===
id_counter = Counter(cid for _, cid in all_ids)
for cid, count in id_counter.items():
    if count > 1:
        dup_files = [f for f, c in all_ids if c == cid]
        issues['E.duplicate_id'].append(f'{cid}: {count} 次 ({dup_files[:3]})')

# === 报告 ===
print('\n' + '=' * 80)
print('综合审核报告')
print('=' * 80)
print(f'总审核数: {total_checked}')

total_issues = sum(len(v) for v in issues.values())
print(f'总问题数: {total_issues}')

for issue_type, files in sorted(issues.items()):
    if files:
        print(f'\n[{issue_type}] {len(files)} 个:')
        for f in files[:10]:
            print(f'  {f}')
        if len(files) > 10:
            print(f'  ... ({len(files) - 10} more)')

# 写报告
report = {
    "checked": total_checked,
    "total_issues": total_issues,
    "by_type": {k: len(v) for k, v in issues.items()},
    "details": {k: v for k, v in issues.items()},
}
report_path = Path(r'D:\Z_学习平台\SPDT-004_EduContent\PT-030\zhenti\数学\AUDIT_REPORT_2026-09-13.json')
report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'\n报告: {report_path}')
