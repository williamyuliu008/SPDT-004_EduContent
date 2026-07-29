/**
 * 入境 APP · 数据模型
 * Chain（逻辑链/剧本）和 Card（节点卡）的核心类型定义
 */

/** 学科 */
export enum Subject {
  HISTORY = '历史',
  GEOGRAPHY = '地理',
  POLITICS = '政治',
  GUWEN = '古诗文',
  CALLIGRAPHY = '书法'
}

/** 链类型 */
export enum ChainType {
  CAUSAL = '因果链',
  TIMELINE = '时序链',
  COMPARISON = '对比链',
  ELEMENT = '要素链',
  THEORY = '理论运用链'
}

/** 卡片类型（对齐 PT-038 产出） */
export enum CardType {
  NODE = '节点卡',
  STRATEGY = '心法卡',
  CHAIN = '链卡'
}

/** 生熟标记 */
export enum Maturity {
  RAW = '生',
  COOKED = '熟'
}

/** 链节点角色 */
export enum ChainRole {
  BACKGROUND = '背景条件',
  TRIGGER = '触发事件',
  PROCESS = '中间过程',
  RESULT = '结果',
  COUNTER = '反例',
  PATTERN = '规律'
}

/** AI 上下文级别 */
export enum ContextLevel {
  LIGHT = 'light',
  STANDARD = 'standard',
  FULL = 'full'
}

/** 媒体类型 */
export enum MediaType {
  AUDIO = 'audio',
  VIDEO = 'video'
}

// ─── Chain（逻辑链/剧本）─────────────────────────────

export interface Chain {
  chain_id: string
  title: string
  subject: Subject
  chain_type: ChainType
  narrative: string          // 四幕微剧本叙事文本（来自 micro_dramas.json）
  child_cards: string[]       // card_id 列表
  related_chains: string[]    // 关联链 ID
  tags: string[]
  card_count: number
  raw_count: number           // 生卡数量
  cooked_count: number        // 熟卡数量
  last_viewed: number         // timestamp
  created_at: number
  updated_at: number
}

// ─── Card（节点卡）──────────────────────────────────

export interface Card {
  card_id: string
  chain_id: string
  chain_title: string
  card_type: CardType
  chain_role: ChainRole
  front: string
  back_core: string
  back_detail: string
  maturity: Maturity
  tags: string[]
  is_new: boolean             // APP 侧新增：本周新导入
  last_marked: number         // timestamp：上次标记生/熟的时间
  media?: MediaRef[]          // 关联的音频/视频
}

// ─── 导入相关 ───────────────────────────────────────

/** PT-038 卡片包顶层结构 */
export interface CardPackage {
  version: string
  series: string
  total_chains: number
  total_cards: number
  node_cards?: Card[]
  strategy_cards?: Card[]
  chain_cards?: Card[]
  // v1/v2 扁平格式兼容
  cards?: Card[]
}

/** 链元数据导入格式 */
export interface ChainMeta {
  chain_id: string
  chain_title: string
  chain_type: string
  subject: string
  narrative: string
  related_chains: string[]
  tags: string[]
  episode_count?: number
  card_count?: number
}

// ─── 媒体相关 ───────────────────────────────────────

export interface MediaRef {
  type: MediaType
  src: string                // 本地文件路径
  title: string
  duration?: number          // 秒
  chain_id: string
}

// ─── AI 相关 ────────────────────────────────────────

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: number
}

export interface AIContext {
  level: ContextLevel
  card?: Card
  chain?: Chain
  recentMessages: ChatMessage[]
}

export interface AIResponse {
  content: string
  card_suggestions?: CardSuggestion[]  // AI 建议的卡片
}

export interface CardSuggestion {
  front: string
  back_core: string
  chain_id: string
  card_type: CardType
}

/** AI 功能类型 */
export enum AIAction {
  QA = 'qa',
  CARD_GEN = 'card_gen',
  ANSWER_TO_CARD = 'answer_to_card',
  CHAIN_GEN = 'chain_gen',
  EXAM_GEN = 'exam_gen'
}

// ─── 学习会话 ───────────────────────────────────────

export interface StudySession {
  chain_id: string
  start_time: number
  cards_reviewed: number
  cards_marked_raw: number
  cards_marked_cooked: number
  completed: boolean
}

// ─── 仪表盘 ─────────────────────────────────────────

export interface DashboardStats {
  total_cards: number
  total_chains: number
  raw_count: number
  cooked_count: number
  new_this_week: number
  today_reviewed: number
}

// ─── 数据库辅助类型 ─────────────────────────────────

/** 聊天记录（DB查询返回） */
export interface ChatRecord {
  id: string
  role: string
  content: string
  timestamp: number
}

/** AI 请求消息 */
export interface AIMessage {
  role: string
  content: string
}

/** HTTP 请求选项 */
export interface HttpRequestOptions {
  method: number
  header: Record<string, string>
  extraData: string
  expectDataType: number
  connectTimeout: number
  readTimeout: number
}

/** 仪表盘统计（DB查询返回） */
export interface DashboardCounts {
  total_cards: number
  total_chains: number
  raw_count: number
  cooked_count: number
}
