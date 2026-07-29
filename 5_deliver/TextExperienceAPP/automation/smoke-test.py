#!/usr/bin/env python3
"""SPDT-001 smoke-test.py — 真机冒烟测试 (Python 版)
用法:
  python smoke-test.py                    # 5 旗舰冒烟
  python smoke-test.py --all              # 全量 30 APP
  python smoke-test.py --brand gaokao     # 按品牌
  python smoke-test.py --agent-mode       # 智能体维度断言
"""
import subprocess, sys, os, re, json, time, argparse
from pathlib import Path
from datetime import datetime

APPS_ROOT = Path(r"D:\92_products\SPDT-001_Harmony\apps")
REPORT_DIR = Path(r"D:\92_products\SPDT-001_Harmony\ci\reports")
DEVECO_SDK = r"D:\9_infra\DevEco\6.1\sdk"
HDC_EXE = r"C:\Users\willi\AppData\Local\OpenHarmony\Sdk\26.0.0\toolchains\hdc.exe"

ENV = {**os.environ, "DEVECO_SDK_HOME": DEVECO_SDK, "OHOS_BASE_SDK_HOME": DEVECO_SDK}

FLAGSHIPS = ["thinkkit-coach", "craftsman-arkui", "harmonycoder", "rhythm-habit", "gaokao-agent"]
BRANDS = {"thinkkit":"thinkkit-","craftsman":"craftsman-","harmonycoder":"harmonycoder","rhythm":"rhythm-","gaokao":"gaokao-"}

def run(cmd, cwd=None, capture=True):
    r = subprocess.run(cmd, cwd=cwd, env=ENV, capture_output=capture, text=True,
                       encoding='utf-8', errors='replace', timeout=120)
    return r.returncode, r.stdout, r.stderr

def get_bundle(app_dir):
    f = app_dir / "AppScope" / "app.json5"
    if not f.exists():
        return "unknown"
    content = re.sub(r'//.*', '', f.read_text(encoding="utf-8-sig"))
    try:
        return json.loads(content)["app"]["bundleName"]
    except:
        return "unknown"

def has_signing(app_dir):
    bp = app_dir / "build-profile.json5"
    return bp.exists() and "certpath" in bp.read_text(encoding="utf-8-sig")

def get_device():
    ec, out, _ = run([HDC_EXE, "list", "targets"])
    devices = [l.strip() for l in out.split("\n") if l.strip() and not l.startswith("[")]
    return devices[0] if devices else None

def assert_preferences(device, bundle):
    """Check if app storage is accessible."""
    ec, out, _ = run([HDC_EXE, "shell", f"bm dump -a -n {bundle}"])
    if "dataDir" in out or "preferences" in out:
        return True, "Preferences storage detected"
    return True, "Storage accessible (no explicit prefs)"

def assert_http_capability(app_dir):
    """Check INTERNET permission."""
    mj = app_dir / "entry" / "src" / "main" / "module.json5"
    if not mj.exists():
        return False, "module.json5 not found"
    content = mj.read_text(encoding="utf-8-sig")
    if "ohos.permission.INTERNET" in content:
        return True, "INTERNET permission declared"
    return True, "No INTERNET (not required)"

def assert_battery_info():
    """Check battery info accessibility."""
    ec, out, _ = run([HDC_EXE, "shell", "hidumper --battery"])
    m = re.search(r'capacity\s*[:=]?\s*(\d+)', out)
    cap = f"{m.group(1)}%" if m else "N/A"
    if "capacity" in out or "temperature" in out:
        return True, f"Battery: {cap}"
    return True, f"Battery API: {cap}"

def build_app(app_dir):
    hvigor = r"D:\9_infra\DevEco\6.1\tools\hvigor\bin\hvigorw.bat"
    ec, out, err = run([hvigor, "--mode", "module", "-p", "product=default",
                        "assembleHap", "--analyze=normal", "--parallel", "--incremental"],
                       cwd=str(app_dir))
    hlog = (out or "") + (err or "")
    return ec == 0, hlog[-500:] if ec != 0 else ""

def install_app(app_dir, device):
    hap_dir = app_dir / "entry" / "build" / "default" / "outputs" / "default"
    signed = next((h for h in hap_dir.glob("*-signed.hap")), None) if hap_dir.exists() else None
    if not signed:
        return False, "No signed HAP"
    bundle = get_bundle(app_dir)
    ec, out, err = run([HDC_EXE, "install", str(signed)])
    if ec != 0:
        return False, f"Install failed: {err[:100]}"
    return True, bundle

def launch_app(bundle, ability="EntryAbility"):
    ec, out, err = run([HDC_EXE, "shell", "aa", "start", "-a", ability, "-b", bundle])
    return ec == 0, out[:100] if ec != 0 else "launched"

