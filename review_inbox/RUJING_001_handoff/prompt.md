# RUJING_001_handoff · Review Prompt

> **Review ID**：`RUJING_001_handoff`
> **发起方**：RUJING 窗口（之前是 SPDT-004 主窗口的一部分）
> **接收方**：SPDT-004 主窗口
> **优先级**：P1
> **预计 SLA**：本轮响应

---

## 1. 上下文

W23 准出门完成后，willi 决定把 RUJING 项目（rujing APP + 内容推送链路）从 SPDT-004 主窗口交接出去，单独推进。本 review 是交接后的**第一次正式 review**，目的是让 SPDT-004 主窗口确认交接文档的完整性和可执行性。

## 2. 待审内容

- [x] `D:/2_products/education/SPDT-004_EduContent/handoff/rujing.md`（8765 字节，已 commit 8272bbe）
- [x] `D:/4_data/knowledge_cards/00-项目文档/MANIFEST.yaml`（闭环字段已填值）
- [x] git tag `v2.0-approved`（W23 准出门锁档）
- [x] 3 个 CI 工具（layer_lint / window_check / layer_doc_sync）已 run-through
- [x] accuracy_auditor 4 真产品 P0 样本全 GOLD

## 3. 关键问题

### 问题 1：交接文档是否完整覆盖接手人所需？

- **建议**：覆盖（handoff/rujing.md 含 11 节：当前状态/文件位置/3 工具/技术细节/待办/坑/能力/紧急/联系/版本）
- **理由**：之前 RUJING 推送踩过 6 个坑（DevEco 关闭/锁屏/IP 变/历史漏/sources 误报/重复推），文档都列了
- **风险**：接手人可能不读"已知坑"表，再次踩坑
- **如果拍板**：让 SPDT-004 接收；如需补——加 RUJING 窗口 review 列

### 问题 2：MANIFEST.yaml 闭环字段是否需要 SPDT-004 主窗口签字？

- **建议**：不需要（已 commit 8272bbe 即为签字）
- **理由**：MANIFEST.yaml 在 D:/4_data/ 仓库外，git 跟踪 SPDT-004 仓库，commit 视为签字
- **风险**：D:/4_data/ 仓库外文件易被误改
- **如果拍板**：保持现状，git 跟踪为唯一可信源

### 问题 3：跨窗口协作机制（review_inbox）是否需要现在落地？

- **建议**：现在落地（W24 路标 3-5）
- **理由**：handoff 是"静态说明"，review_inbox 是"动态协作流"，两者互补
- **风险**：机制太重会让跨窗口协作变慢
- **如果拍板**：W24 内建 `review_inbox/` 目录 + 模板 + 模拟样本

### 问题 4：RUJING 窗口接手后，SPDT-004 主窗口还需提供什么支持？

- **建议**：仅提供 4 个 CI 工具的 maintenance（已落到 tools/）+ accuracy_auditor 的迭代
- **理由**：CI 工具是治理层，跨窗口共享
- **风险**：工具变更影响两边
- **如果拍板**：工具变更走 review_inbox，SPDT-004 主窗口拍板

## 4. 完成信号

- 4 个问题全部写 `decisions/D*.md`
- 主窗口写 `feedback.md`
- 本目录标 `STATUS: completed`
- 文件可移 `archive/`

## 5. 不在本次 review 范围

- RUJING APP 端 UI/UX
- 5 学科扩展
- P-001 视频渲染
- v3.0 拍板
