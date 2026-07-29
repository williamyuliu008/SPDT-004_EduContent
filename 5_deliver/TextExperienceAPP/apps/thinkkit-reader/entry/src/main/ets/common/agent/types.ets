/**
 * agent/types.ets — 智能体架构共享类型定义
 *
 * 基于 docs/specs/data-models-v1.md
 * Phase 1: GaokaoAgent 旗舰验证
 */

// ============================================================
// A 维度：长期记忆
// ============================================================

export interface ErrorAttribution {
  conceptual: number     // 概念性错误 0-1
  calculative: number    // 计算性错误 0-1
  timePressure: number   // 时间压力错误 0-1
}

export interface UserProfile {
  schemaVersion: string                    // "1.0"
  learningStyle: 'visual' | 'auditory' | 'kinesthetic'
  targetScore: number
  patienceLevel: number                    // 1-5
  errorAttribution: ErrorAttribution
  strengths: string[]
  weaknesses: string[]
  preferredDifficulty: number              // 1-3
  dailyGoalQuestions: number
  preferredStudyTime: 'morning' | 'afternoon' | 'evening'
  createdAt: string
  updatedAt: string
  coldStartComplete: boolean
}

export interface MasteryRecord {
  nodeId: string
  mastery: number                          // 0-1
  totalAttempts: number
  correctAttempts: number
  avgTimeSeconds: number
  lastAttemptAt: string
  errorTags: string[]
}

// ============================================================
// B 维度：短期记忆
// ============================================================

export interface ActionRecord {
  action: 'answered_question' | 'viewed_insight' | 'searched' | 'changed_tab'
  targetId: string
  timestamp: string
  durationMs: number
  result?: 'correct' | 'wrong' | 'skipped'
}

export interface IntentContextSnapshot {
  currentTab: string
  currentView: string
  recentActions: ActionRecord[]
  sessionStart: string
}

export interface CrossSessionBookmark {
  lastTab: string
  lastView: string
  activeQuestionId?: string
  activePracticeSetId?: string
  savedAt: string
}

// ============================================================
// C 维度：输入辅助
// ============================================================

export interface PreSelection {
  domain?: string
  difficulty?: number
  board?: string
}

export interface RecommendedAction {
  label: string
  targetTab: string
  prefill: PreSelection
  reason: string
}

export interface ColdStartAnswer {
  questionId: number
  answer: number
  board: string
  correct: boolean
}

// ============================================================
// D 维度：输出操作
// ============================================================

export type RiskLevel = 'safe' | 'caution' | 'dangerous'

export interface RiskConfig {
  level: RiskLevel
  confirm: boolean
}

export interface Insight {
  type: string
  title: string
  description: string
  data: ESObject
  action?: RecommendedAction
}

// ============================================================
// G 维度：小龙虾通信 (Phase 1B)
// ============================================================

export interface TaskIntent {
  currentTab: string
  recentActions: string[]
  sessionStart: string
}

export interface TaskRequest {
  appId: string
  taskType: string
  payload: ESObject
  userContext?: UserProfile
  intent?: TaskIntent
  timeoutMs?: number
}

export interface TaskError {
  code: string
  message: string
}

export interface TaskResponse {
  status: 'ok' | 'error' | 'pending'
  result?: ESObject
  error?: TaskError
  traceId: string
  estimatedMs?: number
}

// ============================================================
// H 维度：环境感知
// ============================================================

export interface DeviceEnv {
  batteryLevel: number           // 0-100
  batteryCharging: boolean
  networkType: 'wifi' | 'cellular' | 'none'
  screenOn: boolean
}

// ============================================================
// I 维度：撤销
// ============================================================

export interface UndoableAction {
  id: string
  type: string
  payload: Record<string, object>
  timestamp: string
  expiresAt: string              // timestamp + 3min
}
