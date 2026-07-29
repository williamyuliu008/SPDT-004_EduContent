# Agent Core 公共模块设计 v1.0

> SPDT-001 智能体架构 · Phase 0 产出
> 定义 common/agent-core/ 的模块目录、接口、职责边界
> 鸿蒙特使 🏗️ | 2026-07-18

---

## 设计原则

- **独立模块**: 每个维度一个 .ets 文件，可独立引用
- **接口驱动**: 全部基于 interface，便于 mock 和替换
- **零 LLM**: Phase 0-2 只用规则引擎+本地存储
- **AgentEngine 编排**: 唯一的依赖注入和生命周期管理入口

---

## 目录结构

```
D:\92_products\SPDT-001_Harmony\common\agent-core\
├── index.ets                  # 统一导出
├── AgentEngine.ets            # 编排层（唯一入口）
├── AgentProfile.ets           # A: 长期记忆
├── IntentContext.ets          # B: 短期记忆
├── InputAssist.ets            # C: 输入辅助
├── OutputAction.ets           # D: 输出操作
├── ContentPipeline.ets        # E: 内容管道
├── LobsterClient.ets          # G: 小龙虾HTTP客户端
├── EnvAwareness.ets           # H: 环境感知
├── UndoManager.ets            # I: 撤销管理
└── types.ets                  # 所有共享类型定义
```

---

## 一、AgentEngine.ets — 编排层

### 职责
- 实例化所有维度模块
- 管理智能体生命周期（init / active / background / destroy）
- 提供事件总线，让各维度解耦通信
- APP侧唯一需要导入的类

### 接口设计

```typescript
// common/agent-core/AgentEngine.ets

interface AgentEngineConfig {
  appId: string                         // "gaokao-agent"
  lobsterBaseUrl: string                // "http://localhost:8848/api/v1"
  lobsterMockMode: boolean              // Phase 1: true → 使用本地规则引擎
  dimensions: AgentDimension[]          // 启用的维度，默认全开
  prefs: dataPreferences.Preferences    // HarmonyOS Preferences 实例
}

class AgentEngine {
  // ---- 子模块 ----
  readonly profile: AgentProfile
  readonly intent: IntentContext
  readonly inputAssist: InputAssist
  readonly output: OutputAction
  readonly pipeline: ContentPipeline
  readonly lobster: LobsterClient
  readonly env: EnvAwareness
  readonly undo: UndoManager

  constructor(config: AgentEngineConfig)

  // ---- 生命周期 ----
  async init(): Promise<void>           // 初始化所有模块
  onForeground(): void                  // APP回到前台
  onBackground(): void                  // APP进入后台
  destroy(): void                       // APP即将关闭（保存书签等）

  // ---- 便捷方法 ----
  async request(taskType: string, payload: object): Promise<TaskResponse>
}

type AgentDimension = 'A'|'B'|'C'|'D'|'E'|'G'|'H'|'I'
```

### APP使用示例

```typescript
// entry/src/main/ets/pages/Index.ets

import { AgentEngine } from 'common/agent-core'

@Entry
@Component
struct Index {
  private agent: AgentEngine = new AgentEngine({
    appId: 'gaokao-agent',
    lobsterBaseUrl: 'http://localhost:8848/api/v1',
    lobsterMockMode: true,    // Phase 1 mock
    dimensions: ['A','B','C','D','E','G','H','I'],
    prefs: /* HarmonyOS Preferences */
  })

  async aboutToAppear() {
    await this.agent.init()
    // 冷启动检查
    if (!this.agent.profile.isColdStartComplete()) {
      this.agent.inputAssist.startColdStartGuide()
    }
  }

  async onPageHide() {
    this.agent.onBackground()
  }
}
```

---

## 二、AgentProfile.ets — A 维度：长期记忆

### 职责
- UserProfile CRUD（通过 Preferences 持久化）
- 知识点掌握度对照表
- 错因归因三维模型计算
- 冷启动状态管理

### 接口

```typescript
class AgentProfile {
  // 用户画像
  getProfile(): UserProfile
  updateProfile(partial: Partial<UserProfile>): void
  exportProfile(): UserProfile         // 导出供小龙虾使用
  isColdStartComplete(): boolean
  completeColdStart(profile: UserProfile): void

  // 掌握度
  getMastery(nodeId: string): number
  updateMastery(nodeId: string, correct: boolean, timeSeconds: number): void
  getAllMasteries(): Map<string, MasteryRecord>
  
  // 错因归因
  getErrorAttribution(): ErrorAttribution
  recalculateAttribution(): void       // 基于历史数据重算三维权重
  recordError(nodeId: string, errorType: 'conceptual'|'calculative'|'time_pressure'): void
  
  // 薄弱/优势分析
  getWeaknesses(threshold?: number): string[]    // mastery < threshold
  getStrengths(threshold?: number): string[]     // mastery > threshold
}
```

