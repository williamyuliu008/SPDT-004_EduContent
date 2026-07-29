/**
 * algo/sm2.ts — SM-2 间隔重复算法（用于闪卡/记忆复习类 App）
 *
 * ============================================================================
 * 算法来源
 * ============================================================================
 * SM-2（SuperMemo-2）是 Piotr Woźniak 开发的间隔重复算法，广泛应用于
 * Anki、Supermemo 等闪卡软件。本实现参考 Anki 源码与 SM-2 原始论文，
 * 从 Python/Java 开源实现蒸馏为 TypeScript（ArkTS 兼容）。
 *
 * ============================================================================
 * 核心概念
 * ============================================================================
 * - Ease Factor (EF)：简易度因子，默认 2.5，范围 [1.3, ∞)
 * - Interval：复习间隔（天），首次复习后为 1 天，之后每次按 EF 放大
 * - Repetition：复习次数。首次复习 = 0，接下来 1, 2, ...
 * - Quality：用户自评质量（0-5），≥3 算"记住了"，<3 算"忘了"
 *
 * ============================================================================
 * 质量标准
 * ============================================================================
 * 0: 完全不记得
 * 1: 错误回答，但看到正确答案后回想起来了
 * 2: 错误回答，但看到正确答案后感觉很容易
 * 3: 正确回答，但有严重困难
 * 4: 正确回答，稍有犹豫
 * 5: 完美正确，毫不费力
 *
 * ============================================================================
 * 用法示例
 * ============================================================================
 * import { SM2, SM2Quality } from '../common/algo/sm2';
 *
 * // 卡片初始状态
 * let card = SM2.create();
 *
 * // 用户复习后评分
 * card = SM2.review(card, SM2Quality.PERFECT);  // 5分
 *
 * // 获取下次复习日期
 * const nextReview = new Date(card.nextReviewAt);
 * console.log(`下次复习: ${nextReview.toLocaleDateString()}, 间隔: ${card.interval}天`);
 *
 * // 忘记后重置
 * card = SM2.review(card, SM2Quality.BLACKOUT);  // 0分 → 重置
 * ============================================================================
 */

// ---- 类型定义 ----

/** SM-2 评分质量（0-5） */
export enum SM2Quality {
  BLACKOUT = 0,     // 完全不记得
  INCORRECT = 1,    // 错误，但看到答案后想起
  INCORRECT_EASY = 2, // 错误，但看到答案后觉得容易
  HARD = 3,         // 正确，但有严重困难
  GOOD = 4,         // 正确，稍有犹豫
  PERFECT = 5,      // 完美
}

/** 闪卡复习状态 */
export interface SM2Card {
  /** 简易度因子（E-Factor），初始 2.5 */
  easeFactor: number;
  /** 下次复习间隔（天） */
  interval: number;
  /** 已完成复习次数 */
  repetitions: number;
  /** 下次复习日期的时间戳（ms） */
  nextReviewAt: number;
  /** 上次复习日期的时间戳（ms） */
  lastReviewAt: number;
}

// ---- 常量 ----

/** 最小简易度因子（EF 不会低于此值） */
const MIN_EASE_FACTOR = 1.3;

/** 初始简易度因子 */
const DEFAULT_EASE_FACTOR = 2.5;

/** 初始间隔（天） */
const DEFAULT_INTERVAL = 0;

// ============================================================================
// 公开 API
// ============================================================================

export class SM2 {
  /**
   * 创建一张新的闪卡（初始状态）
   *
   * @returns 初始状态的 SM2Card
   */
  static create(): SM2Card {
    return {
      easeFactor: DEFAULT_EASE_FACTOR,
      interval: DEFAULT_INTERVAL,
      repetitions: 0,
      nextReviewAt: Date.now(),
      lastReviewAt: 0,
    };
  }

