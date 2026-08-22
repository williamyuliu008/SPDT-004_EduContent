# Decision D02 — MANIFEST 闭环字段签字

> **Review ID**：`RUJING_001_handoff`
> **Decision ID**：`D02_manifest_signoff`
> **决策方**：SPDT-004 主窗口

---

## 问题

> MANIFEST.yaml 闭环字段是否需要 SPDT-004 主窗口单独签字？

## 拍板

- [x] ✅ 不需要（采纳建议：git commit 即签字）

## 理由

- MANIFEST.yaml 在 D:/4_data/ 仓库外，git 跟踪 SPDT-004 仓库
- commit 8272bbe（RUJING 交接）已包含 MANIFEST 闭环字段
- git 提交记录即为可审计的签字

## 风险评估

- **采纳风险**：D:/4_data/ 仓库外文件易被误改（不受 git 保护）
- **缓解措施**：MANIFEST.yaml 的修改必须在 commit 中提及（已在 .githooks/pre-commit 加提醒，W24 后续）

## 下一步动作

- [x] MANIFEST 闭环字段生效（v2.0-approved 锁档）
- [x] git 提交记录为可信源

## 反馈给发起方

> MANIFEST 修改请每次都同步到 git commit。