### 存储方案

```
Preferences Key               Value
───────────────────────────────────────────
agent_profile_v1              JSON: UserProfile
agent_mastery_<nodeId>        JSON: MasteryRecord
agent_error_log               JSON: ErrorLogEntry[]
agent_cold_start_done         boolean
```

---

## 三、IntentContext.ets — B 维度：短期记忆

### 职责
- 跟踪当前 Tab 和视图
- 记录最近 N 个操作序列
- 跨会话书签保存/恢复

### 接口

```typescript
class IntentContext {
  // 上下文跟踪
  setCurrentTab(tab: string): void
  setCurrentView(view: string): void
  getContext(): IntentContextSnapshot
  
  // 动作记录
  recordAction(action: ActionRecord): void
  getRecentActions(limit?: number): ActionRecord[]
  getRecentActionPattern(): string      // 分析最近操作的模式
  
  // 跨会话
  saveBookmark(): void                  // APP关闭时调用
  restoreBookmark(): CrossSessionBookmark | null // APP启动时调用
  
  // 意图推断（规则引擎）
  inferIntent(): 'review' | 'practice' | 'search' | 'idle'
  shouldPreSelect(): boolean            // 是否应该预选条件
  getPreSelectedDomain(): string | null
  getPreSelectedDifficulty(): number | null
}
```

### 规则引擎示例（B→C 的桥梁）

```typescript
inferIntent(): string {
  const actions = this.getRecentActions(5)
  
  // 连续做错同领域3+题 → 意图=复习薄弱点
  const recentErrors = actions.filter(a => a.result === 'wrong')
  if (recentErrors.length >= 3) {
    const sameDomain = /* check if same domain */
    if (sameDomain) return 'review'
  }
  
  // 连续快速作答 → 意图=刷题
  const fastAnswers = actions.filter(a => a.duration_ms < 30000)
  if (fastAnswers.length >= 4) return 'practice'
  
  // 搜索过知识点 → 意图=针对性学习
  const searched = actions.some(a => a.action === 'searched')
  if (searched) return 'search'
  
  return 'idle'
}
```

---

## 四、InputAssist.ets — C 维度：输入辅助

### 职责
- 基于意图推断预选筛选项
- 生成推荐问题/操作
- 冷启动引导流程

### 接口

```typescript
class InputAssist {
  // 预填
  getPreSelection(): PreSelection
  applyPreSelection(context: IntentContext): void
  
  // 推荐
  getRecommendedQuestions(profile: AgentProfile): string[]
  getRecommendedActions(context: IntentContext): RecommendedAction[]
  
  // 冷启动
  startColdStartGuide(): void
  getColdStartQuestions(): Question[]
  submitColdStartAnswers(answers: ColdStartAnswer[]): UserProfile
}

interface PreSelection {
  domain?: string
  difficulty?: number
  board?: string
}

interface RecommendedAction {
  label: string                    // 按钮文字
  target_tab: string               // 跳转目标Tab
  prefill: PreSelection            // 预填参数
  reason: string                   // 为什么推荐
}
```

---

## 五、OutputAction.ets — D 维度：输出操作

### 职责
- D1-D4 分级操作执行
- 风险矩阵判断
- 确认弹窗管理

### 接口

```typescript
class OutputAction {
  // 分级操作
  display(insight: Insight): void              // D1: 展示内容
  recommend(recommendation: Recommendation): void // D2: 推荐+可操作按钮
  execute(action: AgentAction): Promise<void>  // D3: 直接操作
  modifyConfig(config: ConfigChange): void     // D4: 修改配置
  
  // 风险矩阵
  getRiskLevel(actionType: string): 'safe' | 'caution' | 'dangerous'
  needsConfirmation(actionType: string): boolean
  
  // 洞察生成
  generateInsights(profile: AgentProfile, intent: IntentContext): Insight[]
}

interface Insight {
  type: 'strength' | 'weakness' | 'trend' | 'recommendation'
  title: string
  description: string
  data?: Record<string, number>
  action?: RecommendedAction      // D2: 附带可操作按钮
}

// 风险矩阵
const RISK_MATRIX: Record<string, RiskConfig> = {
  'create_practice_set':  { level: 'safe',      confirm: false },
  'start_quiz':           { level: 'safe',      confirm: false },
  'modify_difficulty':    { level: 'caution',   confirm: true },
  'delete_practice_set':  { level: 'dangerous', confirm: true },
  'reset_profile':        { level: 'dangerous', confirm: true },
  'modify_learning_plan': { level: 'caution',   confirm: true },
}
```

---

## 六、LobsterClient.ets — G 维度：小龙虾HTTP客户端

