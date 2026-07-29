/**
 * 入境 APP · AI 对话面板
 */

import { router } from '@kit.ArkUI';
import { ai } from '../service/AIService';
import { db } from '../service/DatabaseService';
import { getChainNarrative } from '../service/ImportService';
import { ChatMessage, Card, CardSuggestion, AIAction, CardType, Maturity, ChainRole } from '../model/DataModel';

interface MarkdownSegment {
  text: string
  bold: boolean
}

@Entry
@Component
struct AIPanelPage {
  @State chainId: string = '';
  @State cardId: string = '';
  @State messages: ChatMessage[] = [];
  @State inputText: string = '';
  @State isLoading: boolean = false;
  @State backendName: string = 'GLM';
  private scrollController: Scroller = new Scroller();

  aboutToAppear(): void {
    const params: Record<string, Object> = router.getParams() as Record<string, Object>;
    this.chainId = (params['chain_id'] as string) ?? '';
    this.cardId = (params['card_id'] as string) ?? '';
    const be = ai.getBackend();
    this.backendName = be.name;
    this.loadHistory();
  }

  async loadHistory(): Promise<void> {
    if (!this.chainId) return;
    const history = await db.getChatHistory(this.chainId, 20);
    this.messages = history.map((h) => {
      const msg: ChatMessage = {
        id: h.id,
        role: h.role as 'user' | 'assistant',
        content: h.content,
        timestamp: h.timestamp
      };
      return msg;
    });
  }

  async sendMessage(): Promise<void> {
    const text: string = this.inputText.trim();
    if (!text || this.isLoading) return;

    this.isLoading = true;
    const userMsg: ChatMessage = {
      id: 'msg_' + Date.now().toString(),
      role: 'user',
      content: text,
      timestamp: Date.now()
    };
    // Use reassignment to trigger @State reactivity
    this.messages = [...this.messages, userMsg];
    await db.saveChatMessage(userMsg.id, this.chainId, 'user', text);
    this.inputText = '';

    let card: Card | undefined;
    if (this.cardId) {
      card = await db.getCard(this.cardId) ?? undefined;
    }

    const level = ai.getDefaultLevel(AIAction.QA);
    const context: string = await ai.buildContext(level, card, this.chainId);

    const historyMsgs: ChatMessage[] = this.messages
      .filter((m: ChatMessage) => m.id !== userMsg.id)
      .slice(-10);

    let response: string;
    try {
      response = await ai.sendMessage(AIAction.QA, text, context, historyMsgs);
    } catch (e) {
      response = 'AI 请求失败。请检查：是否已配置 API Key（rawfile/zhipu_api.txt），网络是否可用。错误: ' + JSON.stringify(e);
    }

    const aiMsg: ChatMessage = {
      id: 'msg_' + (Date.now() + 1).toString(),
      role: 'assistant',
      content: response,
      timestamp: Date.now()
    };
    this.messages = [...this.messages, aiMsg];
    await db.saveChatMessage(aiMsg.id, this.chainId, 'assistant', response);

    this.isLoading = false;

    setTimeout(() => {
      this.scrollController.scrollEdge(Edge.Bottom);
    }, 100);
  }

  async convertToCards(message: ChatMessage): Promise<void> {
    if (message.role !== 'assistant') return;

    const suggestions: CardSuggestion[] = ai.extractCardSuggestions(message.content, this.chainId);

    if (suggestions.length === 0) {
      const ctx: string = await ai.buildContext(
        ai.getDefaultLevel(AIAction.ANSWER_TO_CARD),
        undefined,
        this.chainId
      );
      const resp: string = await ai.sendMessage(
        AIAction.ANSWER_TO_CARD,
        '请从以下内容中提取关键知识点作为卡片：\n' + message.content,
        ctx,
        []
      );
      const retry: CardSuggestion[] = ai.extractCardSuggestions(resp, this.chainId);
      if (retry.length > 0) {
        await this.saveCards(retry);
      }
    } else {
      await this.saveCards(suggestions);
    }
  }

