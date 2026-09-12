"""
PT-030 toolkit 路径配置
========================
优先级: 环境变量 PT030_RAW_DIR > config.yaml > 默认值 D:\\4_data\\rujing_out\\真题主库\\
跨机兼容: 雪薇端机器路径不同时, 用环境变量覆盖

用法:
    >>> from pt030_toolkit.config import RAW_DIR, SPLIT_DIR, ZHENTI_DIR, CONFIG
    >>> print(RAW_DIR)
    D:\\4_data\\rujing_out\\真题主库\\raw
"""

import os
from pathlib import Path
from typing import Optional

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


# 默认路径 (宇兄端 D:\\)
DEFAULT_RAW_DIR = Path("D:/4_data/rujing_out/真题主库/raw")
DEFAULT_SPLIT_DIR = Path("D:/4_data/rujing_out/真题主库/split")
DEFAULT_ZHENTI_DIR = Path("D:/4_data/rujing_out/真题主库/zhenti")
DEFAULT_HANDBOOK_DIR = Path("D:/4_data/knowledge_cards")
DEFAULT_PT030_ROOT = Path("D:/2_products/education/PT-030_GaokaoPrep")


def _find_config_file() -> Optional[Path]:
    """查找 config.yaml, 优先级:
    1. 环境变量 PT030_CONFIG 指定的路径
    2. 当前目录 ./config.yaml
    3. ../config.yaml (从 pt030_toolkit 出发)
    4. ~/pt030_toolkit_config.yaml
    """
    env = os.environ.get("PT030_CONFIG")
    if env:
        p = Path(env)
        if p.exists():
            return p
    candidates = [
        Path("config.yaml"),
        Path(__file__).parent / "config.yaml",
        Path(__file__).parent.parent / "config.yaml",
        Path.home() / "pt030_toolkit_config.yaml",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def load_config() -> dict:
    """加载 config.yaml, 缺失时返回空 dict"""
    config_path = _find_config_file()
    if not config_path or not YAML_AVAILABLE:
        return {}
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        data["_config_path"] = str(config_path)
        return data
    except Exception as e:
        import sys
        print(f"警告: config.yaml 加载失败 ({e}), 使用默认值", file=sys.stderr)
        return {}


# 全局 CONFIG (懒加载, 启动时不读盘)
_CONFIG: Optional[dict] = None


def get_config() -> dict:
    global _CONFIG
    if _CONFIG is None:
        _CONFIG = load_config()
    return _CONFIG


def get_path(key: str, default: Path) -> Path:
    """优先级: 环境变量 PT030_<KEY> > config.yaml <key> > 默认值"""
    env_key = f"PT030_{key.upper()}"
    env_val = os.environ.get(env_key)
    if env_val:
        return Path(env_val)
    cfg = get_config()
    cfg_val = cfg.get(key)
    if cfg_val:
        return Path(cfg_val)
    return default


# 暴露的常用路径 (模块级, 雪薇端直接 import)
RAW_DIR = get_path("raw_dir", DEFAULT_RAW_DIR)
SPLIT_DIR = get_path("split_dir", DEFAULT_SPLIT_DIR)
ZHENTI_DIR = get_path("zhenti_dir", DEFAULT_ZHENTI_DIR)
HANDBOOK_DIR = get_path("handbook_dir", DEFAULT_HANDBOOK_DIR)
PT030_ROOT = get_path("pt030_root", DEFAULT_PT030_ROOT)


def ensure_dirs():
    """确保所有输出目录存在"""
    for d in [RAW_DIR, SPLIT_DIR, ZHENTI_DIR]:
        d.mkdir(parents=True, exist_ok=True)


def info() -> str:
    """打印当前路径配置 (debug 用)"""
    config_path = _find_config_file()
    lines = [
        "PT-030 toolkit path config:",
        f"  config file:        {config_path or '(未找到, 用默认值)'}",
        f"  RAW_DIR:            {RAW_DIR}",
        f"  SPLIT_DIR:          {SPLIT_DIR}",
        f"  ZHENTI_DIR:         {ZHENTI_DIR}",
        f"  HANDBOOK_DIR:       {HANDBOOK_DIR}",
        f"  PT030_ROOT:         {PT030_ROOT}",
        "",
        "环境变量覆盖:",
        "  PT030_RAW_DIR       (覆盖 raw/)",
        "  PT030_SPLIT_DIR     (覆盖 split/)",
        "  PT030_ZHENTI_DIR    (覆盖 zhenti/)",
        "  PT030_HANDBOOK_DIR  (覆盖 knowledge_cards/)",
        "  PT030_PT030_ROOT    (覆盖 PT-030 项目根)",
        "  PT030_CONFIG        (config.yaml 路径)",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    print(info())
