# -*- coding: utf-8 -*-
"""
_push_to_rujing.py — PC 端 → rujing APP 推送脚本 v6.0
- 用 urllib 直接 POST 192.168.43.1:18999/upload
- 不依赖 PC 8080 server（端到端直推）
- 接受文件路径参数

用法:
  python _push_to_rujing.py                          # 推送 D:/4_data/rujing_out/rujing_热力环流与风.json（默认）
  python _push_to_rujing.py D:/path/to/rujing_xxx.json   # 推送指定文件
  python _push_to_rujing.py /list                    # 列出可推送的文件
"""
import sys, io, os, glob, time, json, urllib.request, urllib.error
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ── 配置 ────────────────────────────────────────────
PHONE_IP = "192.168.43.1"   # 手机 wlan1 IP（PC 走这个连 18999）
RUJING_PORT = 18999
DEFAULT_FILES_DIR = r"D:\4_data\rujing_out"
UPLOAD_ENDPOINT = f"http://{PHONE_IP}:{RUJING_PORT}/upload"
TIMEOUT = 60  # 60s

def list_files() -> None:
    """列出 D:/4_data/rujing_out/rujing_*.json 可推送文件"""
    pattern = os.path.join(DEFAULT_FILES_DIR, "rujing_*.json")
    files = sorted(glob.glob(pattern))
    print(f"可推送文件 ({len(files)}):")
    for f in files:
        size = os.path.getsize(f)
        print(f"  {os.path.basename(f)}  ({size} bytes)")
    print(f"\n用法:")
    print(f"  python _push_to_rujing.py                       # 默认推最近 1 个")
    print(f"  python _push_to_rujing.py D:/path/to/file.json  # 推指定文件")
    print(f"  python _push_to_rujing.py /all                  # 推所有")

def push_file(path: str) -> int:
    """推送单个 rujing CardPackage JSON"""
    if not os.path.exists(path):
        print(f"❌ 文件不存在: {path}")
        return 1
    size = os.path.getsize(path)
    print(f"=== 推送 rujing CardPackage ===")
    print(f"文件: {path}  ({size} bytes)")
    print(f"目标: {UPLOAD_ENDPOINT}")

    with open(path, 'rb') as f:
        body = f.read()

    req = urllib.request.Request(
        UPLOAD_ENDPOINT,
        data=body,
        method='POST',
        headers={'Content-Type': 'application/json; charset=utf-8'}
    )

    try:
        t0 = time.time()
        r = urllib.request.urlopen(req, timeout=TIMEOUT)
        elapsed = time.time() - t0
        body_resp = r.read().decode('utf-8', errors='replace')
        print(f"\n✅ status: {r.getcode()}  (耗时 {elapsed:.2f}s)")
        print(f"response: {body_resp}")
        try:
            result = json.loads(body_resp)
            print(f"\n  cards: {result.get('cards', '?')}")
            print(f"  chains: {result.get('chains', '?')}")
        except Exception:
            pass
    except urllib.error.HTTPError as e:
        print(f"\n❌ HTTP {e.code}: {e.read().decode('utf-8', errors='replace')[:300]}")
        return 1
    except Exception as e:
        print(f"\n❌ FAIL: {e}")
        return 1

    # 看 import_result
    time.sleep(1)
    try:
        r = urllib.request.urlopen(f"http://{PHONE_IP}:{RUJING_PORT}/import_result", timeout=5)
        result = json.loads(r.read().decode())
        print(f"\nimport_result:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"\n⚠️ import_result 读不到: {e}")

    # 看 subjects
    try:
        r = urllib.request.urlopen(f"http://{PHONE_IP}:{RUJING_PORT}/subjects", timeout=5)
        subjects = json.loads(r.read().decode())
        print(f"\nsubjects:")
        print(json.dumps(subjects, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"\n⚠️ subjects 读不到: {e}")

    return 0

def push_all() -> int:
    """批量推送所有 rujing_*.json"""
    pattern = os.path.join(DEFAULT_FILES_DIR, "rujing_*.json")
    files = sorted(glob.glob(pattern))
    if not files:
        print("❌ 无可推送文件")
        return 1
    print(f"批量推送 {len(files)} 个文件...")
    for f in files:
        ret = push_file(f)
        if ret != 0:
            print(f"⚠️ 推送 {f} 失败，继续")
        time.sleep(2)
    return 0

def main():
    if len(sys.argv) < 2:
        # 默认推最近 1 个
        pattern = os.path.join(DEFAULT_FILES_DIR, "rujing_*.json")
        files = sorted(glob.glob(pattern), key=os.path.getmtime, reverse=True)
        if not files:
            print("❌ 无 rujing_*.json 文件")
            print(f"请先跑: python 08_tools/ru_cardpkg_convert.py --card-dir <套卡> --output {DEFAULT_FILES_DIR}/<名称>.json")
            return 1
        return push_file(files[0])

    arg = sys.argv[1]
    if arg == "/list":
        list_files()
        return 0
    if arg == "/all":
        return push_all()
    return push_file(arg)

if __name__ == "__main__":
    sys.exit(main())
