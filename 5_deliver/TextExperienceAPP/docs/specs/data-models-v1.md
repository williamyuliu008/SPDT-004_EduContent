# 数据模型标准化 v1.0

> SPDT-001 智能体架构 · Phase 0 产出
> 所有跨 APP、跨维度的共享数据结构定义
> 鸿蒙特使 🏗️ | 2026-07-18

---

## 设计原则

1. **TypeScript-first**: 所有接口用 ArkTS/TypeScript 定义，作为 APP 侧源码参考
2. **小龙虾请求=APP消费**: 请求结构即 API 契约，响应结构即 APP 渲染数据源
3. **渐进精度**: 核心字段 required，扩展字段 optional
4. **版本化**: 每个 Schema 带 `schema_version`，便于向后兼容

---

## 一、A 维度：长期记忆

### UserProfile — 用户画像（持久化到 Preferences）

```typescript
// common/agent-core/AgentProfile.ets

interface UserProfile {
  schema_version: string           // "1.0"
  
  // 学习特征
  learning_style: 'visual' | 'auditory' | 'kinesthetic'
  target_score: number             // 目标分数，如 130
  patience_level: number           // 1-5，影响出题间隔和提示频率
  
  // 薄弱分析
  error_attribution: ErrorAttribution
  strengths: string[]              // 优势知识点ID列表
  weaknesses: string[]             // 薄弱知识点ID列表
  
  // 偏好
  preferred_difficulty: number     // 1-3 偏好难度
  daily_goal_questions: number     // 每日目标题数
  preferred_study_time: string     // "morning" | "afternoon" | "evening"
  
  // 元数据
  created_at: string               // ISO 8601
  updated_at: string               // ISO 8601
  cold_start_complete: boolean     // 冷启动引导是否完成
}

interface ErrorAttribution {
  conceptual: number               // 概念性错误 0-1
  calculative: number              // 计算性错误 0-1
  time_pressure: number            // 时间压力错误 0-1
  // 三个值之和应 ≈ 1.0
}
```

### MasteryRecord — 知识点掌握度

```typescript
interface MasteryRecord {
  node_id: string                  // 知识点ID，如 "alg_001"
  mastery: number                  // 0-1，掌握度
  total_attempts: number           // 总答题次数
  correct_attempts: number         // 正确次数
  avg_time_seconds: number         // 平均用时(秒)
  last_attempt_at: string          // ISO 8601
  error_tags: string[]             // 常见错误标签 ["符号错误", "漏解"]
}
```

---

## 二、B 维度：短期记忆

### IntentContext — 当前上下文

```typescript
// common/agent-core/IntentContext.ets

interface IntentContext {
  current_tab: string              // 当前Tab: "dashboard" | "practice" | "search" | "errors" | "settings"
  current_view: string             // 当前视图细分
  recent_actions: ActionRecord[]   // 最近N个操作 (N≤10)
  session_start: string            // 会话开始时间 ISO 8601
}

interface ActionRecord {
  action: string                   // "answered_question" | "viewed_insight" | "searched" | "changed_tab"
  target_id: string                // 操作对象ID (题目ID/知识点ID)
  timestamp: string                // ISO 8601
  duration_ms: number              // 操作耗时(毫秒)
  result?: string                  // 操作结果 (correct/wrong/skipped)
}
```

### CrossSessionBookmark — 跨会话书签

```typescript
interface CrossSessionBookmark {
  last_tab: string
  last_view: string
  active_question_id?: string      // 正在做的题目ID
  active_practice_set_id?: string  // 正在做的练习集ID
  saved_at: string                 // ISO 8601
}
```

---

## 三、G 维度：小龙虾通信

### TaskRequest — 通用任务请求

```typescript
// common/agent-core/LobsterClient.ets

interface TaskRequest {
  app_id: string                   // 如 "gaokao-agent"
  task_type: string                // 如 "generate_questions"
  payload: Record<string, Object>  // 任务特定参数
  user_context?: UserProfile       // 可选，画像快照
  intent?: IntentSnapshot          // 可选，上下文快照
  timeout_ms?: number              // 默认 30000
}

interface IntentSnapshot {
  current_tab: string
  recent_actions: string[]         // 简化版，只传action名
  session_start: string
}
```

### TaskResponse — 通用任务响应

```typescript
interface TaskResponse {
  status: 'ok' | 'error' | 'pending'
  result?: Record<string, Object>  // status=ok时的结果
  error?: ErrorDetail
  trace_id: string                 // 追踪ID
  estimated_ms?: number            // status=pending时的预计耗时
}

interface ErrorDetail {
  code: string                     // "UNSUPPORTED_TASK_TYPE" etc.
  message: string
}
```

### 各 task_type 的 payload/result 约定

