# Decision D04 — SPDT-004 主窗口支持范围

> **Review ID**：`RUJING_001_handoff`
> **Decision ID**：`D04_maintenance_support`
> **决策方**：SPDT-004 主窗口

---

## 问题

> RUJING 窗口接手后，SPDT-004 主窗口还需提供什么支持？

## 拍板

- [x] ✅ 仅提供 4 个 CI 工具 maintenance + accuracy_auditor 迭代

## 理由

- CI 工具是治理层，跨窗口共享
- 内容生产是 RUJING 窗口自主范围
- 战略层（v3.0 拍板）由 SPDT-004 主窗口负责

## 风险评估

- **采纳风险**：工具变更影响两边（如 accuracy_auditor 加 P-001 规则）
- **缓解措施**：工具变更走 review_inbox，SPDT-004 主窗口拍板

## 下一步动作

- [x] 4 个 CI 工具（layer_lint / window_check / layer_doc_sync / accuracy_auditor）共享
- [x] 工具变更走 review_inbox/REVIEW_ID/decisions/
- [x] 内容生产工具（ru_cardpkg_convert / _push_to_rujing / _batch_convert_push）由 RUJING 窗口维护

## 反馈给发起方

> 工具共享已明确，变更请走 review_inbox。
