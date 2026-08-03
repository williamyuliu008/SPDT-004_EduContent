"""
_upgrade_interface.py — P0 接口标准化脚本
升级所有 *_cards.json 到 interface_version=3.0，字段统一
变更：
  1. 统一 package_id / package_title（兼容 pack_id / pack_title）
  2. card_type 大小写标准化（NODE→node, STRATEGY→strategy）
  3. 删除非标准顶层字段（generated_at）
  4. 删除卡级运行时字段（last_reviewed, created_at, updated_at）
  5. 添加 interface_version 和 kb_source
"""
import json, os, sys
from datetime import datetime, timezone

OUT_DIR = r'D:/2_products/education/SPDT-004_EduContent/5_deliver/TextExperienceAPP/apps/rujing/entry/src/main/resources/rawfile'
NOW = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S+08:00')

CARD_TYPE_MAP = {
    'NODE': 'node',
    'STRATEGY': 'strategy',
    'CHAIN': 'chain',
}

KB_SOURCE_DEFAULT = {
    'pack_id': None,       # 由各包自行填充
    'kb_version': '1.0.0',
    'generated_at': NOW,
    'generator': '_upgrade_interface.py v1.0',
}


def fix_card(card: dict) -> dict:
    """修复单个卡片字段。"""
    # card_type 大小写标准化
    ct = card.get('card_type', 'node')
    card['card_type'] = CARD_TYPE_MAP.get(ct, ct.lower() if isinstance(ct, str) else 'node')

    # 删除运行时字段（App 会在导入时重新生成）
    for f in ('last_reviewed', 'created_at', 'updated_at'):
        card.pop(f, None)

    # 确保必需字段
    card.setdefault('chain_role', 'pivot')
    card.setdefault('tags', [])

    return card


def fix_package(obj: dict, pack_id: str, kb_version: str = '1.0.0') -> dict:
    """标准化包顶层字段。"""
    # 统一 package_id / package_title
    if 'package_id' not in obj and 'pack_id' in obj:
        obj['package_id'] = obj.pop('pack_id')
    if 'package_title' not in obj and 'pack_title' in obj:
        obj['package_title'] = obj.pop('pack_title')

    # 删除非标准顶层字段
    for f in ('generated_at',):
        obj.pop(f, None)

    # 添加 interface_version（已有则保留）
    obj.setdefault('interface_version', '3.0')

    # 添加 kb_source
    obj['kb_source'] = {
        'pack_id': obj.get('package_id', pack_id),
        'kb_version': kb_version,
        'generated_at': NOW,
        'generator': '_upgrade_interface.py v1.0',
    }

    # 修复所有卡片
    if 'node_cards' in obj:
        obj['node_cards'] = [fix_card(c) for c in obj['node_cards']]
    if 'strategy_cards' in obj:
        obj['strategy_cards'] = [fix_card(c) for c in obj['strategy_cards']]
    if 'chain_cards' in obj:
        obj['chain_cards'] = [fix_card(c) for c in obj['chain_cards']]
    # 兼容 v1/v2 扁平格式
    if 'cards' in obj:
        obj['cards'] = [fix_card(c) for c in obj['cards']]

    return obj


def process_file(path: str, pack_id: str, kb_version: str = '1.0.0') -> bool:
    """处理单个文件，返回是否成功。"""
    with open(path, 'r', encoding='utf-8') as f:
        raw = f.read()
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f'  [FAIL] {os.path.basename(path)}: JSON parse error: {e}')
        return False

    obj = fix_package(obj, pack_id, kb_version)

    # 重新序列化
    json_str = json.dumps(obj, ensure_ascii=False, indent=2)

    # 验证
    try:
        json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f'  [FAIL] {os.path.basename(path)}: Re-serialization error: {e}')
        return False

    with open(path, 'w', encoding='utf-8') as f:
        f.write(json_str)

    total = len(obj.get('node_cards', [])) + len(obj.get('strategy_cards', [])) + len(obj.get('chain_cards', [])) + len(obj.get('cards', []))
    print(f"  [OK] {os.path.basename(path)}: interface_version={obj.get('interface_version')}, "
          f"package_id={obj.get('package_id')}, cards={total}")
    return True


def main():
    files = [
        (os.path.join(OUT_DIR, 'geo_cards.json'), 'geo_shanhe_2026', '1.0.0'),
        (os.path.join(OUT_DIR, 'mogustory_cards.json'), 'mogu_calligraphy_series', '1.0.0'),
        (os.path.join(OUT_DIR, 'cafa_cards.json'), 'cafa_calligraphy_2026', '1.0.0'),
    ]

    print(f'OUT_DIR: {OUT_DIR}')
    print(f'P0 Interface Standardization — interface_version=3.0')
    print('=' * 60)

    all_ok = True
    for path, pack_id, kb_ver in files:
        if not os.path.exists(path):
            print(f'  [SKIP] {os.path.basename(path)}: not found')
            continue
        ok = process_file(path, pack_id, kb_ver)
        if not ok:
            all_ok = False

    print('=' * 60)
    print('Done.' if all_ok else 'Some files failed.')
    return 0 if all_ok else 1


if __name__ == '__main__':
    sys.exit(main())