  /**
   * 对闪卡进行一次复习，根据用户评分更新状态
   *
   * @param card - 当前闪卡状态
   * @param quality - 用户自评分数（0-5）
   * @returns 更新后的闪卡状态（新对象，不修改原对象）
   */
  static review(card: SM2Card, quality: SM2Quality): SM2Card {
    // 防御性克隆，避免修改原对象
    const updated: SM2Card = {
      easeFactor: card.easeFactor,
      interval: card.interval,
      repetitions: card.repetitions,
      nextReviewAt: card.nextReviewAt,
      lastReviewAt: Date.now(),
    };

    // 分值必须在 0-5 之间
    const q = Math.max(0, Math.min(5, quality));

    if (q >= SM2Quality.HARD) {
      // ---- 记住了：更新间隔 ----
      if (updated.repetitions === 0) {
        // 第一次正确回忆：间隔 1 天
        updated.interval = 1;
      } else if (updated.repetitions === 1) {
        // 第二次正确回忆：间隔 6 天
        updated.interval = 6;
      } else {
        // 第三次及以上：间隔 = 上次间隔 × EF
        updated.interval = Math.round(updated.interval * updated.easeFactor);
      }

      updated.repetitions += 1;
    } else {
      // ---- 忘了：重置进度 ----
      updated.repetitions = 0;
      updated.interval = 1; // 1 天后重试
    }

    // 更新简易度因子（EF）
    updated.easeFactor = this.calculateEF(updated.easeFactor, q);

    // 计算下次复习时间
    updated.nextReviewAt = Date.now() + updated.interval * 86400000; // 86400000ms = 1天

    return updated;
  }

  /**
   * 计算新的简易度因子
   *
   * EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
   *
   * @param currentEF 当前 EF
   * @param quality 评分（0-5）
   * @returns 更新后的 EF（不低于 MIN_EASE_FACTOR）
   */
  private static calculateEF(currentEF: number, quality: number): number {
    const delta = 5 - quality;
    const newEF = currentEF + (0.1 - delta * (0.08 + delta * 0.02));

    // EF 不能低于最小值
    if (newEF < MIN_EASE_FACTOR) {
      return MIN_EASE_FACTOR;
    }

    return Math.round(newEF * 100) / 100; // 保留 2 位小数
  }

  /**
   * 检查卡片是否已到复习时间
   *
   * @param card 闪卡状态
   * @param now 当前时间戳（默认 Date.now()）
   * @returns true = 应该现在复习
   */
  static isDue(card: SM2Card, now?: number): boolean {
    const n = now ?? Date.now();
    return n >= card.nextReviewAt;
  }

  /**
   * 获取下次复习的倒计时描述
   *
   * @param card 闪卡状态
   * @returns 可读的倒计时字符串
   *
   * @example
   * SM2.getDueDescription(card) // → '今天复习' | '明天复习' | '3天后复习' | '已过期2天'
   */
  static getDueDescription(card: SM2Card): string {
    const now = Date.now();
    const diff = card.nextReviewAt - now;
    const days = Math.ceil(diff / 86400000);

    if (diff <= 0) {
      const overdue = Math.abs(Math.floor(diff / 86400000));
      if (overdue === 0) {
        return '今天复习';
      }
      return `已过期${overdue}天`;
    }

    if (days === 0) {
      return '今天复习';
    }
    if (days === 1) {
      return '明天复习';
    }
    return `${days}天后复习`;
  }

  /**
   * 批量获取到期卡片
   *
   * @param cards 所有闪卡
   * @returns 已到期的卡片数组
   */
  static getDueCards<T extends { sm2: SM2Card }>(cards: T[]): T[] {
    const now = Date.now();
    return cards.filter(c => c.sm2.nextReviewAt <= now);
  }

  /**
   * 获取卡片复习统计
   *
   * @param cards 所有闪卡
   * @returns 统计信息
   */
  static getStats(cards: { sm2: SM2Card }[]): SM2Stats {
    const now = Date.now();
    let newCards = 0;   // 从未复习过的
    let dueCards = 0;   // 到期待复习
    let learned = 0;    // 已掌握（间隔 ≥ 21 天且未到期）

    for (const card of cards) {
      const c = card.sm2;
      if (c.repetitions === 0) {
        newCards++;
      } else if (c.nextReviewAt <= now) {
        dueCards++;
      } else if (c.interval >= 21) {
        learned++;
      }
    }

    return {
      total: cards.length,
      newCards,
      dueCards,
      learned,
    };
  }
}

/** 复习统计 */
export interface SM2Stats {
  total: number;
  newCards: number;
  dueCards: number;
  learned: number;
}
