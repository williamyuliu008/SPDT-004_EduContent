/**
 * 入境 APP · AI 服务抽象层
 * 支持多后端切换：智谱 GLM / OpenAI / 本地模型
 */

import { db } from './DatabaseService';
import { AIContext, AIAction, CardSuggestion, ChatMessage, ChatRecord, Card, CardType, ContextLevel, AIMessage } from '../model/DataModel';
import { getChainNarrative } from './ImportService';
import { http } from '@kit.NetworkKit';

// ─── AI 后端配置 ──────────────────────────────────

export interface AIBackendConfig {
  name: string
  apiUrl: string
  apiKey: string
  model: string
  enabled: boolean
}

export class AIService {
  private backend: AIBackendConfig;
  private defaultSystemPrompt: string;

  constructor() {
    this.backend = {
      name: 'zhipu',
      apiUrl: 'https://open.bigmodel.cn/api/paas/v4/chat/completions',
      apiKey: '',
      model: 'glm-4-flash',
      enabled: true
    };

    this.defaultSystemPrompt = '你是一位高考文科（历史/地理/政治）辅导专家。\n' +
      '你擅长将复杂知识点拆解为清晰易懂的解释，帮助学生建立知识框架。\n' +
      '回答时要：\n' +
      '1. 结合提供的知识点上下文\n' +
      '2. 用学生能理解的语言\n' +
      '3. 适当举例说明\n' +
      '4. 不超过300字（除非用户要求详细回答）';
  }

  /**
   * 配置 AI 后端
   */
  setBackend(config: AIBackendConfig): void {
    this.backend = config;
  }

  getBackend(): AIBackendConfig {
    return this.backend;
  }

  // ─── 上下文构建 ──────────────────────────────────

  /**
   * 构建不同级别的上下文 prompt
   */
  async buildContext(level: ContextLevel, card?: Card, chain_id?: string): Promise<string> {
    let ctx = '';

    if (card) {
      ctx += '【当前卡片】\n';
      ctx += '问题: ' + card.front + '\n';
      ctx += '答案: ' + card.back_core + '\n';
      if (card.back_detail) {
        ctx += '详解: ' + card.back_detail + '\n';
      }
      ctx += '所属知识链: ' + card.chain_title + '\n\n';
    }

    if (level === ContextLevel.STANDARD || level === ContextLevel.FULL) {
      const cid: string = chain_id !== undefined ? chain_id : (card ? card.chain_id : '');
      if (cid) {
        const narrative = getChainNarrative(cid);
        if (narrative) {
          ctx += '【知识链叙事背景】\n' + narrative + '\n\n';
        }

        const cards = await db.getCardsByChain(cid);
        const frontList = cards
          .filter((c: Card) => c.card_id !== (card ? card.card_id : ''))
          .map((c: Card) => '· ' + c.front)
          .join('\n');
        if (frontList) {
          ctx += '【同链其他知识点】\n' + frontList + '\n\n';
        }
      }
    }

    if (level === ContextLevel.FULL) {
      if (card && card.chain_id) {
        const cards = await db.getCardsByChain(card.chain_id);
        ctx += '【同链全部卡片详情】\n';
        for (const c of cards) {
          ctx += '- ' + c.front + ' → ' + c.back_core + '\n';
        }
        ctx += '\n';
      }
    }

    return ctx;
  }

  // ─── AI 动作 → ContextLevel 映射 ─────────────────

  getDefaultLevel(action: AIAction): ContextLevel {
    switch (action) {
      case AIAction.QA: return ContextLevel.STANDARD;
      case AIAction.CARD_GEN: return ContextLevel.STANDARD;
      case AIAction.ANSWER_TO_CARD: return ContextLevel.STANDARD;
      case AIAction.CHAIN_GEN: return ContextLevel.FULL;
      case AIAction.EXAM_GEN: return ContextLevel.FULL;
      default: return ContextLevel.STANDARD;
    }
  }

  // ─── 动作 → System Prompt 映射 ─────────────────

