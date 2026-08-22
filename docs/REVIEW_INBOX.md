# SPDT-004 跨窗口 review_inbox 协作机制 v1.0

> **版本**：v1.0（W24 准出门时落地）
> **目的**：定义跨窗口协作的"动态 review 流"——区别于 handoff/ 的"静态说明"
> **配套**：[handoff/rujing.md](../handoff/rujing.md)（静态交接示例）+ [LAYERS.md](../LAYERS.md) + [WINDOWS.md](../WINDOWS.md)

---

## 1. 设计动机

W23 准出门后，willi 决定把 RUJING 项目从 SPDT-004 主窗口交接出去。但**交接不等于脱钩**——跨窗口仍需协作：

| 场景 | 频率 | 内容 |
|:---|:---|:---|
| RUJING 窗口新卡 ship | 每日 | 需 SPDT-004 主窗口验证 |
| 工具变更（CI / accuracy_auditor）| 每周 | 跨窗口影响 |
| 战略层（v3.0 拍板）| 每月 | SPDT-004 主窗口拍板 |
| 紧急问题 | 不定 | 跨窗口 fast-track |

handoff/ 是"一次性静态交接文档"——无法承载**持续动态协作**。所以需要 review_inbox/ 机制。

---

## 2. 核心设计：3 个角色 + 3 个模板

### 2.1 角色

| 角色 | 责任 |
|:---|:---|
| **发起方**（提交 review）| 写 prompt.md，列出待审问题 |
| **接收方**（审核 review）| 写 decisions/D*.md，对每个问题拍板 |
| **归档**（review 完成）| feedback.md + 移到 archive/ |

### 2.2 模板

| 模板 | 路径 | 用途 |
|:---|:---|:---|
| **prompt.md** | `_templates/prompt.md.tpl` | 发起方填：基本信息 + 上下文 + 待审内容 + 关键问题 |
| **decision.md** | `_templates/decision.md.tpl` | 接收方填：拍板 + 理由 + 风险 + 下一步 |
| **feedback.md** | `_templates/feedback.md.tpl` | 接收方合并：决策汇总 + 承诺 + 经验教训 |

---

## 3. 目录结构

```
review_inbox/
├── README.md                       ← 本文件
├── _templates/                     ← 模板（不修改）
│   ├── prompt.md.tpl
│   ├── decision.md.tpl
│   └── feedback.md.tpl
├── archive/                        ← 已完成 review 归档
│   └── RUJING_001_handoff/         ← 完成的样本
│       ├── prompt.md
│       ├── decisions/D01..D04
│       └── feedback.md
└── <REVIEW_ID>/                    ← 进行中的 review
    ├── prompt.md                   ← 发起方填
    ├── decisions/                  ← 接收方填
    │   ├── D01_<topic>.md
    │   ├── D02_<topic>.md
    │   └── ...
    └── feedback.md                 ← 完成时合并
```

---

## 4. 工作流（4 步）

```
Step 1 · 发起方写 prompt.md
  ↓ （提交到 review_inbox/<REVIEW_ID>/prompt.md）
Step 2 · 接收方看 prompt.md
  ↓ （理解问题）
Step 3 · 接收方写 decisions/D*.md
  ↓ （每个问题 1 个 decision）
Step 4 · 接收方写 feedback.md + 移到 archive/
  ↓ （review 完成）
```

### 时序示例

```
T0:  RUJING 窗口写 RUJING_002_xxx/prompt.md
T1:  SPDT-004 主窗口看 prompt.md
T2:  SPDT-004 主窗口写 RUJING_002_xxx/decisions/D01..D03
T3:  SPDT-004 主窗口写 RUJING_002_xxx/feedback.md
T4:  RUJING 窗口看 feedback.md 行动
T5:  RUJING 窗口 mv 到 archive/
```

---

## 5. 关键规则

### 5.1 决策必带"建议+理由+风险"

**不允许"3 选 1 形式"**。发起方在 prompt.md 中每个问题都要给：
- **建议**：我的推荐
- **理由**：为什么
- **风险**：最坏情况
- **如果拍板**：下一步动作

接收方在 decision.md 中要么采纳、要么调整、要么不采纳——但**必须说明理由**。

### 5.2 紧急情况允许破窗

紧急情况可绕过 review_inbox：
- P0 生产故障
- 安全漏洞
- 关键路径测试失败

破窗后必须：
1. 当天补 review 文档
2. 当周内做 post-mortem
3. 视情况加 review 规则防止再次发生

### 5.3 review_inbox vs handoff/

| 维度 | handoff/ | review_inbox/ |
|:---|:---|:---|
| 形态 | 静态文档 | 动态协作 |
| 时机 | 一次性交接 | 持续协作 |
| 产出 | 1 份 README.md | 1 个 review 目录（多文件）|
| SLA | 一次性读 | 约定响应时长 |
| 完成信号 | 文档写完 | 移到 archive/ |

### 5.4 review 优先级

| 优先级 | SLA | 场景 |
|:---|:---|:---|
| P0 | 当小时 | 生产故障 / 安全漏洞 |
| P1 | 当天 | 关键里程碑 / 跨窗口阻塞 |
| P2 | 1 周 | 日常运营 / 工具变更 |
| P3 | 1 月 | 战略层 / 长期规划 |

---

## 6. 已完成样本

### RUJING_001_handoff（W24 路标 5 模拟）

- 4 个决策全部"是"（handoff 准备充分）
- 详见 `archive/RUJING_001_handoff/`
- 关键经验：
  - 轻量模板生效（每个决策 < 200 行）
  - git commit 作为签字简化流程
  - 模板 3 件套（prompt/decision/feedback）够用

---

## 7. 未来扩展

### 7.1 自动化（如果需要）

- `_tools/review_lint.py` 验证 prompt.md 必填字段
- `_tools/review_status.py` 列出所有进行中 review + SLA 状态
- `_tools/review_archive.py` 自动归档 30 天未更新的 review

### 7.2 跨仓库支持（如果需要）

- review_inbox 复制到 RUJING 仓库（不是 SPDT-004 独有）
- 跨仓库 review 通过 GitHub PR 实现

---

## 8. 文件索引

```
docs/REVIEW_INBOX.md                    ← 本文件
review_inbox/_templates/                ← 3 个模板
review_inbox/archive/                   ← 已完成归档
review_inbox/README.md                  ← review_inbox 目录索引（待写）
handoff/rujing.md                       ← 静态交接文档（示例）
LAYERS.md                               ← 分层定义
WINDOWS.md                              ← 窗口节奏
```

---

## 9. 版本历史

| 版本 | 变更 |
|:---|:---|
| v1.0 | 首发：3 模板 + 工作流 + 6 规则 + 样本 + 未来扩展 |
