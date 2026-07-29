# 鸿蒙自动化调试助手 — 概念设计

> 鸿蒙特使 🏗️ | 2026-07-18 | SPDT-001 自研调试工具 | v0.1-concept

---

## 0. 设计原则

1. **CLI-first**：所有功能可通过命令行调用，无缝集成到 `build-all.py` / `ci-daily.ps1`
2. **hdc-native**：底层依赖 `hdc`（已集成在 SDK 26.0.0），避免引入额外运行时
3. **Python 单文件**：核心工具为单个 `.py`，依赖仅限 Python 标准库 + Pillow（截图对比）
4. **HTML 报告**：每次运行输出一个自包含 HTML，可直接浏览器打开、存档、对比历史

---

## 1. 架构总览

```
┌──────────────────────────────────────────────────────────┐
│              harmony-debug-tool.py  (CLI entry)           │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐  │
│  │ 日志采集  │  │ 崩溃分析  │  │ UI 对比  │  │ 批量  │  │
│  │ collect  │  │  crash   │  │  diff    │  │ batch  │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └───┬────┘  │
│       │             │             │            │        │
│  hdc hilog      hdc shell       hdc shell     build-all │
│  -T domain      hilog -e        screenshot     .py      │
│       │             │             │            │        │
│       └─────────────┴─────────────┴────────────┘        │
│                          │                               │
│                    ┌─────▼──────┐                        │
│                    │ HTML 报告  │                        │
│                    │ 生成引擎   │                        │
│                    └────────────┘                        │
└──────────────────────────────────────────────────────────┘
```

---

## 2. 功能模块详解

### 2.1 日志采集 (`collect`)

**目标**：一键抓取指定 APP 的运行日志，按时间段/关键字过滤。

```powershell
# 用法示例
python harmony-debug-tool.py collect --app gaokao-agent --duration 30s --filter "ERROR|FATAL"
python harmony-debug-tool.py collect --app thinkkit-coach --since 14:00:00
python harmony-debug-tool.py collect --all-apps --output ./logs/2026-07-18/
```

**实现路径**：
```
hdc shell hilog -T <domain>          → 按 APP 域过滤
hdc shell hilog -t <type>            → 按日志类型（ERROR/WARN/INFO）
hdc shell hilog --since <timestamp>  → 时间窗口
```

**输出**：结构化 JSON 日志文件 + HTML 报告中可搜索的日志表格。

### 2.2 崩溃分析 (`crash`)

**目标**：自动捕获 APP 崩溃堆栈，解析为可读报告。

```powershell
# 用法示例
python harmony-debug-tool.py crash --app gaokao-agent --watch
python harmony-debug-tool.py crash --dump-last
python harmony-debug-tool.py crash --app thinkkit-coach --output crash-report.html
```

**实现路径**：
```
1. hdc shell hilog -e                            → 实时监控错误日志
2. 正则匹配 "FATAL EXCEPTION" / "Process:"        → 识别崩溃事件
3. 提取堆栈帧 → 解析源文件:行号                     → 定位崩溃点
4. 匹配已知错误模式库 (errors-patterns.json)       → 自动诊断建议
```

**已知错误模式库示例**：
```json
{
  "arkts-no-obj-literals-as-types": {
    "pattern": "Object literal must correspond to some explicitly declared class or interface",
    "cause": "DevEco 6.1 新增严格模式",
    "fix": "为对象字面量定义 interface 类型"
  },
  "arkts-no-spread": {
    "pattern": "Spread operator is not supported",
    "cause": "ArkTS 限制",
    "fix": "改用 Object.assign 或手动属性复制"
  }
}
```

### 2.3 UI 截图对比 (`diff`)

**目标**：截取 APP 界面并与基线截图做像素级对比，检测 UI 回归。

```powershell
# 用法示例
python harmony-debug-tool.py diff --app gaokao-agent --screen home
python harmony-debug-tool.py diff --app gaokao-agent --all-screens --baseline v1.0
python harmony-debug-tool.py diff --app thinkkit-coach --threshold 0.05  # 5% 差异容忍度
```

**实现路径**：
```
1. hdc shell snapshot_display -f /data/local/tmp/screen.jpeg
2. hdc file recv /data/local/tmp/screen.jpeg ./screenshots/<app>_<screen>_<timestamp>.jpeg
3. Pillow ImageChops.difference(baseline, current)
4. 计算差异像素百分比 + 生成高亮差异图
5. 超过阈值 → 标记为 UI 回归
```

**基线管理**：
```
automation/baselines/
├── gaokao-agent/
│   ├── home_v1.0.jpeg
│   ├── practice_v1.0.jpeg
│   └── search_v1.0.jpeg
├── thinkkit-coach/
│   └── ...
└── diff_history.json     ← 记录每次对比结果
```

### 2.4 批量验证 (`batch`)

**目标**：对 30 个 APP 执行相同的验证流程，输出汇总结果。

