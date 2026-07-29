/**
 * agent/OutputAction.ets — D 维度：输出操作
 */

import { Insight, RiskLevel, RiskConfig, RecommendedAction, PreSelection } from './types';

interface InsightPayload {
  count?: number
  rate?: number
  conceptual?: number
  calculative?: number
}

const SAFE: RiskLevel = 'safe' as RiskLevel;
const CAUTION: RiskLevel = 'caution' as RiskLevel;
const DANGEROUS: RiskLevel = 'dangerous' as RiskLevel;

export const RISK_MATRIX: Record<string, RiskConfig> = {
  'create_practice_set':  { level: SAFE,      confirm: false },
  'start_quiz':           { level: SAFE,      confirm: false },
  'modify_difficulty':    { level: CAUTION,   confirm: true },
  'delete_practice_set':  { level: DANGEROUS, confirm: true },
  'reset_profile':        { level: DANGEROUS, confirm: true },
  'modify_learning_plan': { level: CAUTION,   confirm: true },
};

function makeInsight(type: string, title: string, desc: string, data: InsightPayload, action?: RecommendedAction): Insight {
  return { type: type, title: title, description: desc, data: data, action: action };
}

export class OutputAction {
  generateInsights(weaknesses: string[], strengths: string[], errorConceptual: number, errorCalculative: number, recentCorrectRate: number): Insight[] {
    const insights: Insight[] = [];

    if (weaknesses.length > 0) {
      const action: RecommendedAction = {
        label: '开始专项练习', targetTab: 'tutoring',
        prefill: { difficulty: 1 } as PreSelection, reason: '针对薄弱点出题'
      };
      const data: InsightPayload = { count: weaknesses.length };
      insights.push(makeInsight('weakness', '薄弱环节', weaknesses.length + ' 个知识点需要加强', data, action));
    }

    if (strengths.length > 0) {
      const data: InsightPayload = { count: strengths.length };
      insights.push(makeInsight('strength', '已掌握的板块', strengths.length + ' 个知识点掌握良好', data));
    }

    if (recentCorrectRate > 0) {
      const rate: number = Math.round(recentCorrectRate * 100);
      const data: InsightPayload = { rate: rate };
      const stype: string = recentCorrectRate >= 0.7 ? 'strength' : 'weakness';
      insights.push(makeInsight(stype, stype === 'strength' ? '正确率良好' : '正确率偏低', '近期正确率 ' + rate + '%', data));
    }

    if (errorConceptual > 0.4) {
      const action: RecommendedAction = {
        label: '查看知识地图', targetTab: 'knowledge', prefill: {} as PreSelection, reason: '概念薄弱→建议先学再练'
      };
      const data: InsightPayload = { conceptual: Math.round(errorConceptual * 100) };
      insights.push(makeInsight('recommendation', '概念性错误较多', '建议先回顾知识点后再做题', data, action));
    } else if (errorCalculative > 0.4) {
      const action: RecommendedAction = {
        label: '开始练习', targetTab: 'tutoring', prefill: { difficulty: 1 } as PreSelection, reason: '多练习，注意计算细节'
      };
      const data: InsightPayload = { calculative: Math.round(errorCalculative * 100) };
      insights.push(makeInsight('recommendation', '计算错误较多', '建议放慢节奏，仔细检查步骤', data, action));
    }

    return insights;
  }

  getRiskLevel(actionType: string): RiskConfig {
    const config: RiskConfig | undefined = RISK_MATRIX[actionType];
    if (config !== undefined) return config;
    const safe: RiskConfig = { level: SAFE, confirm: false };
    return safe;
  }

  needsConfirmation(actionType: string): boolean { return this.getRiskLevel(actionType).confirm; }

  getConfirmMessage(actionType: string): string {
    const risk: RiskConfig = this.getRiskLevel(actionType);
    if (risk.level === DANGEROUS) return '⚠️ 此操作不可撤销，确认继续？';
    if (risk.level === CAUTION) return '确认执行此操作？';
    return '';
  }
}
