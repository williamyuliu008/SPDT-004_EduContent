# Hypium UI 自动化测试框架调研报告

> 鸿蒙特使 🏗️ | 2026-07-18 | SPDT-001 8月预研

---

## 1. 框架概述

**DevEco Testing Hypium** 是华为官方为 HarmonyOS 平台提供的 UI 自动化测试框架，基于 Python，支持通过 CLI 和 IDE 两种方式执行测试。核心能力：

- **三种控件定位**：原生控件、图像识别、比例坐标
- **多种模拟输入**：触摸屏、鼠标、键盘
- **多设备并行**：手机/平板/PC 同时执行
- **详细报告**：自动记录设备日志 + 操作截图

**两种使用模式**（可混合但非嵌套）：

| 模式 | 用途 | CLI 入口 |
|:---|:---|:---|
| **Driver 模式** | 作为 SDK 嵌入其他框架，直接控制设备 | `from hypium import UiDriver` |
| **测试工程模式** | 独立测试项目，JSON 配置 + Python 用例 | `python -m hypium run -l <用例>` |

---

## 2. 环境安装

```powershell
# 1. 确认 hdc 可用
& "C:\Users\willi\AppData\Local\OpenHarmony\Sdk\26.0.0\toolchains\hdc.exe" list targets

# 2. 安装 Hypium（依赖 xdevice，按实际版本号）
pip install xdevice-5.0.7.200.tar.gz
pip install hypium

# 3. 验证安装
python -m hypium.docs   # 查看 API 文档路径
```

**注意**：Hypium 需要设备连接（USB/WiFi），不支持纯离线执行。

---

## 3. CLI 集成评估

### 3.1 现有 CLI 入口

当前 `_check_hypium.ps1` 已封装基础调用：
```powershell
# 交互模式
python -m hypium

# 指定用例运行
python -m hypium run -l TC_001_video_play -ta screenshot:true
```

### 3.2 build-all.py 集成方案

Hypium **可直接从 `build-all.py` 调用**，三种集成深度：

**L1：最简集成（8月即可落地）**
```python
# build-all.py 新增 --smoke 参数
subprocess.run([
    "python", "-m", "hypium", "run",
    "-l", f"TC_{app_id}_smoke",
    "-ta", "screenshot:true"
], cwd=r"D:\92_products\SPDT-001_Harmony\automation")
```
调用路径：`build-all.py --deploy --smoke` → 编译 → 签名 → 部署 → Hypium 冒烟

**L2：CI 集成（按现有 cron 触发）**
```powershell
# ci-daily.ps1 新增加 pipeline 阶段
# PREFLIGHT → BUILD → SIGN → DEPLOY → HPIUM_SMOKE → REPORT
python -m hypium run -l TC_gaokao_smoke --report-dir ./reports/
```

**L3：Driver SDK 集成（高级，Python 脚本内嵌）**
```python
from hypium import UiDriver
driver = UiDriver.connect(device_sn="xxx")
driver.start_app("com.example.gaokao-agent")
# 执行自定义操作序列
assert driver.find_element({"id": "tab_home"}).exists()
driver.close()
```

### 3.3 已知限制

| 限制 | 影响 | 缓解措施 |
|:---|:---|:---|
| 需要连接真机 | CI 环境必须有设备 | 使用 USB Hub + 测试手机 |
| hdc 版本适配 | SDK 版本需匹配 | 锁定 `toolchains/26.0.0` |
| JSON 配置冗长 | 30 APP 需 30 套配置 | 模板化生成脚本 |
| 报告格式固定 | 不可自定义 | 后处理转换为 HTML |

---

## 4. SPDT-001 适配结论

| 评估维度 | 结论 |
|:---|:---|
| **CLI 可用性** | ✅ 完全支持 `python -m hypium run -l` |
| **build-all.py 集成** | ✅ `subprocess` 调用即可，无需额外适配 |
| **CI cron 集成** | ✅ 加入 ci-daily.ps1 pipeline |
| **多设备支持** | ✅ 可指定 `device_sn` |
| **报告输出** | ✅ 自动生成，路径可配置 |
| **学习成本** | 中（需掌握控件定位 + JSON 配置规范） |

**建议**：8月第1-2周完成 Hypium 环境搭建和 GaokaoAgent 3 个 APP 的试点用例；8月第3-4周扩展到 ThinkKit 5 款 APP；9月全量覆盖 30 APP。

> 📎 **参考来源**: [PyPI - hypium](https://pypi.org/project/hypium) | [华为官方 Hypium 指南](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/hypium-python-guidelines) | [CSDN 实战](https://blog.csdn.net/weixin_68781269/article/details/141029148) | [知乎 CLI 详解](https://zhuanlan.zhihu.com/p/1903447210529624925)
