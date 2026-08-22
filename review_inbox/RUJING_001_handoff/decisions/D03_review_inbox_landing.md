# Decision D03 — review_inbox 落地

> **Review ID**：`RUJING_001_handoff`
> **Decision ID**：`D03_review_inbox_landing`
> **决策方**：SPDT-004 主窗口

---

## 问题

> 跨窗口协作机制（review_inbox）是否需要现在落地？

## 拍板

- [x] ✅ 是（采纳建议：W24 内落地）

## 理由

- handoff 是"静态说明"，review_inbox 是"动态协作流"，两者互补
- W24 立项目标已包含此机制（路标 3-5）
- RUJING 窗口接手后立刻会有跨窗口协作需求（如新卡 ship 验证）

## 风险评估

- **采纳风险**：机制太重 → 协作变慢
- **缓解措施**：保持模板轻量（每模板 < 200 行）；不强制走 review（紧急情况可绕过）

## 下一步动作

- [x] `review_inbox/_templates/` 3 个模板（prompt/decision/feedback）
- [x] `review_inbox/RUJING_001_handoff/` 模拟样本（4 个决策）
- [x] `docs/REVIEW_INBOX.md` 机制说明（待写）

## 反馈给发起方

> review_inbox 机制已落地，可开始正式跨窗口协作。