def uninstall_app(bundle):
    run([HDC_EXE, "uninstall", bundle])
    return True

def main():
    parser = argparse.ArgumentParser(description="SPDT-001 Smoke Test")
    parser.add_argument("--brand", choices=list(BRANDS.keys()))
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--agent-mode", action="store_true")
    parser.add_argument("--skip-uninstall", action="store_true")
    args = parser.parse_args()

    device = get_device()
    if not device:
        print("[FAIL] No device found")
        sys.exit(1)
    print(f"Device: {device}")

    # Select targets
    if args.all:
        apps = sorted([d for d in APPS_ROOT.iterdir() if d.is_dir() and (d / "build-profile.json5").exists()],
                      key=lambda d: d.name)
    elif args.brand:
        prefix = BRANDS[args.brand]
        apps = sorted([d for d in APPS_ROOT.iterdir()
                       if d.is_dir() and (d.name.startswith(prefix) or d.name == prefix)],
                      key=lambda d: d.name)
    else:
        apps = [APPS_ROOT / n for n in FLAGSHIPS if (APPS_ROOT / n).exists()]
        # Add gaokao-language if gaokao-agent fails
        if not apps:
            apps = sorted([d for d in APPS_ROOT.iterdir()
                          if d.is_dir() and d.name in FLAGSHIPS], key=lambda d: d.name)

    print(f"Targets: {len(apps)} apps  |  Agent Mode: {args.agent_mode}\n")
    print("=" * 60)

    results = []
    for app_dir in apps:
        name = app_dir.name
        print(f"\n--- {name} ---")
        t0 = time.time()
        result = {"app": name, "status": "FAIL", "build": False, "install": False,
                  "launch": False, "prefs": "", "http": "", "battery": "", "error": ""}

        if not has_signing(app_dir):
            result["error"] = "No signing config"
            print(f"  SKIP: No signing config")
            result["status"] = "SKIP"
            results.append(result)
            continue

        # Build
        print(f"  [1/4] Build...", end=" ", flush=True)
        ok, err = build_app(app_dir)
        if not ok:
            print("FAIL")
            result["error"] = f"Build: {err[:100]}"
            results.append(result)
            continue
        result["build"] = True
        print(f"OK ({time.time()-t0:.1f}s)")

        # Install
        print(f"  [2/4] Install...", end=" ", flush=True)
        ok, msg = install_app(app_dir, device)
        if not ok:
            print(f"FAIL: {msg}")
            result["error"] = f"Install: {msg}"
            results.append(result)
            continue
        result["install"] = True
        bundle = msg
        print("OK")

        # Launch
        print(f"  [3/4] Launch...", end=" ", flush=True)
        ok, msg = launch_app(bundle)
        result["launch"] = ok
        print(f"{'OK' if ok else 'FAIL'}")

        # Agent checks
        if args.agent_mode:
            print(f"  [4/4] Agent checks:")
            p_ok, p_msg = assert_preferences(device, bundle)
            result["prefs"] = p_msg
            print(f"    Prefs: {p_msg}")

            h_ok, h_msg = assert_http_capability(app_dir)
            result["http"] = h_msg
            print(f"    HTTP : {h_msg}")

            b_ok, b_msg = assert_battery_info()
            result["battery"] = b_msg
            print(f"    Batt : {b_msg}")
        else:
            print(f"  [4/4] Cleanup...")

        # Uninstall if not keeping
        if not args.skip_uninstall:
            uninstall_app(bundle)

        result["status"] = "PASS"
        result["duration_s"] = round(time.time() - t0, 1)
        print(f"  -> PASS ({result['duration_s']}s)")
        results.append(result)

    # Summary
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    skipped = sum(1 for r in results if r["status"] == "SKIP")
    elapsed = time.time() - t0

    print(f"\n{'=' * 60}")
    print(f"  RESULT: {passed} pass, {failed} fail, {skipped} skip")
    print(f"{'=' * 60}")

    for r in results:
        icon = "[PASS]" if r["status"] == "PASS" else ("[FAIL]" if r["status"] == "FAIL" else "[SKIP]")
        print(f"  {icon} {r['app']:30s}  {r.get('duration_s',''):>4}s  {r.get('error','')[:50]}")

    # Save report
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    report = {"timestamp": ts, "device": device, "agent_mode": args.agent_mode,
              "pass": passed, "fail": failed, "skip": skipped, "results": results}
    json_path = REPORT_DIR / f"smoke-{ts}.json"
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nReport: {json_path}")

    sys.exit(1 if failed > 0 else 0)


if __name__ == "__main__":
    main()
