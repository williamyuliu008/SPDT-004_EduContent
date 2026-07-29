/**
 * agent/AgentProfile.ets — A 维度：长期记忆
 *
 * 职责：UserProfile CRUD + 知识点掌握度 + 错因归因三维模型
 * 存储：HarmonyOS Preferences
 *
 * Phase 1A: 地基 · 零 LLM · 纯规则引擎
 */

import { StorageService } from '../storage/storageService';
import { STORAGE_KEYS } from '../storage/keys';
import {
  UserProfile, MasteryRecord, ErrorAttribution
} from './types';

const DEFAULT_PROFILE: UserProfile = {
  schemaVersion: '1.0',
  learningStyle: 'visual',
  targetScore: 120,
  patienceLevel: 3,
  errorAttribution: { conceptual: 0.4, calculative: 0.4, timePressure: 0.2 },
  strengths: [],
  weaknesses: [],
  preferredDifficulty: 2,
  dailyGoalQuestions: 10,
  preferredStudyTime: 'evening',
  createdAt: '',
  updatedAt: '',
  coldStartComplete: false
};

export class AgentProfile {
  private profileStore: StorageService<UserProfile>;
  private masteryStore: StorageService<MasteryRecord>;
  private profile: UserProfile | null = null;

  constructor() {
    this.profileStore = new StorageService<UserProfile>(STORAGE_KEYS.AGENT_PROFILE);
    this.masteryStore = new StorageService<MasteryRecord>(STORAGE_KEYS.AGENT_MASTERY);
  }

  // ============================================================
  // 初始化
  // ============================================================

  async init(): Promise<void> {
    const profiles = await this.profileStore.getAll();
    if (profiles.length === 0) {
      const now = new Date().toISOString();
      const d = DEFAULT_PROFILE;
      this.profile = {
        schemaVersion: d.schemaVersion, learningStyle: d.learningStyle,
        targetScore: d.targetScore, patienceLevel: d.patienceLevel,
        errorAttribution: d.errorAttribution,
        strengths: d.strengths, weaknesses: d.weaknesses,
        preferredDifficulty: d.preferredDifficulty, dailyGoalQuestions: d.dailyGoalQuestions,
        preferredStudyTime: d.preferredStudyTime,
        createdAt: now, updatedAt: now, coldStartComplete: d.coldStartComplete
      };
      await this.profileStore.save(this.profile, (p: UserProfile): string => 'singleton');
    } else {
      this.profile = profiles[0];
    }
  }

  // ============================================================
  // 用户画像
  // ============================================================

  getProfile(): UserProfile {
    return this.profile!;
  }

  getSnapshot(): UserProfile {
    const p: UserProfile = this.profile!;
    const attr: ErrorAttribution = {
      conceptual: p.errorAttribution.conceptual,
      calculative: p.errorAttribution.calculative,
      timePressure: p.errorAttribution.timePressure
    };
    return {
      schemaVersion: p.schemaVersion, learningStyle: p.learningStyle,
      targetScore: p.targetScore, patienceLevel: p.patienceLevel,
      errorAttribution: attr,
      strengths: p.strengths.slice(), weaknesses: p.weaknesses.slice(),
      preferredDifficulty: p.preferredDifficulty, dailyGoalQuestions: p.dailyGoalQuestions,
      preferredStudyTime: p.preferredStudyTime,
      createdAt: p.createdAt, updatedAt: p.updatedAt, coldStartComplete: p.coldStartComplete
    };
  }

  async updateProfile(partial: Partial<UserProfile>): Promise<void> {
    const p: UserProfile = this.profile!;
    this.profile = {
      schemaVersion: partial.schemaVersion !== undefined ? partial.schemaVersion : p.schemaVersion,
      learningStyle: partial.learningStyle !== undefined ? partial.learningStyle : p.learningStyle,
      targetScore: partial.targetScore !== undefined ? partial.targetScore : p.targetScore,
      patienceLevel: partial.patienceLevel !== undefined ? partial.patienceLevel : p.patienceLevel,
      errorAttribution: partial.errorAttribution !== undefined ? partial.errorAttribution : p.errorAttribution,
      strengths: partial.strengths !== undefined ? partial.strengths : p.strengths,
      weaknesses: partial.weaknesses !== undefined ? partial.weaknesses : p.weaknesses,
      preferredDifficulty: partial.preferredDifficulty !== undefined ? partial.preferredDifficulty : p.preferredDifficulty,
      dailyGoalQuestions: partial.dailyGoalQuestions !== undefined ? partial.dailyGoalQuestions : p.dailyGoalQuestions,
      preferredStudyTime: partial.preferredStudyTime !== undefined ? partial.preferredStudyTime : p.preferredStudyTime,
      createdAt: p.createdAt,
      updatedAt: new Date().toISOString(),
      coldStartComplete: partial.coldStartComplete !== undefined ? partial.coldStartComplete : p.coldStartComplete
    };
    await this.profileStore.save(this.profile, (p: UserProfile): string => 'singleton');
  }

  isColdStartComplete(): boolean {
    return this.profile!.coldStartComplete;
  }

