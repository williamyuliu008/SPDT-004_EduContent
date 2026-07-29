# GaokaoAgent · 智能体实施计划 v3.0

> 基于 8 维框架(v2.1) + HarmonyOS SDK 评估 + 审核反馈(10项)
> 2026-07-17 | 鸿蒙特使

---

## 一、SDK 可用性速查

| 需要 | SDK | 状态 |
|:---|:---|:---|
| 本地 KV 存储 | `@ohos.data.preferences` | ✅ common/ 已有 |
| 设备电量/状态 | `@ohos.batteryInfo` | ✅ 可直接用 |
| 系统专注模式 | `@ohos.intelligentScene` | ✅ 可直接用 |
| 本地 AI 推理 | `@ohos.ai.mindSporeLite` | ⚠️ 引擎可用，需模型 |
| 通知推送 | `@ohos.notification` | ✅ 可直接用 |
| 后台任务 | `@ohos.backgroundTaskManager` | ⚠️ 有系统限制 |
| 语音识别 | HMS Speech Kit | ❌ SDK 不提供 |
| OCR 文字识别 | HMS ML Kit | ❌ SDK 不提供 |
| 大模型对话 | 无原生 API | ❌ 需外部服务 |

**策略：** 先用 SDK 原生能力建基础（A/B/C/D/H），外部服务（语音/OCR/LLM）留到 v3.0+。

---

## 二、三期实施计划

### 第一期：地基（本周 · 零 LLM · 零外部依赖）

| # | 维度 | 任务 | SDK | 代码量 | 验证方式 |
|:---|:---|:---|:---|:---|:---|
| 1 | G(协议) | **小龙虾统一API规范** `lobster-api-v1.yaml` | 无 | 文档 | 协议评审通过 |
| 2 | A | `UserProfile` 数据结构 + Preferences CRUD | preferences | ~40行 | 读写测试 |
| 3 | A | `error_attribution` 初始化（概念/计算/时间三维） | 纯数据 | ~30行 | 诊断结果可写入 |
| 4 | B | `IntentContext`：当前Tab + 最近N操作 | @State | ~30行 | 控制台打印验证 |
| 5 | B | 跨会话书签：关闭前保存 → 下次打开恢复 | preferences | ~40行 | 关APP重开验证 |
| 6 | C | 基于B→刷题Tab预选学科/难度 | 规则引擎 | ~25行 | UI 验证 |
| 7 | H | `BatteryObserver`：<20%暂停后台同步 | batteryInfo | ~20行 | 低电量弹窗 |
| 8 | C(冷启动) | 首次使用5题引导 → 生成初始画像 | 规则引擎 | ~50行 | 新装APP走通 |

**产出：** 8个任务全部完成后 commit `v2.1-foundation`

### 第二期：动手（下周 · 零 LLM）

| # | 维度 | 任务 | SDK | 代码量 | 验证方式 |
|:---|:---|:---|:---|:---|:---|
| 9 | D1 | 学习洞察卡片（面板Tab底部） | 纯UI | ~60行 | 面板滚动可见 |
| 10 | D2 | 推荐练习按钮（洞察→一键创建练习集） | Navigation | ~40行 | 点击跳转刷题Tab |
| 11 | D | 分级风险矩阵（D1-D4确认机制） | 纯逻辑 | ~30行 | 各场景弹窗验证 |
| 12 | I | 撤销按钮（修改操作后3分钟内可回滚） | 纯逻辑 | ~30行 | 撤销验证 |
| 13 | E | 内容管道第一版：PC侧JSON→APP解析入库 | 文件IO | ~80行 | 导入测试JSON验证 |
| 14 | G | 状态回写协议：APP掌握度→PC知识图谱 | preferences+export | ~50行 | PC端验证颜色变化 |

**产出：** 6个任务完成后 commit `v2.1-hands`

### 第三期：聪明（两周后 · 引入 LLM）

| # | 维度 | 任务 | 前置条件 |
|:---|:---|:---|:---|
| 15 | F | 学习路径规划 | A+B+D 全部就绪 |
| 16 | B.3 | LLM意图推断（替代规则引擎） | LLM API 就绪 |
| 17 | D4 | Agent自动修改配置 | 风险矩阵 + 1期用户数据 |
| 18 | 🧪 | LLM Readiness Checklist 全部通过 | Prompt模板等 |