### 职责
- 封装小龙虾 API 的 HTTP 调用
- 自动重试 + 超时降级
- mock 模式支持（Phase 1）

### 接口

```typescript
class LobsterClient {
  // 配置
  constructor(baseUrl: string, mockMode: boolean)
  setMockMode(enabled: boolean): void
  
  // API 方法
  async health(): Promise<HealthStatus>
  async task(request: TaskRequest): Promise<TaskResponse>
  async queryTask(traceId: string): Promise<TaskResponse>
  async queryKnowledge(query: KnowledgeQuery): Promise<KnowledgeNode[]>
  async importContent(content: ContentImport): Promise<ImportResult>
  async writeBackState(updates: StateUpdate[]): Promise<void>
  async registerApp(registration: AppRegistration): Promise<void>
  
  // 降级
  async taskWithFallback(request: TaskRequest): Promise<TaskResponse>
  // 先尝试小龙虾，失败/超时 → 降级到本地规则引擎
}

interface HealthStatus {
  status: 'ok' | 'degraded' | 'down'
  version: string
  ready: boolean
}
```

### 降级策略

```typescript
async taskWithFallback(request: TaskRequest): Promise<TaskResponse> {
  try {
    const response = await this.task(request)
    return response
  } catch (error) {
    if (error.type === 'TIMEOUT' || error.type === 'NETWORK') {
      // 降级到本地规则引擎
      return this.localFallback(request)
    }
    throw error
  }
}

private localFallback(request: TaskRequest): TaskResponse {
  // 每种 task_type 的规则引擎 fallback
  switch (request.task_type) {
    case 'generate_questions':
      return this.fallbackGenerateQuestions(request)
    case 'recommend_plan':
      return this.fallbackRecommendPlan(request)
    default:
      return { status: 'error', trace_id: 'local_fallback', error: { code: 'NO_FALLBACK', message: '无本地降级方案' } }
  }
}
```

---

## 七、ContentPipeline.ets — E 维度：内容管道

### 职责
- 解析小龙虾推送的 JSON 内容
- 格式验证
- 入库管理（替换/增量）

### 接口

```typescript
class ContentPipeline {
  async importFromJson(json: string): Promise<ImportResult>
  async importFromLobster(appId: string, contentType: string): Promise<ImportResult>
  
  validateQuestion(q: Question): ValidationResult
  validateFlashCard(fc: FlashCard): ValidationResult
  
  getManifest(): ContentManifest
  checkForUpdates(lobsterClient: LobsterClient): Promise<boolean>
}

interface ImportResult {
  imported_count: number
  skipped_count: number          // 重复跳过
  error_count: number
  errors: ImportError[]
}
```

### 内容存储方案

```
APP文件系统: entry/src/main/resources/rawfile/content/
├── manifest.json               # ContentManifest
├── questions/
│   ├── math_algebra_v2.json    # 250题
│   ├── math_geometry_v2.json   # 180题
│   └── ...
├── flashcards/
│   ├── math_formulas_v1.json
│   └── ...
└── notes/
    └── ...
```

---

## 八、EnvAwareness.ets — H 维度：环境感知

### 职责
- 电池状态监控
- 网络类型检测
- 通知/勿扰模式感知

### 接口

```typescript
class EnvAwareness {
  getBatteryLevel(): number
  isCharging(): boolean
  getNetworkType(): 'wifi' | 'cellular' | 'none'
  
  shouldThrottleSync(): boolean       // <20%电量且未充电 → true
  shouldUseCellularData(): boolean    // WiFi → true, cellular → 仅小数据
  
  onBatteryChange(callback: (level: number) => void): void
}
```

---

## 九、UndoManager.ets — I 维度：撤销管理

### 职责
- 记录可撤销操作
- 3分钟时间窗口管理
- 撤销执行

### 接口

```typescript
class UndoManager {
  recordAction(action: UndoableAction): void
  canUndo(actionId: string): boolean
  undo(actionId: string): Promise<boolean>
  
  getUndoableActions(): UndoableAction[]   // 当前所有可撤销操作
  clearExpired(): void                     // 清理超过3分钟的操作
}
```

---

## 十、index.ets — 统一导出

```typescript
// common/agent-core/index.ets
export { AgentEngine } from './AgentEngine'
export { AgentProfile } from './AgentProfile'
export { IntentContext } from './IntentContext'
export { InputAssist } from './InputAssist'
export { OutputAction } from './OutputAction'
export { ContentPipeline } from './ContentPipeline'
export { LobsterClient } from './LobsterClient'
export { EnvAwareness } from './EnvAwareness'
export { UndoManager } from './UndoManager'

// 也可整体导出
export { AgentEngine as default } from './AgentEngine'
```

---

> 🏗️ Agent Core v1.0 | 9模块 + 1编排层 | Phase 1 开始实现
