/**
 * agent/IntentContext.ets — B 维度：短期记忆
 *
 * 职责：当前Tab跟踪 + 操作序列记录 + 跨会话书签
 * Phase 1A: 地基 · 零 LLM · 纯规则引擎
 */

import { StorageService } from '../storage/storageService';
import { STORAGE_KEYS } from '../storage/keys';
import {
  ActionRecord, IntentContextSnapshot, CrossSessionBookmark
} from './types';

const MAX_RECENT_ACTIONS = 10;
const BOOKMARK_KEY = 'AGENT_BOOKMARK';

export class IntentContext {
  private currentTab: string = 'diagnostic';
  private currentView: string = '';
  private recentActions: ActionRecord[] = [];
  private sessionStart: string = new Date().toISOString();
  private bookmarkStore: StorageService<CrossSessionBookmark>;

  constructor() {
    this.bookmarkStore = new StorageService<CrossSessionBookmark>(BOOKMARK_KEY);
  }

  // ============================================================
  // Tab/View 跟踪
  // ============================================================

  setCurrentTab(tab: string): void {
    if (this.currentTab !== tab) {
      this.recordAction({
        action: 'changed_tab',
        targetId: tab,
        timestamp: new Date().toISOString(),
        durationMs: 0
      });
      this.currentTab = tab;
    }
  }

  setCurrentView(view: string): void {
    this.currentView = view;
  }

  getCurrentTab(): string {
    return this.currentTab;
  }

  getSnapshot(): IntentContextSnapshot {
    return {
      currentTab: this.currentTab,
      currentView: this.currentView,
      recentActions: this.recentActions.slice(),
      sessionStart: this.sessionStart
    };
  }

  // ============================================================
  // 操作记录
  // ============================================================

  recordAction(action: ActionRecord): void {
    this.recentActions.push(action);
    if (this.recentActions.length > MAX_RECENT_ACTIONS) {
      this.recentActions = this.recentActions.slice(-MAX_RECENT_ACTIONS);
    }
  }

  getRecentActions(limit: number = 5): ActionRecord[] {
    return this.recentActions.slice(-limit);
  }

  // ============================================================
  // 意图推断（规则引擎）
  // ============================================================

  inferIntent(): 'review' | 'practice' | 'search' | 'idle' {
    const recent = this.getRecentActions(5);
    if (recent.length === 0) return 'idle';

    // 连续做错同领域3+题 → review
    const errors = recent.filter(a => a.result === 'wrong');
    if (errors.length >= 3) return 'review';

    // 连续快速作答4+ → practice
    const fast = recent.filter(a =>
      a.action === 'answered_question' && a.durationMs < 30000
    );
    if (fast.length >= 4) return 'practice';

    // 搜索过 → search
    const searched = recent.some(a => a.action === 'searched');
    if (searched) return 'search';

    return 'idle';
  }

  shouldPreSelect(): boolean {
    return this.inferIntent() !== 'idle';
  }

  getPreSelectedDomain(): string | null {
    // 从最近错误中提取领域
    const recent = this.getRecentActions(5);
    const errorIds: string[] = [];
    for (let i = 0; i < recent.length; i++) {
      if (recent[i].result === 'wrong' && recent[i].targetId) {
        errorIds.push(recent[i].targetId);
      }
    }
    if (errorIds.length >= 2) return 'math'; // 当前仅数学，后续扩展
    return null;
  }

  getPreSelectedDifficulty(): number | null {
    const recent = this.getRecentActions(5);
    let correct = 0, total = 0;
    for (let i = 0; i < recent.length; i++) {
      if (recent[i].action === 'answered_question') {
        total++;
        if (recent[i].result === 'correct') correct++;
      }
    }
    if (total < 3) return null;

    const rate = correct / total;
    if (rate >= 0.8) return 3;  // 答对率高 → 提难度
    if (rate <= 0.4) return 1;  // 答对率低 → 降难度
    return 2;
  }

  // ============================================================
  // 跨会话书签
  // ============================================================

  async saveBookmark(): Promise<void> {
    const bookmark: CrossSessionBookmark = {
      lastTab: this.currentTab,
      lastView: this.currentView,
      activeQuestionId: undefined,
      savedAt: new Date().toISOString()
    };
    await this.bookmarkStore.save(bookmark, (b: CrossSessionBookmark): string => 'current');
  }

  async restoreBookmark(): Promise<CrossSessionBookmark | null> {
    const bookmarks = await this.bookmarkStore.getAll();
    return bookmarks.length > 0 ? bookmarks[0] : null;
  }
}