**LLM Readiness Checklist（引入前必须完成）：**
- [ ] Prompt 模板库（意图推断/路径规划/分步讲解 各至少3个模板）
- [ ] Token 成本模型（日活×人均调用×单价→月度预算）
- [ ] 降级策略（LLM不可用时→规则引擎 fallback）
- [ ] A/B 测试框架（LLM版 vs 规则版的对比指标）
- [ ] 回滚机制（新版出问题时一键切回规则引擎）

---

## 三、本期（第一期）任务拆解

### 任务 1：SHARED_CTX 协议定义（G 维度）

**产出文件：** `SHARED_CTX/lobster-api-v1.yaml`

```yaml
# 小龙虾统一API v1.0 — PC作为APP的个人服务器
# 每个APP通过此接口向PC侧小龙虾请求内容/计算/知识

base: http://localhost:8848/api/v1

endpoints:
  health:
    GET /health → {status, version, ready}
  
  task:
    POST /task
    请求:
      app_id: string        # 如"gaokao-agent"
      task_type: enum        # generate_questions | analyze_errors | recommend_plan
      payload: object        # 任务特定参数
      user_context: object   # 可选，用户画像快照
    响应:
      status: ok|error|pending
      result: object         # 任务特定结果
      trace_id: string       # 用于查询异步任务
  
  knowledge:
    POST /knowledge/query
    请求: {app_id, domain, board, query}
    响应: {nodes: [{id,name,examFrequency,...}]}
  
  content:
    POST /content/import
    请求: {app_id, content_type, data: []}
    响应: {imported_count, errors: []}
  
  state:
    POST /state/write-back
    请求: {app_id, updates: [{node_id, mastery, timestamp}]}
    响应: {acknowledged: true}
```

**关键设计决策：**
- `task_type` 是枚举值，不是自由对话——每个APP预定义3-5种任务
- `app_id` 让小龙虾做差异化处理
- 初期小龙虾侧 mock 实现，接口规范定了，后续替换后端零成本
- 所有响应带 `trace_id`，APP端可查询异步任务状态

### 任务 2-3：UserProfile + error_attribution（A 维度）

**修改文件：** `services/storage.ts`（新建）

```
UserProfile 结构:
  ├─ learningStyle: 从用户答题模式推断
  ├─ errorAttribution: {conceptual, calculative, timePressure}
  ├─ masteryMap: {nodeId → score}
  ├─ sessionBookmark: {lastTab, lastQuestion, context}
  └─ createdAt / updatedAt

存储: @ohos.data.preferences (已有 common/)
```

### 任务 4-5：IntentContext + 跨会话书签（B 维度）

```
IntentContext 结构:
  ├─ currentTab: 'diagnostic' | 'tutoring' | ...
  ├─ recentActions: 最近5个用户操作
  ├─ inferredIntent: string | null
  ├─ confidence: 0-1
  └─ envStatus: {battery, isCharging}

持久化: 每次 tab 切换或操作完成 → 写 preferences
恢复: aboutToAppear() 中读取 → 恢复到上次状态
```

### 任务 6：预填推荐（C 维度）

基于 IntentContext → 
- 如果是 tutoring Tab → 预选最近做的学科和难度
- 如果是 diagnostic Tab → 提示"上次诊断3天前，要不要重新诊断？"
- 如果刚做错一道题 → 推荐同类题

### 任务 7：电池感知（H 维度）

```
@ohos.batteryInfo.batterySOC → 电量%
< 20% 且未充电 → 提示用户 + 暂停后台同步
```

### 任务 8：冷启动引导（C 维度）

首次使用（UserProfile 为空时）→ 渐进式引导：
1. "你是高三吗？"（1题）
2. "你想重点提升数学的哪个板块？"（选择）
3. "每天能花多少时间刷题？"（选择）
4. "你的数学基础自评？"（4档滑动条）
5. 基于以上→生成初始 UserProfile → 推荐首次诊断

---

## 四、Git 版本规划

| Tag | 内容 | 日期 |
|:---|:---|:---|
| `v1.0-baseline` | 5-tab MVP （已推送） | 07-17 |
| `v2.1-foundation` | 第一期 8 项完成 | 07-18 |
| `v2.1-hands` | 第二期 6 项完成 | 07-21 |
| `v3.0-agent` | LLM 增强版 | LLM 就绪后 |

---

> 🏗️ GaokaoAgent · 实施计划 v3.0 | 基于 8维框架 + SDK评估 + 10项审核反馈
