/**
 * algo/streak.ts — 连续打卡天数计算
 *
 * ============================================================================
 * 用途：习惯追踪 / 专注打卡 / 学习记录等需要「连续天数」的场景。
 * 从开源 Streak 计算器（Android Kotlin 版）蒸馏为 TypeScript。
 *
 * ============================================================================
 * 核心逻辑
 * ============================================================================
 * 1. 从今天往前数，直到遇到第一个"未打卡"的日期
 * 2. 特殊处理：今天还没打卡时，从昨天开始算
 * 3. 返回：连续打卡天数、今日是否已打卡、最长连续记录
 *
 * ============================================================================
 * 用法示例
 * ============================================================================
 * import { StreakCalculator } from '../common/algo/streak';
 *
 * // 打卡日期数组（时间戳）
 * const checkins = [1702656000000, 1702742400000, 1702828800000];
 *
 * const streak = StreakCalculator.calculate(checkins);
 * console.log(`当前连续: ${streak.current}天, 最长: ${streak.longest}天`);
 * console.log(`今日已打卡: ${streak.todayDone}`);
 *
 * // 判断今天是否已打卡（用于 UI 按钮状态）
 * if (!streak.todayDone) {
 *   // 显示「打卡」按钮
 * } else {
 *   // 显示「已完成」状态
 * }
 * ============================================================================
 */

// ---- 类型定义 ----

/** 连续打卡计算结果 */
export interface StreakResult {
  /** 当前连续打卡天数 */
  current: number;
  /** 历史最长连续天数 */
  longest: number;
  /** 今日是否已打卡 */
  todayDone: boolean;
  /** 昨日是否已打卡（判断断签用） */
  yesterdayDone: boolean;
  /** 总打卡天数 */
  totalDays: number;
}

// ---- 主计算类 ----

export class StreakCalculator {
  /**
   * 计算连续打卡天数
   *
   * @param checkins - 打卡日期的时间戳数组（ms），可无序
   * @param now - 当前时间戳（默认 Date.now()），方便测试时注入
   * @returns StreakResult
   */
  static calculate(checkins: number[], now?: number): StreakResult {
    const currentTime = now ?? Date.now();

    if (!checkins || checkins.length === 0) {
      return {
        current: 0,
        longest: 0,
        todayDone: false,
        yesterdayDone: false,
        totalDays: 0,
      };
    }

    // 步骤 1：将所有时间戳归一化到「当天零点」并去重
    const normalizedSet = new Set<number>();
    for (const ts of checkins) {
      const normalized = StreakCalculator.normalizeToDayStart(ts);
      normalizedSet.add(normalized);
    }

    // 转为排序数组（从旧到新）
    const days = Array.from(normalizedSet).sort((a, b) => a - b);

    // 步骤 2：计算今天、昨天零点
    const today = StreakCalculator.normalizeToDayStart(currentTime);
    const yesterday = today - 86400000;

    // 步骤 3：检查今日和昨日是否已打卡
    const todayDone = normalizedSet.has(today);
    const yesterdayDone = normalizedSet.has(yesterday);

    // 步骤 4：计算当前连续天数
    // 从"要检查的今天或昨天"开始往前数
    const startDay = todayDone ? today : yesterday;
    let currentStreak = 0;
    let checkDay = startDay;

    while (normalizedSet.has(checkDay)) {
      currentStreak++;
      checkDay -= 86400000; // 往前推一天
    }

    // 如果今天没打卡但昨天打卡了，current 从昨天算起
    // 如果今天和昨天都没打卡，current = 0
    if (!todayDone && !yesterdayDone) {
      currentStreak = 0;
    }

    // 步骤 5：计算历史最长连续天数
    let longestStreak = 0;
    let tempStreak = 1;

    for (let i = 1; i < days.length; i++) {
      if (days[i] - days[i - 1] === 86400000) {
        // 相邻天，连续
        tempStreak++;
      } else {
        // 断开
        longestStreak = Math.max(longestStreak, tempStreak);
        tempStreak = 1;
      }
    }
    // 处理最后一组
    longestStreak = Math.max(longestStreak, tempStreak);

    return {
      current: currentStreak,
      longest: longestStreak,
      todayDone,
      yesterdayDone,
      totalDays: normalizedSet.size,
    };
  }

  /**
   * 将时间戳归一化到当天零点（UTC+8 北京时间）
   *
   * @param timestamp 原始时间戳(ms)
   * @returns 当天零点的时间戳(ms)
   */
  static normalizeToDayStart(timestamp: number): number {
    const date = new Date(timestamp);
    // 使用本地时区（鸿蒙设备上默认本地时间）
    date.setHours(0, 0, 0, 0);
    return date.getTime();
  }

  /**
   * 生成本周的打卡热力图数据
   *
   * @param checkins 打卡日期时间戳数组（ms）
   * @param now 当前时间戳
   * @returns 最近7天的打卡状态数组（索引 0 = 6天前，索引 6 = 今天）
   *
   * @example
   * const week = StreakCalculator.getWeekHeatmap(checkins);
   * // week = [false, true, true, false, true, true, false]
   */
  static getWeekHeatmap(checkins: number[], now?: number): boolean[] {
    const currentTime = now ?? Date.now();
    const todayStart = StreakCalculator.normalizeToDayStart(currentTime);
    const normalizedSet = new Set<number>();

    for (const ts of checkins) {
      normalizedSet.add(StreakCalculator.normalizeToDayStart(ts));
    }

    const result: boolean[] = [];
    for (let i = 6; i >= 0; i--) {
      const dayStart = todayStart - i * 86400000;
      result.push(normalizedSet.has(dayStart));
    }

    return result;
  }

  /**
   * 生成月度的打卡热力图数据
   *
   * @param checkins 打卡日期时间戳数组（ms）
   * @param year 年份
   * @param month 月份（1-12）
   * @returns 该月每天的打卡状态 Map<日期(DD), boolean>
   */
  static getMonthHeatmap(
    checkins: number[],
    year: number,
    month: number
  ): Map<number, boolean> {
    const normalizedSet = new Set<number>();
    for (const ts of checkins) {
      normalizedSet.add(StreakCalculator.normalizeToDayStart(ts));
    }

    const map = new Map<number, boolean>();
    const daysInMonth = new Date(year, month, 0).getDate();

    for (let day = 1; day <= daysInMonth; day++) {
      const dateStr = new Date(year, month - 1, day);
      const dayStart = dateStr.getTime();
      map.set(day, normalizedSet.has(dayStart));
    }

    return map;
  }
}
