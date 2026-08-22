# review_inbox/ · L1_evolutionary · 跨窗口协作机制

> **Layer**: L1_evolutionary（默认 W_mid）
> **依据**: [LAYERS.md](../LAYERS.md) + [WINDOWS.md](../WINDOWS.md) + [docs/REVIEW_INBOX.md](../docs/REVIEW_INBOX.md)
> **状态**: W24 准出门时落地

---

## 定位

跨窗口协作的"动态 review 流"目录。区别于 [handoff/](../handoff/) 的"静态交接"。

## 子目录

| 子目录 | 用途 | 状态 |
|:---|:---|:---:|
| `_templates/` | 3 个模板（prompt/decision/feedback）| ✅ 稳定 |
| `archive/` | 已完成 review 归档 | ✅ 活跃 |
| `<REVIEW_ID>/` | 进行中的 review | ⏳ 动态 |

## 当前进行中

（暂无——上一轮 RUJING_001_handoff 已移到 archive/）

## 已完成归档

| Review ID | 状态 | 时间 |
|:---|:---|:---|
| RUJING_001_handoff | ✅ completed | W24 路标 5 |

## 协作方

- **SPDT-004 主窗口**：拍板方（决策/反馈）
- **RUJING 窗口**（已交接）：发起方（提交 prompt）

## 改动窗口

- 默认 **W_mid**（跨窗口协作）
- 紧急 P0 允许破窗（详见 WINDOWS.md §5.2）

## 引用

- 上层: [docs/REVIEW_INBOX.md](../docs/REVIEW_INBOX.md)（机制详细说明）
- 配套: [handoff/rujing.md](../handoff/rujing.md)（静态交接示例）
