/**
 * utils/debounce.ts — 防抖与节流
 *
 * ArkTS 兼容的防抖 (debounce) 和节流 (throttle) 工具函数。
 * 使用 setTimeout/clearTimeout，适用于页面搜索输入、按钮防连点等场景。
 *
 * ============================================================================
 * 用法示例
 * ============================================================================
 * import { debounce, throttle } from '../common/utils/debounce';
 *
 * // 搜索输入防抖
 * this.searchInput.onChange(debounce((val: string) => { this.search(val); }, 300));
 *
 * // 按钮防连点
 * Button('提交').onClick(throttle(() => { this.submit(); }, 1000));
 */

/**
 * 创建防抖函数
 *
 * 在连续调用时，只有最后一次调用在 delay 毫秒后执行。
 *
 * @param fn 目标函数
 * @param delay 延迟毫秒，默认 300
 * @returns 防抖后的函数
 *
 * @example
 * const debouncedSearch = debounce((keyword: string) => { this.doSearch(keyword); }, 300);
 * debouncedSearch('鸿蒙');
 * debouncedSearch('鸿蒙开发'); // 只执行最后一次
 */
export function debounce<T extends (...args: unknown[]) => void>(
  fn: T,
  delay: number = 300
): (...args: Parameters<T>) => void {
  let timer: number = -1;

  return function (this: unknown, ...args: Parameters<T>): void {
    if (timer >= 0) {
      clearTimeout(timer);
    }
    timer = setTimeout(() => {
      fn.apply(this, args);
      timer = -1;
    }, delay);
  };
}

/**
 * 创建节流函数
 *
 * 在 interval 毫秒内只执行一次，忽略后续调用。
 *
 * @param fn 目标函数
 * @param interval 节流间隔毫秒，默认 1000
 * @returns 节流后的函数
 *
 * @example
 * const throttledSave = throttle(() => { this.saveData(); }, 2000);
 * throttledSave(); // 执行
 * throttledSave(); // 忽略
 */
export function throttle<T extends (...args: unknown[]) => void>(
  fn: T,
  interval: number = 1000
): (...args: Parameters<T>) => void {
  let lastTime = 0;

  return function (this: unknown, ...args: Parameters<T>): void {
    const now = Date.now();
    if (now - lastTime >= interval) {
      lastTime = now;
      fn.apply(this, args);
    }
  };
}