  getActionPrompt(action: AIAction): string {
    const base = this.defaultSystemPrompt;

    switch (action) {
      case AIAction.QA:
        return base;
      case AIAction.CARD_GEN:
        return base + '\n' +
          '【制卡任务】\n' +
          '你是制卡专家。请从用户提供的文本中提取关键知识点，为每个知识点生成一张知识卡片。\n' +
          '每张卡片包含：\n' +
          '- front: 一个简洁的设问（不超过20字）\n' +
          '- back_core: 核心答案（1-2行，不超过40字）\n' +
          '- chain_id: 请用户指定\n' +
          '- card_type: 节点卡/心法卡/链卡（默认为节点卡）\n\n' +
          '请以JSON数组格式输出：[{"front":"...","back_core":"...","card_type":"节点卡"}]';
      case AIAction.ANSWER_TO_CARD:
        return base + '\n' +
          '【回答转卡片任务】\n' +
          '用户想把你的回答中的关键知识点转为卡片。请从你的回答中提取1-3个关键知识点，按JSON数组格式输出：\n' +
          '[{"front":"设问","back_core":"核心答案","card_type":"节点卡"}]';
      case AIAction.EXAM_GEN:
        return base + '\n' +
          '【模拟出题任务】\n' +
          '你是命题专家。根据提供的知识链内容，生成模拟考题。支持三种难度：\n' +
          '- 难度Ⅰ：直问直答，考查基础知识点\n' +
          '- 难度Ⅱ：结合材料分析，考查理解和运用\n' +
          '- 难度Ⅲ：跨章节综合题，考查知识迁移和论证能力\n' +
          '为每道题提供参考答案和得分点。';
      case AIAction.CHAIN_GEN:
        return base + '\n' +
          '【知识链生成任务】\n' +
          '你是课程设计专家。根据用户指定的知识点范围，生成教学知识链。\n' +
          '请按以下结构输出完整的四段式知识链叙事：\n' +
          '1. 逻辑主线与背景（为什么重要 / 必然规律）\n' +
          '2. 时空舞台与冲突（关键时间地点人物 / 矛盾张力）\n' +
          '3. 关键人事与选择（核心转折点 / 考点密集区）\n' +
          '4. 去向与今启（对今天的意义 / 可迁移的规律）\n' +
          '同时标注出叙事中的关键记忆点，建议生成节点卡。';
      default:
        return base;
    }
  }

  // ─── 主调方法 ──────────────────────────────────

  /**
   * 发送 AI 请求
   */
  async sendMessage(
    action: AIAction,
    userMessage: string,
    context: string,
    history: ChatMessage[]
  ): Promise<string> {
    if (!this.backend.apiKey) {
      return 'AI 服务未配置 API Key，请在设置中配置。';
    }

    const messages: AIMessage[] = [];

    // System prompt
    const sysMsg: AIMessage = { role: 'system', content: this.getActionPrompt(action) };
    messages.push(sysMsg);

    // 上下文
    if (context) {
      const ctxMsg: AIMessage = { role: 'system', content: '当前知识上下文：\n' + context };
      messages.push(ctxMsg);
    }

    // 历史消息（最近10条）
    const recentHistory = history.slice(-10);
    for (const msg of recentHistory) {
      const histMsg: AIMessage = { role: msg.role, content: msg.content };
      messages.push(histMsg);
    }

    // 当前消息
    const userMsg: AIMessage = { role: 'user', content: userMessage };
    messages.push(userMsg);

    try {
      const response = await this.callAPI(messages);
      return response;
    } catch (e) {
      return 'AI 请求失败: ' + JSON.stringify(e);
    }
  }

  /**
   * 实际 HTTP 调用（可替换后端）
   */
  private async callAPI(messages: AIMessage[]): Promise<string> {
    const body: string = JSON.stringify({
      model: this.backend.model,
      messages: messages,
      max_tokens: 2048,
      temperature: 0.7
    });

    const httpReq = http.createHttp();
    const resp = await httpReq.request(this.backend.apiUrl, {
      method: http.RequestMethod.POST,
      header: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + this.backend.apiKey },
      extraData: body,
      connectTimeout: 30000,
      readTimeout: 60000
    });

    const resultStr: string = (resp.result as string);
    httpReq.destroy();

    const data = JSON.parse(resultStr) as Record<string, Object>;
    const choices = data['choices'] as Array<Record<string, Object>>;
    if (choices && choices.length > 0) {
      const msg = choices[0]['message'] as Record<string, Object>;
      return (msg['content'] as string) ?? 'AI 返回为空';
    }
    return 'AI 返回异常: ' + resultStr.substring(0, 200);
  }

  // ─── 辅助方法：从 AI 回答中提取卡片建议 ─────────

  /**
   * 尝试从 AI 回答文本中提取 JSON 格式的卡片建议
   */
  extractCardSuggestions(response: string, defaultChainId: string): CardSuggestion[] {
    try {
      // 尝试匹配 JSON 数组
      const match: RegExpMatchArray | null = response.match(/\[[\s\S]*?\{[\s\S]*?"front"[\s\S]*?"back_core"[\s\S]*?\}[\s\S]*?\]/);
      if (match) {
        const arr: Object[] = JSON.parse(match[0]) as Object[];
        if (Array.isArray(arr)) {
          const result: CardSuggestion[] = [];
          for (const item of arr) {
            const obj: Record<string, string> = item as Record<string, string>;
            const suggestion: CardSuggestion = {
              front: obj.front ?? '',
              back_core: obj.back_core ?? '',
              chain_id: obj.chain_id ?? defaultChainId,
              card_type: (obj.card_type as CardType) ?? CardType.NODE
            };
            result.push(suggestion);
          }
          return result;
        }
      }
    } catch (_) {
      // 解析失败，无卡片建议
    }
    return [];
  }
}

// 单例
export const ai = new AIService();
