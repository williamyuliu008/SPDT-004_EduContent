/**
 * utils/id.ts — 唯一 ID 生成器
 *
 * 基于时间戳 + 随机字符串，生成排序友好的唯一 ID。
 * 不依赖任何外部库，可在 ArkTS 环境和纯 TypeScript 中通用。
 *
 * ============================================================================
 * 用法示例
 * ============================================================================
 * const noteId = generateId();           // → 'lxv8k2m9p4qr'
 * const cardId = generateId('card_');    // → 'card_lxv8k2m9p4qr'
 */

/**
 * 生成唯一 ID
 *
 * 格式：{prefix}{timestamp36}{random8}
 * - timestamp36：当前毫秒时间戳的 36 进制表示（8 位，保证时序递增）
 * - random8：Math.random 36 进制 8 位（保证唯一性）
 *
 * @param prefix - 可选前缀，如 'note_' / 'habit_' / 'card_'
 * @returns 唯一 ID 字符串
 *
 * @example
 * generateId()          // → 'l3m5k7n9p2q4'
 * generateId('note_')   // → 'note_l3m5k7n9p2q4'
 */
export function generateId(prefix: string = ''): string {
  const timestamp36 = Date.now().toString(36);
  const random8 = Math.random().toString(36).substring(2, 10);
  return `${prefix}${timestamp36}${random8}`;
}

/**
 * 生成短 ID（仅随机部分，适合显示用）
 *
 * @param length 长度，默认 8
 * @returns 短随机字符串
 */
export function shortId(length: number = 8): string {
  return Math.random().toString(36).substring(2, 2 + length);
}
