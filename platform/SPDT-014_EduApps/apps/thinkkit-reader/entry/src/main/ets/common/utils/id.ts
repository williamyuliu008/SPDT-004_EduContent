/**
 * utils/id.ts — 唯一 ID 生成器
 */

export function generateId(prefix: string = ''): string {
  const timestamp36 = Date.now().toString(36);
  const random8 = Math.random().toString(36).substring(2, 10);
  return `${prefix}${timestamp36}${random8}`;
}

export function shortId(length: number = 8): string {
  return Math.random().toString(36).substring(2, 2 + length);
}
