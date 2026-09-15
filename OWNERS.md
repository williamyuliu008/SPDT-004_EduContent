# SPDT-004 所有权矩阵 (OWNERS.md)

> **版本**: v1.0 (本轮)
> **模式**: 宇兄端主导开发，雪薇端主导知识/真题，手机端集成
> **更新**: 每次分工调整时更新

---

## 1. 总览

| 角色 | 主体 | 工作模式 | 接入 |
|:---|:---|:---|:---|
| 宇兄端 (本机) | mavis (Mavis) | 开发助手 / 工具 / 算法 / rujing demo | git push 直接 |
| 雪薇端 | 另一台机器 AI | 学生视角 / 知识卡片 / 真题挖掘 | `handoff/` + git PR |
| 手机端 | 鸿蒙开发 | HarmonyOS APP 集成 | 第三方仓库 |

---

## 2. 目录所有权

| 目录 | 主负责 | 协负责 | git 状态 | 说明 |
|:---|:---|:---|:---|:---|
| **`PROJECT.md` / `OWNERS.md` / `STATUS.md`** | 宇兄 | - | ✅ | 项目顶层元数据 |
| **`AGENTS.md`** | 宇兄 | - | ✅ | 数据迁移规范 (D:\4_data 路径) |
| `tools/` | 宇兄 | 雪薇可调用 | ✅ | 12+ 脚本 (validator / batch_gen / path_finder) |
| `knowledge_graphs/` | 宇兄 | - | ✅ | KG JSON (math + multi_subject) |
| `products/math_4step_mvp/` | 宇兄 | - | ✅ | rujing Flask Web demo |
| `handoff/` | 宇兄 + 雪薇 | - | ✅ | 双窗口协作契约 |
| `docs/` | 宇兄 | - | ✅ | 设计文档 |
| `prompts/` | 宇兄 | 雪薇可调用 | ✅ | LLM 提示词 |
| `quality/` | 宇兄 | 雪薇可调用 | ✅ | 质检工具 |
| `templates/` | 宇兄 | - | ✅ | HTML/PDF 模板 |
| `common/` | 宇兄 | - | ✅ | 公共代码 |
| `1_ingest/` | 雪薇 | - | ❌ | PT-030 原始数据采集 |
| `2_structure/TextExperience/` (submodule) | 宇兄 | - | ❌ (submodule) | 剧本化脚本 |
| `3_render/` | 宇兄 | - | ❌ | CGM 多媒体渲染管线 |
| `4_adapt/AdaptivePrepPlatform/` | **独立 SPDT-021 项目** | - | ❌ | 5 Agent + CGM 融合方法论 |
| `5_deliver/TextExperienceAPP/` | **手机端** | - | ❌ | HarmonyOS APP |
| `PT-030/` | 雪薇 | 宇兄工具 | ❌ (子目录) | 真题挖掘 handoff 工具 |
| `review_inbox/` | 雪薇 | 宇兄 | ❌ | 审查入站 |

---

## 3. git 仓库边界

| 仓库 | 位置 | 状态 |
|:---|:---|:---|
| **SPDT-004 主仓** | `D:\2_products\education\SPDT-004_EduContent` | `williamyuliu008/SPDT-004_EduContent` |
| **`2_structure/TextExperience`** | submodule | 共享剧本 |
| **`4_adapt/AdaptivePrepPlatform`** | 子目录 | **SPDT-021 独立项目** (应分开) |
| **`5_deliver/TextExperienceAPP`** | 子目录 | **手机端独立仓库** (应分开) |
| **`PT-030/`** | 子目录 | **雪薇端独立仓库** (应分开) |

---

## 4. 数据归属

| 数据位置 | 主负责 | git | 说明 |
|:---|:---|:---|:---|
| `D:\4_data\knowledge_cards\<学科>\<4step>` | 雪薇 | ❌ | 76 张母题 + 37 张策略 + 20 张元学习 |
| `D:\4_data\knowledge_cards\策略\<学科>` | 宇兄 | ❌ | 6 学科策略卡 JSON |
| `D:\4_data\knowledge_cards\元学习` | 雪薇 | ❌ | 20 张元学习 (8 旧 + 12 新) |
| `D:\4_data\rujing_out\真题主库` | 雪薇 | ❌ | PT-030 真题 (5407 题) |
| `D:\4_data\work\media\renders` | 宇兄 | ❌ | CGM 视频/音频 (55 张 mp4 + 55 mp3) |

---

## 5. 双窗口交接契约

### 宇兄 → 雪薇
- 路径: `handoff/P0-X_<topic>_v1.0_<to雪薇>.md`
- 触发: 工具/数据/规范变化时
- 内容: 角色/上下文/任务/验收/输出格式

### 雪薇 → 宇兄
- 路径: `review_inbox/P0-X_<topic>_雪薇反馈_YYYY-MM-DD.md`
- 触发: 验收完成 / 工具 bug / 缺数据
- 内容: 路由测试结果 + 数据缺失 + 改进建议

### 宇兄 → 手机端
- 路径: `handoff/P0-D_rujing_手机端集成_v1.0.md`
- 内容: Web demo URL + API 路由 + 集成步骤

---

## 6. 联系方式 (人工)
- 宇兄端: 本机 Claude Code
- 雪薇端: 另一台机器 AI
- 手机端: 鸿蒙开发 (独立仓库)

**冲突解决**: 用户 (willi) 拍板，宇兄端执行