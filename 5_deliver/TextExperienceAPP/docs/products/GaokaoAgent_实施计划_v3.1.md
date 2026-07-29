# GaokaoAgent · 智能体实施计划 v3.1

> 基于 8 维框架(v2.1) + 小龙虾统一API + HarmonyOS SDK评估 + 审核反馈
> 2026-07-17 | 鸿蒙特使

---

## 一、架构核心：小龙虾作为个人 APP 服务器

```
每个 APP ──→ 小龙虾统一 API (localhost:8848)
                 │
                 ├── 内容生成 (出题/分析/推荐)
                 ├── 知识库 RAG (高考考纲/知识点)
                 ├── OMAS SDC (代码审查/脚手架)
                 └── Design SOP (Agent 集群设计)
```

**原则：APP只做消费和交互，所有"重"的计算/生成/分析交给小龙虾。**

---

## 二、第一期：地基（本周 · 零 LLM · 零外部依赖）

| # | 维度 | 任务 | SDK | 代码量 |
|:---|:---|:---|:---|:---|
| 1 | **G(协议)** | **小龙虾统一API规范** `lobster-api-v1.yaml` | 无 | 文档 |
| 2 | A | `UserProfile` 数据结构 + Preferences CRUD | preferences | ~40行 |
| 3 | A | `error_attribution` (概念/计算/时间三维) | 纯数据 | ~30行 |
| 4 | B | `IntentContext`：当前Tab + 最近N操作 | @State | ~30行 |
| 5 | B | 跨会话书签：关闭前保存→下次打开恢复 | preferences | ~40行 |
| 6 | C | 基于B→刷题Tab预选学科/难度 | 规则引擎 | ~25行 |
| 7 | H | `BatteryObserver`：<20%暂停后台同步 | batteryInfo | ~20行 |
| 8 | C(冷启动) | 首次使用5题引导→生成初始画像 | 规则引擎 | ~50行 |

**产出：** `v2.1-foundation`

---

## 三、第二期：动手（下周 · 接入小龙虾API）

| # | 维度 | 任务 | SDK | 代码量 |
|:---|:---|:---|:---|:---|
| 9 | D1 | 学习洞察卡片（面板Tab底部） | 纯UI | ~60行 |
| 10 | D2 | 推荐练习按钮（洞察→调用小龙虾生成练习集） | HTTP | ~40行 |
| 11 | D | 分级风险矩阵（D1-D4确认机制） | 纯逻辑 | ~30行 |
| 12 | I | 撤销按钮（修改操作后3分钟内可回滚） | 纯逻辑 | ~30行 |
| 13 | E | 内容管道：PC侧JSON→APP解析入库 | 文件IO | ~80行 |
| **14** | **G** | **小龙虾API v1落地: `POST /task` 请求出题** | HTTP | **~100行** |
| 15 | G | 状态回写: APP掌握度→小龙虾 `POST /state/write-back` | HTTP | ~50行 |

**产出：** `v2.1-hands`

---

## 四、第三期：聪明（LLM就绪后 · 小龙虾后端升级）

| # | 维度 | 任务 | 前置条件 |
|:---|:---|:---|:---|
| 16 | F | 学习路径规划（小龙虾侧 LLM 生成） | A+B+D 就绪 + 小龙虾 LLM |
| 17 | B.3 | LLM意图推断 | LLM API 就绪 |
| 18 | D4 | Agent自动修改配置 | 风险矩阵 + 用户数据 |

**LLM Readiness Checklist（引入前必须完成）：**
- [ ] Prompt 模板库（意图推断/路径规划/分步讲解 各至少3个模板）
- [ ] Token 成本模型
- [ ] 降级策略（LLM不可用→规则引擎 fallback）
- [ ] A/B 测试框架
- [ ] 回滚机制

---

## 五、小龙虾统一 API v1.0

```yaml
# lobster-api-v1.yaml
base: http://localhost:8848/api/v1

endpoints:
  health: GET /health
  task:   POST /task      # 通用任务: 出题/分析/推荐
  knowledge: POST /knowledge/query  # 知识库查询
  content: POST /content/import     # 内容批量导入
  state:  POST /state/write-back    # APP状态→PC回写
```

**适用的 APP（不止 GaokaoAgent）：**

| APP | task_type | 小龙虾做什么 |
|:---|:---|:---|
| gaokao-agent | `generate_questions` | 基于薄弱点出题 |
| gaokao-agent | `analyze_errors` | 错因归因分析 |
| thinkkit-flashcard | `generate_cards` | 生成闪卡内容 |
| thinkkit-coach | `recommend_plan` | 生成学习计划 |
| rhythm-habit | `suggest_habit` | 推荐习惯方案 |
| harmonycoder | `code_review` | 代码审查+修复建议 |

---

## 六、Git 版本规划

| Tag | 内容 | 日期 |
|:---|:---|:---|
| `v1.0-baseline` | 5-tab MVP（已推送） | 07-17 |
| `v2.1-foundation` | 第一期 8项 | 07-18 |
| `v2.1-hands` | 第二期 7项 + 小龙虾API落地 | 07-21 |
| `v3.0-agent` | LLM增强版 | LLM就绪后 |

---

> 🏗️ GaokaoAgent · v3.1 | 小龙虾作为个人APP统一服务器