  async completeColdStart(partial: Partial<UserProfile>): Promise<void> {
    const d = DEFAULT_PROFILE;
    this.profile = {
      schemaVersion: d.schemaVersion,
      learningStyle: partial.learningStyle !== undefined ? partial.learningStyle : d.learningStyle,
      targetScore: partial.targetScore !== undefined ? partial.targetScore : d.targetScore,
      patienceLevel: partial.patienceLevel !== undefined ? partial.patienceLevel : d.patienceLevel,
      errorAttribution: partial.errorAttribution !== undefined ? partial.errorAttribution : d.errorAttribution,
      strengths: partial.strengths !== undefined ? partial.strengths : d.strengths,
      weaknesses: partial.weaknesses !== undefined ? partial.weaknesses : d.weaknesses,
      preferredDifficulty: partial.preferredDifficulty !== undefined ? partial.preferredDifficulty : d.preferredDifficulty,
      dailyGoalQuestions: partial.dailyGoalQuestions !== undefined ? partial.dailyGoalQuestions : d.dailyGoalQuestions,
      preferredStudyTime: partial.preferredStudyTime !== undefined ? partial.preferredStudyTime : d.preferredStudyTime,
      coldStartComplete: true,
      updatedAt: new Date().toISOString(),
      createdAt: d.createdAt
    };
    await this.profileStore.save(this.profile, (p: UserProfile): string => 'singleton');
  }

  // ============================================================
  // 掌握度
  // ============================================================

  async getMastery(nodeId: string): Promise<number> {
    const records = await this.masteryStore.getAll();
    for (let i = 0; i < records.length; i++) {
      if (records[i].nodeId === nodeId) return records[i].mastery;
    }
    return 0.5; // 默认中等
  }

  async updateMastery(nodeId: string, correct: boolean, timeSeconds: number): Promise<void> {
    const records = await this.masteryStore.getAll();
    let record: MasteryRecord | null = null;
    for (let i = 0; i < records.length; i++) {
      if (records[i].nodeId === nodeId) { record = records[i]; break; }
    }

    if (record === null) {
      record = {
        nodeId: nodeId,
        mastery: correct ? 0.65 : 0.35,
        totalAttempts: 1,
        correctAttempts: correct ? 1 : 0,
        avgTimeSeconds: timeSeconds,
        lastAttemptAt: new Date().toISOString(),
        errorTags: []
      };
    } else {
      record.totalAttempts++;
      if (correct) record.correctAttempts++;
      record.mastery = record.correctAttempts / record.totalAttempts;
      // 加权平均耗时
      record.avgTimeSeconds = Math.round(
        (record.avgTimeSeconds * (record.totalAttempts - 1) + timeSeconds) / record.totalAttempts
      );
      record.lastAttemptAt = new Date().toISOString();
    }

    await this.masteryStore.save(record, (r: MasteryRecord): string => r.nodeId);
  }

  async getMasteries(): Promise<MasteryRecord[]> {
    return await this.masteryStore.getAll();
  }

  // ============================================================
  // 错因归因三维模型
  // ============================================================

  async recordError(nodeId: string, errorType: 'conceptual' | 'calculative' | 'timePressure'): Promise<void> {
    // 更新掌握度记录的错误标签
    const records = await this.masteryStore.getAll();
    let record: MasteryRecord | null = null;
    for (let i = 0; i < records.length; i++) {
      if (records[i].nodeId === nodeId) { record = records[i]; break; }
    }
    if (record !== null) {
      if (record.errorTags.indexOf(errorType) === -1) {
        record.errorTags.push(errorType);
      }
      await this.masteryStore.save(record, (r: MasteryRecord): string => r.nodeId);
    }

    // 重新计算三维权重
    await this.recalculateAttribution();
  }

  async recalculateAttribution(): Promise<void> {
    const records = await this.masteryStore.getAll();
    let conceptual = 0, calculative = 0, timePressure = 0;
    let total = 0;

    for (let i = 0; i < records.length; i++) {
      const tags = records[i].errorTags;
      for (let j = 0; j < tags.length; j++) {
        if (tags[j] === 'conceptual') conceptual++;
        else if (tags[j] === 'calculative') calculative++;
        else if (tags[j] === 'timePressure') timePressure++;
        total++;
      }
    }

    if (total > 0) {
      this.profile!.errorAttribution = {
        conceptual: Math.round(conceptual / total * 100) / 100,
        calculative: Math.round(calculative / total * 100) / 100,
        timePressure: Math.round(timePressure / total * 100) / 100
      };
      await this.profileStore.save(this.profile!, (p: UserProfile): string => 'singleton');
    }
  }

  getErrorAttribution(): ErrorAttribution {
    return this.profile!.errorAttribution;
  }

  // ============================================================
  // 薄弱/优势分析
  // ============================================================

  async getWeaknesses(threshold: number = 0.4): Promise<string[]> {
    const records = await this.masteryStore.getAll();
    const result: string[] = [];
    for (let i = 0; i < records.length; i++) {
      if (records[i].mastery < threshold) result.push(records[i].nodeId);
    }
    return result;
  }

  async getStrengths(threshold: number = 0.7): Promise<string[]> {
    const records = await this.masteryStore.getAll();
    const result: string[] = [];
    for (let i = 0; i < records.length; i++) {
      if (records[i].mastery >= threshold) result.push(records[i].nodeId);
    }
    return result;
  }
}
