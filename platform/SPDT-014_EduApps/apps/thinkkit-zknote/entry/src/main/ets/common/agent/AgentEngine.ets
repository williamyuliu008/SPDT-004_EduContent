/**
 * agent-core/AgentEngine.ets — 编排层
 *
 * APP侧唯一需要导入的类。实例化所有8维模块，管理生命周期。
 * Phase 2: 从 GaokaoAgent 提炼 → 共享模块
 */

import { AgentProfile } from './AgentProfile';
import { IntentContext } from './IntentContext';
import { InputAssist, ColdStartQuestion, ColdStartProgress } from './InputAssist';
import { OutputAction } from './OutputAction';
import { EnvAwareness } from './EnvAwareness';
import { LobsterClient } from './LobsterClient';
import { UndoManager } from './UndoManager';
import { ContentPipeline } from './ContentPipeline';
import { Insight, RecommendedAction, PreSelection, UserProfile, TaskResponse, ColdStartAnswer } from './types';

export type AgentDimension = 'A' | 'B' | 'C' | 'D' | 'E' | 'G' | 'H' | 'I';

export interface AgentConfig {
  appId: string;
  lobsterBaseUrl: string;
  mockMode: boolean;
  dimensions: AgentDimension[];
}

/**
 * AgentEngine — 智能体引擎唯一入口
 *
 * 用法:
 *   const agent = new AgentEngine({
 *     appId: 'thinkkit-coach',
 *     lobsterBaseUrl: 'http://localhost:8848/api/v1',
 *     mockMode: true,
 *     dimensions: ['A','B','C','D','G']
 *   });
 *   await agent.init();
 *   const profile = agent.profile.getProfile();
 *   const insights = agent.output.generateInsights(...);
 */
export class AgentEngine {
  readonly config: AgentConfig;
  readonly profile: AgentProfile;
  readonly intent: IntentContext;
  readonly input: InputAssist;
  readonly output: OutputAction;
  readonly env: EnvAwareness;
  readonly lobster: LobsterClient;
  readonly undo: UndoManager;
  readonly pipeline: ContentPipeline;

  constructor(config: AgentConfig) {
    this.config = config;
    this.profile = new AgentProfile();
    this.intent = new IntentContext();
    this.input = new InputAssist(this.profile, this.intent);
    this.output = new OutputAction();
    this.env = new EnvAwareness();
    this.lobster = new LobsterClient(config.lobsterBaseUrl, config.mockMode);
    this.undo = new UndoManager();
    this.pipeline = new ContentPipeline();
  }

  async init(): Promise<void> {
    await this.profile.init();
    const bookmark = await this.intent.restoreBookmark();
    if (bookmark !== null && bookmark.lastTab) {
      // 返回值供APP侧决定是否恢复
    }
  }

  /** 快速获取当前画像 */
  getProfile(): UserProfile { return this.profile.getProfile(); }

  /** 快速获取推荐操作 */
  getRecommendedActions(): RecommendedAction[] { return this.input.getRecommendedActions(); }

  /** 快速生成洞察 */
  generateInsights(weaknesses: string[], strengths: string[], errorCon: number, errorCal: number, rate: number): Insight[] {
    return this.output.generateInsights(weaknesses, strengths, errorCon, errorCal, rate);
  }

  /** Tab切换 */
  setTab(tab: string): void { this.intent.setCurrentTab(tab); }

  /** 记录操作 */
  recordAction(action: string, targetId: string, durationMs: number, result?: string): void {
    this.intent.recordAction({
      action: action as 'answered_question' | 'viewed_insight' | 'searched' | 'changed_tab',
      targetId: targetId, timestamp: new Date().toISOString(), durationMs: durationMs,
      result: result as 'correct' | 'wrong' | 'skipped'
    });
  }

  /** 保存书签 */
  async saveBookmark(): Promise<void> { await this.intent.saveBookmark(); }

  /** 冷启动 */
  startColdStart(): void { this.input.startColdStartGuide(); }
  getColdStartQuestion(): ColdStartQuestion | null { return this.input.getCurrentColdStartQuestion(); }
  getColdStartProgress(): ColdStartProgress { return this.input.getColdStartProgress(); }
  submitColdStartAnswer(idx: number): boolean { return this.input.submitColdStartAnswer(idx); }
  isColdStartActive(): boolean { return this.input.isColdStartActive(); }
  isColdStartComplete(): boolean { return this.profile.isColdStartComplete(); }
}