  async saveCards(suggestions: CardSuggestion[]): Promise<void> {
    for (const s of suggestions) {
      const card: Card = {
        card_id: 'AI_' + Date.now().toString() + '_' + Math.random().toString(36).slice(2, 6),
        chain_id: s.chain_id !== '' ? s.chain_id : this.chainId,
        chain_title: '',
        card_type: s.card_type,
        chain_role: ChainRole.PROCESS,
        front: s.front,
        back_core: s.back_core,
        back_detail: '',
        maturity: Maturity.RAW,
        tags: ['#AI生成'],
        is_new: true,
        last_marked: 0
      };
      await db.upsertCard(card);
    }
    await db.recalcChainCounts(this.chainId);
  }

  build() {
    Column() {
      Row() {
        Image($r('app.media.startIcon'))
          .width(20).height(20).fillColor('#333')
          .onClick(() => router.back())
        Text('AI ' + this.backendName)
          .fontSize(16).fontWeight(500).fontColor('#1a1a1a')
          .layoutWeight(1).margin({ left: 8 })
        Text('清空')
          .fontSize(11).fontColor('#999')
          .onClick(async () => {
            await db.clearChatHistory(this.chainId);
            this.messages = [];
          })
      }
      .width('100%').padding(14)

      List({ scroller: this.scrollController }) {
        ForEach(this.messages, (msg: ChatMessage) => {
          ListItem() {
            Column() {
              Row() {
                Text(msg.role === 'user' ? '你' : 'AI')
                  .fontSize(12).fontColor(msg.role === 'user' ? '#3B82B0' : '#5B8C5A')
                  .fontWeight(600)
                Blank()
                if (msg.role === 'assistant') {
                  Text('转卡片')
                    .fontSize(11).fontColor('#5B8C5A')
                    .padding({ left: 8, right: 8, top: 2, bottom: 2 })
                    .border({ width: 1, color: '#5B8C5A', radius: 8 })
                    .onClick(() => this.convertToCards(msg))
                }
              }
              .width('100%').margin({ bottom: 6 })

              // 解析 **bold** 标记并渲染
              if (msg.role === 'assistant' && msg.content.includes('**')) {
                this.markdownText(msg.content)
              } else {
                Text(msg.content)
                  .fontSize(14).fontColor('#333')
                  .lineHeight(22)
                  .textAlign(TextAlign.Start)
                  .width('100%')
              }
            }
            .padding(14)
            .backgroundColor(msg.role === 'user' ? '#f0f7ff' : Color.White)
            .borderRadius(12)
            .width('94%')
            .margin({ bottom: 8, left: 12, right: 12 })
          }
        })

        if (this.isLoading) {
          ListItem() {
            Row() {
              LoadingProgress().width(16).height(16)
              Text('...').fontSize(13).fontColor('#aaa').margin({ left: 8 })
            }
            .padding(14).margin({ left: 16 })
          }
        }
      }
      .layoutWeight(1)
      .padding({ top: 8 })

      Row() {
        TextInput({ placeholder: '对当前知识链提问...', text: this.inputText })
          .fontSize(14)
          .layoutWeight(1)
          .backgroundColor('#f0f0f0')
          .borderRadius(20)
          .padding({ left: 16, right: 16 })
          .height(40)
          .onChange((v: string) => { this.inputText = v; })
          .onSubmit(() => { this.sendMessage(); })

        Button('发送')
          .fontSize(13)
          .backgroundColor('#5B8C5A')
          .borderRadius(20)
          .height(36)
          .width(56)
          .margin({ left: 8 })
          .enabled(!this.isLoading && this.inputText.trim().length > 0)
          .onClick(() => this.sendMessage())
      }
      .width('100%')
      .padding({ left: 16, right: 16, bottom: 20, top: 12 })
      .backgroundColor(Color.White)
    }
    .width('100%').height('100%')
    .backgroundColor('#F5F5F5')
  }

  @Builder
  markdownText(content: string) {
    Text() {
      ForEach(this.parseMarkdown(content), (seg: MarkdownSegment) => {
        Span(seg.text)
          .fontSize(14)
          .fontColor(seg.bold ? '#1a1a1a' : '#333')
          .fontWeight(seg.bold ? 700 : 400)
      })
    }
    .fontSize(14)
    .lineHeight(22)
    .textAlign(TextAlign.Start)
    .width('100%')
  }

  parseMarkdown(content: string): MarkdownSegment[] {
    const result: MarkdownSegment[] = [];
    const parts = content.split('**');
    for (let i = 0; i < parts.length; i++) {
      if (parts[i].length > 0) {
        result.push({ text: parts[i], bold: i % 2 === 1 });
      }
    }
    return result;
  }}
