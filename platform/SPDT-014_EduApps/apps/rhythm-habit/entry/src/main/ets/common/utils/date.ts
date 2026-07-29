/**
 * utils/date.ts — 日期格式化与星期计算
 *
 * ============================================================================
 * 所有函数均为纯函数（无副作用），可在 ArkTS 页面和工具类中直接调用。
 * 不依赖任何第三方库，基于原生 Date 实现。
 * ============================================================================
 */

/**
 * 格式化日期为指定格式字符串
 *
 * @param date - Date 对象或时间戳(ms)
 * @param format - 格式模板，支持以下占位符：
 *   YYYY → 四位年份    MM → 两位月份    DD → 两位日期
 *   HH → 两位小时      mm → 两位分钟    ss → 两位秒
 * @returns 格式化后的日期字符串
 *
 * @example
 * formatDate(new Date(), 'YYYY-MM-DD')          // → '2026-06-16'
 * formatDate(Date.now(), 'YYYY/MM/DD HH:mm')    // → '2026/06/16 21:55'
 * formatDate(new Date(2026, 0, 1), 'YYYY年MM月DD日') // → '2026年01月01日'
 */
export function formatDate(date: Date | number, format: string): string {
  const d = date instanceof Date ? date : new Date(date);
  if (isNaN(d.getTime())) {
    return '';
  }

  const pad = (n: number): string => n.toString().padStart(2, '0');

  const tokens: Record<string, string> = {
    'YYYY': d.getFullYear().toString(),
    'MM': pad(d.getMonth() + 1),
    'DD': pad(d.getDate()),
    'HH': pad(d.getHours()),
    'mm': pad(d.getMinutes()),
    'ss': pad(d.getSeconds()),
  };

  let result = format;
  for (const key of Object.keys(tokens)) {
    result = result.replace(key, tokens[key]);
  }
  return result;
}

/**
 * 获取相对时间描述（刚刚 / X分钟前 / X小时前 / X天前 / 具体日期）
 *
 * @param date - Date 对象或时间戳(ms)
 * @param now - 当前时间戳(ms)，默认 Date.now()
 * @returns 相对时间字符串
 *
 * @example
 * timeAgo(Date.now() - 30000)        // → '刚刚'
 * timeAgo(Date.now() - 300000)       // → '5分钟前'
 * timeAgo(Date.now() - 7200000)      // → '2小时前'
 * timeAgo(Date.now() - 86400000)     // → '1天前'
 * timeAgo(Date.now() - 259200000)    // → '3天前'
 * timeAgo(Date.now() - 604800000)    // → '06-10'（超过7天显示具体日期）
 */
export function timeAgo(date: Date | number, now?: number): string {
  const d = date instanceof Date ? date : new Date(date);
  const n = now ?? Date.now();
  const diff = n - d.getTime();

  if (diff < 0) {
    return '刚刚';
  }

  const seconds = Math.floor(diff / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);

  if (seconds < 60) {
    return '刚刚';
  }
  if (minutes < 60) {
    return `${minutes}分钟前`;
  }
  if (hours < 24) {
    return `${hours}小时前`;
  }
  if (days < 7) {
    return `${days}天前`;
  }
  // 超过 7 天显示具体日期
  return formatDate(d, 'MM-DD');
}

/**
 * 获取指定日期的星期名称
 *
 * @param date - Date 对象或时间戳(ms)
 * @param lang - 语言：'zh'（中文） | 'en'（英文缩写），默认 'zh'
 * @returns 星期字符串
 *
 * @example
 * getWeekday(new Date(2026, 5, 16))    // → '星期二'
 * getWeekday(new Date(2026, 5, 16), 'en') // → 'Tue'
 */
export function getWeekday(date: Date | number, lang: 'zh' | 'en' = 'zh'): string {
  const d = date instanceof Date ? date : new Date(date);
  const zhNames = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六'];
  const enNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  return lang === 'zh' ? zhNames[d.getDay()] : enNames[d.getDay()];
}

/**
 * 判断两个日期是否为同一天
 *
 * @param date1 日期1
 * @param date2 日期2（默认今天）
 * @returns 是否同一天
 *
 * @example
 * isSameDay(new Date(), new Date())             // → true
 * isSameDay(new Date(), new Date('2026-06-15')) // → false
 */
export function isSameDay(date1: Date | number, date2?: Date | number): boolean {
  const d1 = date1 instanceof Date ? date1 : new Date(date1);
  const d2 = date2 ? (date2 instanceof Date ? date2 : new Date(date2)) : new Date();
  return (
    d1.getFullYear() === d2.getFullYear() &&
    d1.getMonth() === d2.getMonth() &&
    d1.getDate() === d2.getDate()
  );
}

/**
 * 获取指定日期所在周的起始日期（周一）和结束日期（周日）
 *
 * @param date - 参考日期
 * @returns { start: Date, end: Date }
 */
export function getWeekRange(date: Date | number): { start: Date; end: Date } {
  const d = date instanceof Date ? date : new Date(date);
  const dayOfWeek = d.getDay();
  // 周一为起始（周日=0 需特殊处理）
  const diffToMonday = dayOfWeek === 0 ? -6 : 1 - dayOfWeek;
  const start = new Date(d);
  start.setDate(d.getDate() + diffToMonday);
  start.setHours(0, 0, 0, 0);

  const end = new Date(start);
  end.setDate(start.getDate() + 6);
  end.setHours(23, 59, 59, 999);

  return { start, end };
}

/**
 * 获取两个日期之间的天数差
 *
 * @param date1 较早日期
 * @param date2 较晚日期
 * @returns 天数差（整数）
 */
export function daysBetween(date1: Date | number, date2: Date | number): number {
  const d1 = date1 instanceof Date ? date1 : new Date(date1);
  const d2 = date2 instanceof Date ? date2 : new Date(date2);

  // 归一化到当天零点
  const utc1 = Date.UTC(d1.getFullYear(), d1.getMonth(), d1.getDate());
  const utc2 = Date.UTC(d2.getFullYear(), d2.getMonth(), d2.getDate());

  return Math.floor(Math.abs(utc2 - utc1) / (1000 * 60 * 60 * 24));
}

/**
 * 获取某个月的天数
 *
 * @param year  年份
 * @param month 月份（1-12）
 * @returns 该月天数
 */
export function daysInMonth(year: number, month: number): number {
  return new Date(year, month, 0).getDate();
}
