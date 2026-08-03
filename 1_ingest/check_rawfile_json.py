#!/usr/bin/env python3
"""
check_rawfile_json.py — App rawfile JSON 预检脚本
用途：App 集成前对 *_cards.json 进行 BOM + JSON 有效性 + 控制字符 检查
来源：地理山河系列 App 接入经验（2026-08-01）

用法：
    python check_rawfile_json.py <path_to_json>
    python check_rawfile_json.py                          # 默认检查 geo_cards.json
    python check_rawfile_json.py --all rawfile/           # 检查目录下所有 JSON
"""
import json, sys, os, glob, argparse

ERROR_COLOR = '\033[91m'
WARN_COLOR = '\033[93m'
OK_COLOR = '\033[92m'
RESET = '\033[0m'

def green(s): return f"{OK_COLOR}{s}{RESET}"
def red(s): return f"{ERROR_COLOR}{s}{RESET}"
def yellow(s): return f"{WARN_COLOR}{s}{RESET}"


def check_single(path: str) -> list[str]:
    """对单个 JSON 文件进行检查，返回错误列表（空=通过）。"""
    errors = []

    # 1. BOM 检测
    try:
        with open(path, 'rb') as f:
            first3 = f.read(3)
        if first3 == b'\xef\xbb\xbf':
            errors.append(f"BOM detected: UTF-8 BOM (\\xef\\xbb\\xbf) must be removed")
    except Exception as e:
        errors.append(f"Cannot read file: {e}")
        return errors

    # 2. JSON 有效性
    try:
        with open(path, 'r', encoding='utf-8') as f:
            raw = f.read()
        obj = json.loads(raw)
    except json.JSONDecodeError as e:
        errors.append(f"JSON parse error: {e}")
        return errors

    # 3. 控制字符检测（\r 在字符串内容内为非法）
    ctrl_chars = [(i, hex(ord(c))) for i, c in enumerate(raw)
                  if ord(c) < 32 and c not in '\n\t']
    if ctrl_chars:
        snippet = ', '.join(f"pos={p} {h}" for p, h in ctrl_chars[:3])
        errors.append(f"Control characters in file: {snippet}{' ...' if len(ctrl_chars) > 3 else ''}")

    # 4. 必需顶层字段检查（仅对字典类型有效）
    if not isinstance(obj, dict):
        errors.append(f"Root type is {type(obj).__name__}, expected dict — not a card package")
        return errors

    required = ['package_id', 'package_title', 'node_cards', 'total_cards', 'total_chains']
    missing = [f for f in required if f not in obj]
    if missing:
        errors.append(f"Missing required fields: {missing}")

    # 5. node_cards 格式抽查（前3张）
    cards = obj.get('node_cards', [])
    if not isinstance(cards, list):
        errors.append(f"'node_cards' is not a list: {type(cards)}")
    else:
        for i, card in enumerate(cards[:3]):
            for field in ['card_id', 'chain_id', 'chain_title', 'front', 'back_core']:
                if field not in card:
                    errors.append(f"Card[{i}] missing field: {field}")

    # 6. 卡数一致性
    declared_total = obj.get('total_cards', None)
    if declared_total is not None and len(cards) != declared_total:
        errors.append(f"Card count mismatch: node_cards has {len(cards)} but total_cards={declared_total}")

    return errors


def check_path(path: str) -> bool:
    """检查单个文件或目录，返回是否全部通过。"""
    all_ok = True
    if os.path.isdir(path):
        # 目录下所有 .json 文件
        patterns = [os.path.join(path, '*.json'), os.path.join(path, '**', '*.json')]
        json_files = []
        for p in patterns:
            json_files.extend(glob.glob(p, recursive=True))
        json_files = [f for f in set(json_files) if 'node_modules' not in f]
        print(f"Checking {len(json_files)} JSON files in {path}...")
        for f in sorted(json_files):
            ok = check_path(f)
            if not ok:
                all_ok = False
    else:
        rel = os.path.relpath(path, os.getcwd())
        errors = check_single(path)
        if errors:
            print(f"  {red('FAIL')} {rel}")
            for e in errors:
                print(f"        {e}")
            all_ok = False
        else:
            card_count = 0
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    obj = json.load(f)
                card_count = len(obj.get('node_cards', []))
            except Exception:
                pass
            print(f"  {green('OK')}   {rel} ({card_count} cards)")

    return all_ok


def main():
    parser = argparse.ArgumentParser(description='App rawfile JSON pre-flight checks')
    parser.add_argument('path', nargs='?', default=None,
                        help='Path to JSON file or directory (default: auto-detect)')
    parser.add_argument('--all', dest='all_mode', action='store_true',
                        help='Check all JSON files recursively')
    args = parser.parse_args()

    # 默认路径
    if args.path is None:
        candidates = [
            '../5_deliver/TextExperienceAPP/apps/rujing/entry/src/main/resources/rawfile/geo_cards.json',
            'entry/src/main/resources/rawfile/geo_cards.json',
            'geo_cards.json',
        ]
        for c in candidates:
            if os.path.exists(c):
                args.path = c
                break
        if args.path is None:
            print(yellow("No JSON file specified and none of the default paths exist."))
            print("Usage: python check_rawfile_json.py <path>")
            sys.exit(1)

    print(f"\n{'='*60}")
    print(f"  App rawfile JSON 预检")
    print(f"{'='*60}\n")

    ok = check_path(args.path)

    print(f"\n{'='*60}")
    if ok:
        print(f"  {green('ALL CHECKS PASSED')}")
    else:
        print(f"  {red('CHECKS FAILED — Fix errors before building')}")
    print(f"{'='*60}\n")

    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
