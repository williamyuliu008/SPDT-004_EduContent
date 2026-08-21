## PR 类型

- [ ] 🐛 Bug 修复
- [ ] ✨ 新功能
- [ ] ♻️ 重构
- [ ] 📝 文档
- [ ] 🧪 测试
- [ ] 🔧 工具 / 脚本
- [ ] 🎨 样式 / 格式

## 分层信息（必填）

**Layer**:
- [ ] L0_stable（受 W_low 保护，必须有 RFC）
- [ ] L1_evolutionary（W_mid/W_low 改）
- [ ] L2_experimental（W_high 改）

**Window**:
- [ ] W_low（稳定维护窗）
- [ ] W_mid（演化迭代窗）
- [ ] W_high（架构开发窗）

**变更类型**:
- [ ] 普通提交
- [ ] 破窗提交（需要说明原因）

## 关联信息

- **关联 RFC**（L0 必填）: <链接 or "无">
- **关联 Issue**: <#号 or "无">
- **关联 CHANGELOG 条目**: <行号 or "无">

## 变更说明

### 改了什么
<!-- 简要说明本次修改的内容 -->

### 为什么改
<!-- 描述动机 / 痛点 / 价值 -->

### 改动的文件
<!-- 列出主要文件 + 行号 -->

## 检查清单

### 必做
- [ ] `python tools/layer_lint.py` 跑过（无 error）
- [ ] `python tools/window_check.py` 跑过（无 mismatch）
- [ ] `python tools/layer_doc_sync.py` 跑过（无 error）
- [ ] 单元测试通过（如果是 L0）
- [ ] CHANGELOG 更新（如果是 L0/L1）

### 视情况
- [ ] 新增/更新 README
- [ ] 新增/更新 LAYERS.md（如新增 pdt）
- [ ] 新增/更新 ISOLATION.md（如修改 L2）
- [ ] 增量测试覆盖（如 L1）
- [ ] 文档同步（SPDT.yaml）
- [ ] 回滚方案（如 L0）

## 风险评估

- **影响范围**: <列出受影响的模块/路径>
- **回滚方案**: <如何回滚>
- **是否需要联调测试**: 是 / 否

## 截图/示例（如适用）

<!-- 贴上对比图、运行截图、示例输出 -->

---

## Reviewer Checklist

- [ ] Layer/Window 匹配
- [ ] 跨层依赖合规（通过 L0 公开 API）
- [ ] 测试覆盖达标
- [ ] 文档同步
- [ ] CHANGELOG 完整

**Reviewer**: @willi

**审批时间**: <预计 YYYY-MM-DD HH:MM>
