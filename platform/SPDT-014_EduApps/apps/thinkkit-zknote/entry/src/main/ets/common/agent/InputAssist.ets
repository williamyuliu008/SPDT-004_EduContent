/**
 * agent/InputAssist.ets — C 维度：输入辅助
 *
 * 职责：基于意图推断预选筛选项 + 推荐问题/操作 + 冷启动引导
 * Phase 1A: 地基 · 零 LLM · 纯规则引擎
 */

import { IntentContext } from './IntentContext';
import { AgentProfile } from './AgentProfile';
import { PreSelection, RecommendedAction, ColdStartAnswer } from './types';

export interface ColdStartProgress { current: number; total: number; }
interface BoardStat { correct: number; total: number; }

// 冷启动引导5题 (按板块采样)
const COLD_START_QUESTIONS: ColdStartQuestion[] = [
  { id: 1, text: '函数 f(x)=x²+2x-3 的最小值是？', options: ['-4', '-3', '-2', '-1'], answer: 0, board: '函数与导数', domain: 'math', difficulty: 1 } as ColdStartQuestion,
  { id: 2, text: '圆 x²+y²=4 的半径是？', options: ['1', '2', '3', '4'], answer: 1, board: '解析几何', domain: 'math', difficulty: 1 } as ColdStartQuestion,
  { id: 3, text: '等差数列 2,5,8,... 的第10项是？', options: ['26', '29', '32', '35'], answer: 1, board: '数列', domain: 'math', difficulty: 1 } as ColdStartQuestion,
  { id: 4, text: '掷一枚硬币两次，至少一次正面的概率？', options: ['1/4', '1/2', '3/4', '1'], answer: 2, board: '概率统计', domain: 'math', difficulty: 1 } as ColdStartQuestion,
  { id: 5, text: 'sin(30°) = ?', options: ['0', '1/2', '√2/2', '√3/2'], answer: 1, board: '三角函数', domain: 'math', difficulty: 1 } as ColdStartQuestion,
];

export interface ColdStartQuestion {
  id: number; text: string; options: string[]; answer: number; board: string; domain: string; difficulty: number;
}

export class InputAssist {
  private profile: AgentProfile;
  private intent: IntentContext;
  private coldStartActive: boolean = false;
  private coldStartAnswers: ColdStartAnswer[] = [];
  private coldStartCurrentQ: number = 0;

  constructor(profile: AgentProfile, intent: IntentContext) {
    this.profile = profile;
    this.intent = intent;
  }

  // ============================================================
  // 预填
  // ============================================================

  getPreSelection(): PreSelection {
    const sel: PreSelection = {};

    if (this.intent.shouldPreSelect()) {
      const domain = this.intent.getPreSelectedDomain();
      if (domain !== null) sel.domain = domain;

      const diff = this.intent.getPreSelectedDifficulty();
      if (diff !== null) sel.difficulty = diff;
    }

    return sel;
  }

  // ============================================================
  // 推荐
  // ============================================================

  getRecommendedActions(): RecommendedAction[] {
    const actions: RecommendedAction[] = [];
    const inferredIntent = this.intent.inferIntent();

    if (inferredIntent === 'review') {
      actions.push({
        label: '复习薄弱点',
        targetTab: 'tutoring',
        prefill: { domain: 'math', difficulty: 1 },
        reason: '你最近做错了3+道题，建议复习相关知识点'
      });
    } else if (inferredIntent === 'practice') {
      actions.push({
        label: '继续刷题',
        targetTab: 'tutoring',
        prefill: {},
        reason: '看起来你正在刷题中，要继续吗？'
      });
    } else if (inferredIntent === 'search') {
      actions.push({
        label: '查看知识地图',
        targetTab: 'knowledge',
        prefill: {},
        reason: '搜索过的知识点在地图中可以查看全貌'
      });
    }

    // 冷启动未完成 → 引导完成冷启动
    if (!this.profile.isColdStartComplete() && !this.coldStartActive) {
      actions.push({
        label: '完善学习画像',
        targetTab: 'diagnostic',
        prefill: {},
        reason: '完成5题引导测试，建立你的学习画像'
      });
    }

    return actions;
  }

  // ============================================================
  // 冷启动引导
  // ============================================================

  startColdStartGuide(): void {
    this.coldStartActive = true;
    this.coldStartAnswers = [];
    this.coldStartCurrentQ = 0;
  }

  getColdStartQuestions(): ColdStartQuestion[] {
    return COLD_START_QUESTIONS;
  }

  getCurrentColdStartQuestion(): ColdStartQuestion | null {
    if (!this.coldStartActive || this.coldStartCurrentQ >= COLD_START_QUESTIONS.length) return null;
    return COLD_START_QUESTIONS[this.coldStartCurrentQ];
  }

  getColdStartProgress(): ColdStartProgress {
    return { current: this.coldStartCurrentQ + 1, total: COLD_START_QUESTIONS.length } as ColdStartProgress;
  }

  submitColdStartAnswer(selectedIndex: number): boolean {
    const q = COLD_START_QUESTIONS[this.coldStartCurrentQ];
    const correct = selectedIndex === q.answer;

    const answer: ColdStartAnswer = {
      questionId: q.id,
      answer: selectedIndex,
      board: q.board,
      correct: correct
    } as ColdStartAnswer;
    this.coldStartAnswers.push(answer);

    this.coldStartCurrentQ++;
    if (this.coldStartCurrentQ >= COLD_START_QUESTIONS.length) {
      this.finishColdStart();
      return true; // 表示完成
    }
    return false; // 还有下一题
  }

  private finishColdStart(): void {
    const correctCount = this.coldStartAnswers.filter(a => a.correct).length;
    const rate = correctCount / this.coldStartAnswers.length;

    // 按板块统计正确率
    const boardMap: Record<string, BoardStat> = {};
    for (let i = 0; i < this.coldStartAnswers.length; i++) {
      const a: ColdStartAnswer = this.coldStartAnswers[i];
      if (boardMap[a.board] === undefined) {
        const stat: BoardStat = { correct: 0, total: 0 };
        boardMap[a.board] = stat;
      }
      boardMap[a.board].total++;
      if (a.correct) boardMap[a.board].correct++;
    }

    const weaknesses: string[] = [];
    const boardKeys = Object.keys(boardMap);
    for (let i = 0; i < boardKeys.length; i++) {
      const b = boardMap[boardKeys[i]];
      if (b.correct / b.total < 0.5) weaknesses.push(boardKeys[i]);
    }

    this.profile.completeColdStart({
      preferredDifficulty: rate >= 0.8 ? 3 : rate >= 0.5 ? 2 : 1,
      weaknesses: weaknesses,
      patienceLevel: rate >= 0.6 ? 4 : 2,
      learningStyle: 'visual'
    });

    this.coldStartActive = false;
  }

  isColdStartActive(): boolean {
    return this.coldStartActive;
  }
}