```powershell
# 用法示例
python harmony-debug-tool.py batch --all-apps --verify install,launch,screenshot
python harmony-debug-tool.py batch --brand gaokao --verify install,launch,crash-watch:10s
python harmony-debug-tool.py batch --apps gaokao-agent,thinkkit-coach,thinkkit-flashcard
```

**验证流程**：
```
for each APP:
  1. hdc install <app.hap>           → 安装验证
  2. hdc shell aa start -a <ability> → 启动验证（等待 5s）
  3. hdc shell snapshot_display      → 截图验证
  4. 可选：hdc shell hilog -T <app>  → 日志扫描（5s 窗口查找 ERROR）
  5. 记录：PASS / FAIL + 失败原因    → 汇总表
```

### 2.5 回归测试 (`regression`)

**目标**：版本对比——新版本 vs 上一个已知良好版本。

```powershell
# 用法示例
python harmony-debug-tool.py regression --app gaokao-agent --version current --baseline v1.0.0
python harmony-debug-tool.py regression --all-apps --baseline-tag v1.0-stable
```

**对比维度**：
| 维度 | 方法 | 阈值 |
|:---|:---|:---|
| 编译结果 | HAP 大小对比 | ±10% |
| 启动时间 | hdc shell aa start 耗时 | +20% |
| 安装成功率 | hdc install 返回码 | 必须 100% |
| UI 一致性 | screenshot diff | 差异 <5% |
| 崩溃率 | 10s 窗口 hilog ERROR | 0 ERROR |

### 2.6 HTML 报告生成

每次 `batch` / `regression` / `crash` 执行自动生成自包含 HTML：

```
reports/
├── 2026-07-18_1430_batch-gaokao.html
├── 2026-07-18_1500_regression-thinkkit.html
└── 2026-07-18_1600_crash-gaokao-agent.html
```

**报告内容**：
- 执行摘要（PASS/FAIL 计数、通过率、耗时）
- 逐 APP 详情（可折叠）：编译日志、安装结果、截图（含差异高亮）、崩溃堆栈
- 趋势图（reports/ 历史数据聚合）：通过率曲线、常见失败模式
- 一键复制到剪贴板的错误摘要

---

## 3. CLI 接口设计

```
harmony-debug-tool.py <command> [options]

Commands:
  collect     日志采集
  crash       崩溃监控与分析
  diff        UI 截图对比
  batch       批量 APP 验证
  regression  版本回归测试
  report      仅生成报告（基于已有日志/截图）

Common options:
  --app APP_ID           目标 APP ID
  --brand BRAND          品牌（gaokao/thinkkit/craftsman/harmonycoder/rhythm）
  --all-apps             全部 30 APP
  --output DIR           输出目录（默认: ./reports/）
  --device SN            指定设备序列号（默认: hdc list targets 第一个）
  --hdc PATH             hdc 路径（默认: SDK 26.0.0 toolchains/hdc.exe）
  --verbose              详细输出
```

---

## 4. 与现有工具链的关系

```
                    build-all.py
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
     编译+签名        部署          冒烟验证
     (hvigorw)    (hdc install)   (smoke-test.py)
                                       │
                          ┌────────────┴────────────┐
                          ▼                         ▼
                   harmony-debug-tool.py      Hypium (华为官方)
                   (本工具 - 自研)             (python -m hypium)
                   ├─ 日志/崩溃                 ├─ UI 控件测试
                   ├─ 截图对比                   ├─ 手势模拟
                   ├─ 批量验证                   └─ 多设备并行
                   └─ HTML 报告
```

**定位**：hypium 做**精细化的 UI 交互测试**（点击/滑动/断言），harmony-debug-tool 做**质量基础设施**（日志/崩溃/截图/批量/回归），两者互补。

---

## 5. 实施计划

| 阶段 | 范围 | 预计工时 | 产出 |
|:---|:---|:---|:---|
| **POC（8月第3周）** | `collect` + `batch` 基础功能 | 3天 | 可用的单文件 py |
| **Alpha（8月第4周）** | `crash` + `diff` + HTML 报告 | 3天 | GaokaoAgent 3 APP 试点 |
| **Beta（9月第1周）** | `regression` + 错误模式库 | 2天 | 全品牌覆盖 |
| **GA（9月第2周）** | 集成 `ci-daily.ps1` | 1天 | CI 每日自动运行 |

**代码规模预估**：单文件 ~800-1200 行 Python，依赖 `Pillow`（截图对比）。

---

## 6. 风险与缓解

| 风险 | 缓解 |
|:---|:---|
| hdc 命令在不同 HarmonyOS 版本行为差异 | 抽象 `HdcWrapper` 层，命令参数可配置 |
| 真机截图权限（部分设备需要授权） | 首次运行检测并提示用户手动授权 |
| 30 APP 批量截图耗时较长 | 支持 `--parallel N` 并发执行 |
| 错误模式库覆盖不足 | 每次崩溃自动记录新模式到 `errors-patterns.json` |

---

> 🏗️ 鸿蒙特使 · SPDT-001 | 自研调试工具概念设计 v0.1 | 待审批后进入 POC 阶段