```typescript
// ======= generate_questions =======
interface GenerateQuestionsPayload {
  domain: string                   // "math"
  board: string                    // "解析几何"
  difficulty: number               // 1-3
  count: number                    // 出题数量
  exclude_ids?: string[]           // 排除的题目ID
  focus_nodes?: string[]           // 聚焦的知识点ID
}
interface GenerateQuestionsResult {
  questions: Question[]
  set_id: string
}

// ======= analyze_errors =======
interface AnalyzeErrorsPayload {
  question_ids: string[]           // 要分析的题目ID列表
  user_answers: number[]           // 用户答案索引
}
interface AnalyzeErrorsResult {
  attribution: ErrorAttribution
  recommendations: Recommendation[]
}

// ======= recommend_plan =======
interface RecommendPlanPayload {
  target: string
  weeks_remaining: number
  hours_per_day: number
}
interface RecommendPlanResult {
  weekly_plan: WeekPlan[]
  focus_areas: string[]
}

// ======= generate_cards =======
interface GenerateCardsPayload {
  domain: string
  board: string
  card_type: 'vocab' | 'formula' | 'concept' | 'date'
  count: number
}
interface GenerateCardsResult {
  cards: FlashCard[]
}

// ======= code_review =======
interface CodeReviewPayload {
  language: string                 // "ArkTS" | "Python" | etc.
  code_snippet: string
  context?: string                 // 可选，代码用途说明
}
interface CodeReviewResult {
  issues: CodeIssue[]
  suggestions: string[]
  score: number                    // 0-100
}

// ======= scaffold =======
interface ScaffoldPayload {
  app_type: string                 // "harmony-app" | "harmony-module"
  name: string
  features: string[]               // ["navigation", "preferences", "http"]
}
interface ScaffoldResult {
  files: GeneratedFile[]
  instructions: string
}
```

---

## 四、E 维度：内容管道

### Question — 题目（核心内容类型）

```typescript
interface Question {
  id: string                       // "q_alg_001_001"
  domain: string                   // "math"
  board: string                    // "代数" | "几何" | ...
  node_id: string                  // 关联知识点ID
  difficulty: number               // 1-3
  exam_frequency: 'high' | 'medium' | 'low'
  
  text: string                     // 题目正文
  options: string[]                // 选项 [A, B, C, D]
  answer: number                   // 正确答案索引 0-based
  explanation: string              // 解析
  step_by_step: string[]           // 分步解析
  
  common_mistakes: CommonMistake[] // 常见错误
  tags: string[]                   // 标签
  created_at: string               // ISO 8601
}

interface CommonMistake {
  wrong_answer: number             // 典型错误选项索引
  description: string              // 为什么学生会选这个
  correction_tip: string           // 纠正提示
}
```

### FlashCard — 闪卡

```typescript
interface FlashCard {
  id: string
  domain: string
  card_type: 'vocab' | 'formula' | 'concept' | 'date'
  front: string                    // 正面内容
  back: string                     // 背面内容
  hint?: string
  tags: string[]
}
```

### ContentManifest — 内容清单

```typescript
interface ContentManifest {
  version: string                  // 内容版本号
  updated_at: string               // ISO 8601
  domains: string[]                // 包含的学科域
  content_types: string[]          // "questions" | "flashcards" | "notes"
  item_counts: Record<string, number> // 每种类型数量
  checksum: string                 // MD5
}
```

---

## 五、H 维度：环境感知

```typescript
interface DeviceEnv {
  battery_level: number            // 0-100
  battery_charging: boolean
  network_type: 'wifi' | 'cellular' | 'none'
  screen_on: boolean
  last_user_interaction: string    // ISO 8601
}
```

---

## 六、I 维度：撤销

```typescript
interface UndoableAction {
  id: string
  type: string                     // "answer_question" | "delete_card" | "modify_plan"
  payload: Record<string, Object>  // 撤销所需的反向数据
  timestamp: string                // ISO 8601
  expires_at: string               // timestamp + 3min
}
```

---

## 七、跨APP共享（Phase 3）

```typescript
// 小龙虾内部维护
interface CrossAppContext {
  entries: Record<string, AppStateSnapshot> // app_id → 状态快照
  relations: CrossAppRelation[]             // APP间关系
}

interface AppStateSnapshot {
  app_id: string
  last_active: string              // ISO 8601
  key_metrics: Record<string, number>
  recent_outputs: string[]         // 最近产出ID列表
}

interface CrossAppRelation {
  source_app: string               // "gaokao-agent"
  target_app: string               // "thinkkit-flashcard"
  relation_type: string            // "error_to_card" | "schedule_to_plan"
  enabled: boolean
}
```

---

> 🏗️ 数据模型 v1.0 | 3 大核心模型 + 6 种 task_type 约定 + 跨APP扩展
