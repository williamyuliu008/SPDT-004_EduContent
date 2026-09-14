"""
5 学科母题异步批跑器 v1.0
=========================
按学科串行批跑 41 张母题, 失败重试, 进度落盘.

依赖: mother_problem_batch_gen.py 的 gen_one 函数 (子进程调用).

用法:
  # 后台启动全量批跑
  python mother_problem_async_batch.py start

  # 查进度
  python mother_problem_async_batch.py status

  # 停止
  python mother_problem_async_batch.py stop
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

# 进度文件
PROGRESS_FILE = Path(r"D:\2_products\education\SPDT-004_EduContent\tools\_mother_problem_progress.json")
LOG_DIR = Path(r"D:\2_products\education\SPDT-004_EduContent\tools\_mother_problem_logs")
PID_FILE = Path(r"D:\2_products\education\SPDT-004_EduContent\tools\_mother_problem.pid")
PYTHON = sys.executable

# 5 学科 41 张选题
SUBJECTS = {
    "语文": [
        "古诗意象-意境-情感鉴赏", "文言文断句", "文言实词词义推断",
        "议论文论据分析", "现代文阅读主旨大意", "现代文阅读细节理解",
        "病句修改", "成语辨析", "名句默写", "作文审题立意",
    ],
    "英语": [
        "阅读理解主旨大意", "阅读理解细节理解", "阅读理解词义猜测",
        "完形填空上下文推断", "语法填空时态", "语法填空非谓语",
        "应用文写作邀请信", "长难句五步切分", "短文改错", "七选五段落匹配",
    ],
    "地理": [
        "经纬定位", "等值线判读", "气候类型判断", "地理过程-流水地貌",
        "区域比较-南北方", "人地关系-城市化", "自然灾害-洪涝", "资源分布",
    ],
    "政治": [
        "主体分析法-国家企业个人", "矛盾分析-两点论重点论",
        "价值判断-核心价值观", "时政结合-十四五", "政治生活-政府职能",
        "经济生活-供给侧", "文化生活-文化自信", "哲学-认识论",
    ],
    "书法": [
        "五体辨识", "楷书结构-颜体欧体", "笔法-永字八法",
        "书法史-王羲之兰亭序", "临摹要点",
    ],
}


def load_progress() -> dict:
    if PROGRESS_FILE.exists():
        return json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
    return {"completed": {}, "failed": {}, "started_at": None, "last_update": None}


def save_progress(p: dict) -> None:
    p["last_update"] = time.strftime("%Y-%m-%d %H:%M:%S")
    PROGRESS_FILE.write_text(json.dumps(p, ensure_ascii=False, indent=2), encoding="utf-8")


def is_already_done(progress: dict, subject: str, theme: str) -> bool:
    """检查母题是否已存在"""
    subj_progress = progress.get("completed", {}).get(subject, [])
    return theme in subj_progress


def run_one(subject: str, theme: str, max_retry: int = 2) -> bool:
    """跑 1 张, 失败重试 max_retry 次"""
    log_path = LOG_DIR / f"{subject}_{int(time.time())}.log"
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    for attempt in range(max_retry + 1):
        try:
            cmd = [PYTHON, "tools/mother_problem_batch_gen.py",
                   "gen", "--subject", subject, "--theme", theme]
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=90,
                cwd=r"D:\2_products\education\SPDT-004_EduContent",
            )
            log_path.write_text(
                f"=== attempt {attempt+1} ===\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}\n",
                encoding="utf-8",
            )
            if result.returncode == 0 and "写入:" in result.stdout:
                return True
        except subprocess.TimeoutExpired:
            log_path.write_text(f"=== attempt {attempt+1} TIMEOUT ===\n", encoding="utf-8")
        time.sleep(2)
    return False


def start_batch() -> None:
    """串行跑全量"""
    progress = load_progress()
    progress["started_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    progress.setdefault("completed", {})
    progress.setdefault("failed", {})

    # 写 PID
    PID_FILE.write_text(str(os.getpid()), encoding="utf-8")

    total = sum(len(themes) for themes in SUBJECTS.values())
    done_count = sum(len(t) for t in progress["completed"].values())
    print(f"=== 5 学科母题批跑 (总 {total} 张, 已完成 {done_count} 张) ===")

    for subject, themes in SUBJECTS.items():
        print(f"\n--- {subject} ({len(themes)} 张) ---")
        for i, theme in enumerate(themes, 1):
            if is_already_done(progress, subject, theme):
                print(f"  [{i}/{len(themes)}] {theme} -> 已完成, 跳过")
                continue

            print(f"  [{i}/{len(themes)}] {theme} ... ", end="", flush=True)
            ok = run_one(subject, theme)
            if ok:
                progress["completed"].setdefault(subject, []).append(theme)
                print("OK")
            else:
                progress["failed"].setdefault(subject, []).append(theme)
                print("FAILED")
            save_progress(progress)
            time.sleep(1)

    print(f"\n=== 批跑完成 ===")
    print(f"  完成: {sum(len(t) for t in progress['completed'].values())} 张")
    print(f"  失败: {sum(len(t) for t in progress['failed'].values())} 张")
    if PID_FILE.exists():
        PID_FILE.unlink()


def status() -> None:
    """看进度"""
    if not PROGRESS_FILE.exists():
        print("尚未启动")
        return
    p = load_progress()
    print(f"启动: {p.get('started_at')}, 更新: {p.get('last_update')}")
    print()
    for subj in SUBJECTS:
        themes = SUBJECTS[subj]
        done = len(p.get("completed", {}).get(subj, []))
        failed = len(p.get("failed", {}).get(subj, []))
        pending = len(themes) - done - failed
        print(f"  {subj}: 完成 {done}/{len(themes)}, 失败 {failed}, 待办 {pending}")
        if failed > 0:
            for t in p.get("failed", {}).get(subj, []):
                print(f"    FAILED: {t}")


def stop() -> None:
    """停批跑"""
    if PID_FILE.exists():
        pid = int(PID_FILE.read_text(encoding="utf-8").strip())
        try:
            os.kill(pid, 9)  # SIGKILL
            print(f"已 stop PID {pid}")
        except ProcessLookupError:
            print(f"PID {pid} 不存在")
        PID_FILE.unlink()
    else:
        print("无 PID 文件, 批跑未启动")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "start":
        start_batch()
    elif cmd == "status":
        status()
    elif cmd == "stop":
        stop()
    else:
        print("用法: start | status | stop")
