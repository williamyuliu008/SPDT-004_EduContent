/**
 * storage/keys.ts — 存储 Key 常量枚举
 *
 * ============================================================================
 * 用途：统一管理所有 Preferences 存储键名，避免魔法字符串散布在代码各处。
 * 维护规则：
 *   - 新增存储键时在此文件中添加条目
 *   - key 命名规范：大写下划线，语义明确
 *   - 按赛道/模块分组注释
 * ============================================================================
 */

export const STORAGE_KEYS = {
  // ---- 通用 ----
  /** 应用设置（主题、语言等） */
  APP_SETTINGS: 'APP_SETTINGS',

  // ---- Mindmap 专用 ----
  /** 思维导图列表 */
  MINDMAPS: 'MINDMAPS',
  /** 导图节点数据 */
  MINDMAP_NODES: 'MINDMAP_NODES',
  /** 导图设置 */
  MINDMAP_SETTINGS: 'MINDMAP_SETTINGS',

  // ---- Agent · 智能体维度 ----
  /** 用户画像 (A维度) */
  AGENT_PROFILE: 'AGENT_PROFILE',
  /** 知识点掌握度 (A维度) */
  AGENT_MASTERY: 'AGENT_MASTERY',
  /** 内容清单 (E维度) */
  CONTENT_MANIFEST: 'CONTENT_MANIFEST',
} as const;

/** 所有合法 key 的联合类型 */
export type StorageKey = typeof STORAGE_KEYS[keyof typeof STORAGE_KEYS];
