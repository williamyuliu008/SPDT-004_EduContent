/**
 * utils/format.ts — 数字格式化与时长格式化
 *
 * ============================================================================
 * 所有函数均为纯函数，可在 ArkTS 页面和工具类中直接调用。
 * 涵盖：数字千分位、货币、百分比、文件大小、时长（秒 → 可读字符串）。
 * ============================================================================
 */

/**
 * 数字千分位格式化
 *
 * @param value - 原始数字
 * @param decimals - 保留小数位数，默认 0
 * @returns 带千分位逗号的字符串
 *
 * @example
 * formatNumber(1234567)        // → '1,234,567'
 * formatNumber(1234567.89, 2)  // → '1,234,567.89'
 * formatNumber(-9876, 0)       // → '-9,876'
 */
export function formatNumber(value: number, decimals: number = 0): string {
  if (!isFinite(value)) {
    return '0';
  }
  const fixed = value.toFixed(decimals);
  const [intPart, decimalPart] = fixed.split('.');
  const formattedInt = intPart.replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  return decimalPart !== undefined ? `${formattedInt}.${decimalPart}` : formattedInt;
}

/**
 * 货币格式化（人民币）
 *
 * @param value - 金额（单位：元）
 * @param symbol - 货币符号，默认 '¥'
 * @returns 格式化后的金额字符串
 *
 * @example
 * formatCurrency(1999)       // → '¥1,999.00'
 * formatCurrency(29.9)       // → '¥29.90'
 * formatCurrency(0)          // → '¥0.00'
 * formatCurrency(1234, '$')  // → '$1,234.00'
 */
export function formatCurrency(value: number, symbol: string = '¥'): string {
  return `${symbol}${formatNumber(value, 2)}`;
}

/**
 * 百分比格式化
 *
 * @param value - 比例值（0.0 ~ 1.0）
 * @param decimals - 小数位数，默认 1
 * @returns 百分比字符串
 *
 * @example
 * formatPercent(0.857)      // → '85.7%'
 * formatPercent(1)          // → '100.0%'
 * formatPercent(0.333, 0)   // → '33%'
 */
export function formatPercent(value: number, decimals: number = 1): string {
  if (!isFinite(value)) {
    return '0%';
  }
  const pct = Math.min(100, Math.max(0, value * 100));
  return `${pct.toFixed(decimals)}%`;
}

/**
 * 文件大小格式化
 *
 * @param bytes - 字节数
 * @returns 可读的文件大小字符串
 *
 * @example
 * formatFileSize(0)           // → '0 B'
 * formatFileSize(1024)        // → '1.0 KB'
 * formatFileSize(1048576)     // → '1.0 MB'
 * formatFileSize(1073741824)  // → '1.0 GB'
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) {
    return '0 B';
  }
  const units = ['B', 'KB', 'MB', 'GB', 'TB'];
  const k = 1024;
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  const size = bytes / Math.pow(k, i);
  return `${size.toFixed(1)} ${units[i]}`;
}

/**
 * 时长格式化（秒 → 可读字符串）
 *
 * @param totalSeconds - 总秒数
 * @param format - 输出格式：'compact' | 'verbose'，默认 'compact'
 * @returns 时长字符串
 *
 * @example
 * formatDuration(65)                         // → '01:05'
 * formatDuration(3661)                       // → '01:01:01'
 * formatDuration(65, 'verbose')              // → '1分钟5秒'
 * formatDuration(3661, 'verbose')            // → '1小时1分钟1秒'
 * formatDuration(0)                          // → '00:00'
 */
export function formatDuration(totalSeconds: number, format: 'compact' | 'verbose' = 'compact'): string {
  if (totalSeconds < 0) {
    totalSeconds = 0;
  }

  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = Math.floor(totalSeconds % 60);

  if (format === 'verbose') {
    const parts: string[] = [];
    if (hours > 0) {
      parts.push(`${hours}小时`);
    }
    if (minutes > 0) {
      parts.push(`${minutes}分钟`);
    }
    if (seconds > 0 || parts.length === 0) {
      parts.push(`${seconds}秒`);
    }
    return parts.join('');
  }

  // compact: HH:MM:SS 或 MM:SS
  const pad = (n: number): string => n.toString().padStart(2, '0');
  if (hours > 0) {
    return `${pad(hours)}:${pad(minutes)}:${pad(seconds)}`;
  }
  return `${pad(minutes)}:${pad(seconds)}`;
}

/**
 * 数字截断缩写（用于大数字显示）
 *
 * @param value - 原始数字
 * @returns 缩写后的字符串（中文单位）
 *
 * @example
 * abbreviateNumber(1234)       // → '1,234'
 * abbreviateNumber(12345)      // → '1.2万'
 * abbreviateNumber(12345678)   // → '1234.6万'
 * abbreviateNumber(123456789)  // → '1.2亿'
 */
export function abbreviateNumber(value: number): string {
  if (value < 10000) {
    return formatNumber(value);
  }
  if (value < 100000000) {
    return `${(value / 10000).toFixed(1)}万`;
  }
  return `${(value / 100000000).toFixed(1)}亿`;
}

/**
 * 补零到指定位数
 *
 * @param value 数字
 * @param length 目标长度
 * @returns 补零后的字符串
 *
 * @example
 * padZero(5, 2)  // → '05'
 * padZero(42, 4) // → '0042'
 */
export function padZero(value: number, length: number): string {
  return value.toString().padStart(length, '0');
}
