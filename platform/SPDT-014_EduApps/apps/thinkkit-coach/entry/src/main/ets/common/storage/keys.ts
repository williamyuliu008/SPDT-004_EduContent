/**
 * storage/keys.ts — 存储 Key 常量枚举
 *
 * ============================================================================
 * 用途：统一管理所有 Preferences 存储键名，避免魔法字符串散布在代码各处。
 * 维护规则：
 *   - 新增存储键时在此文件中添加条目
 *   - key 命名规范：大写下划线，语义明确
 *   - 按赛道/模块分组注释
 *
 * 用法示例：
 *   import { STORAGE_KEYS } from '../common/storage/keys';
 *   const noteStore = new StorageService<Note>(STORAGE_KEYS.NOTES);
 * ============================================================================
 */

export const STORAGE_KEYS = {
  // ---- 通用 ----
  /** 应用设置（主题、语言等） */
  APP_SETTINGS: 'APP_SETTINGS',

  // ---- Personal Productivity & Knowledge 赛道 ----
  /** 笔记列表（闪卡/ZK 共用） */
  NOTES: 'ALL_NOTES',
  /** 闪卡复习进度 */
  FLASHCARD_PROGRESS: 'FLASHCARD_PROGRESS',

  // ---- Habit & Life Optimization 赛道 ----
  /** 习惯列表 */
  HABITS: 'ALL_HABITS',
  /** 习惯打卡记录 */
  HABIT_CHECKINS: 'HABIT_CHECKINS',
  /** 专注计时记录 */
  FOCUS_SESSIONS: 'FOCUS_SESSIONS',

  // ---- Pro Utility & Dev Tools 赛道 ----
  /** 订阅列表 */
  SUBSCRIPTIONS: 'ALL_SUBSCRIPTIONS',
  /** 极客工具用户偏好 */
  DEV_TOOLS_PREFS: 'DEV_TOOLS_PREFS',
  AGENT_PROFILE: 'AGENT_PROFILE',
  AGENT_MASTERY: 'AGENT_MASTERY',
  CONTENT_MANIFEST: 'CONTENT_MANIFEST',
} as const;

/** 所有合法 key 的联合类型 */
export type StorageKey = typeof STORAGE_KEYS[keyof typeof STORAGE_KEYS];
