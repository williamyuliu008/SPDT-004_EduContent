/**
 * Index.ets — 静·闪卡
 */
import { HNavBar } from '../common';
import { AppConfig } from '../app.config';

interface CardItem { id: string; front: string; back: string; }
interface CardGroup { id: string; name: string; cardCount: number; dueCount: number; }

@Entry
@Component
struct Index {
  @State page: string = 'home';
  @State title: string = AppConfig.appName;
  // 卡组数据
  @State groups: CardGroup[] = [
    { id: '1', name: '鸿蒙 ArkTS 核心概念', cardCount: 12, dueCount: 5 },
    { id: '2', name: '英语四级词汇', cardCount: 200, dueCount: 23 },
    { id: '3', name: '设计模式速查', cardCount: 23, dueCount: 0 }
  ];
  // 复习模式
  @State reviewGroupId: string = '';
  @State reviewGroupName: string = '';
  @State reviewCards: CardItem[] = [];
  @State reviewIndex: number = 0;
  @State showBack: boolean = false;
  @State reviewDone: boolean = false;

  private sampleCards: Record<string, CardItem[]> = {
    '1': [
      { id: '1a', front: 'ArkTS 是什么？', back: 'ArkTS 是 HarmonyOS 生态的应用开发语言，基于 TypeScript 扩展，提供了声明式 UI、状态管理等能力。' },
      { id: '1b', front: '@State 装饰器的作用？', back: '@State 装饰的变量变化时，会触发所在组件的 build 方法重新执行，实现 UI 自动更新。' },
      { id: '1c', front: 'Stage 模型 vs FA 模型', back: 'Stage 模型是 HarmonyOS NEXT 推荐的开发模型，支持多窗口、跨设备迁移，FA 模型已逐步废弃。' }
    ],
    '2': [
      { id: '2a', front: 'abandon', back: 'v. 放弃；抛弃' },
      { id: '2b', front: 'brilliant', back: 'adj. 杰出的；明亮的' }
    ]
  };

  private navTo(p: string, t: string): void { this.page = p; this.title = t; }

  private startReview(g: CardGroup): void {
    this.reviewGroupId = g.id; this.reviewGroupName = g.name;
    this.reviewCards = this.sampleCards[g.id] ?? [];
    this.reviewIndex = 0; this.showBack = false; this.reviewDone = false;
    this.navTo('review', g.name);
  }

  private flipCard(): void { this.showBack = !this.showBack; }

  private rateCard(q: number): void {
    this.showBack = false;
    if (this.reviewIndex < this.reviewCards.length - 1) { this.reviewIndex++; }
    else { this.reviewDone = true; }
  }

  build() {
    Column() {
      HNavBar({ title: this.title, showBack: this.page !== 'home', navBgColor: AppConfig.primaryColor, onBack: (): void => { this.page = 'home'; this.title = AppConfig.appName; } })

      if (this.page === 'home') {
        List({ space: 12 }) {
          ForEach(this.groups, (g: CardGroup) => {
            ListItem() {
              Row() {
                Column() {
                  Text(g.name).fontSize(17).fontWeight(600).fontColor('#1C1C1E')
                  Text(g.cardCount + ' 张卡片').fontSize(13).fontColor('#888')
                  if (g.dueCount > 0) { Text(g.dueCount + ' 张待复习').fontSize(12).fontColor(AppConfig.primaryColor).margin({ top: 2 }) }
                }.alignItems(HorizontalAlign.Start).layoutWeight(1)
                Button('开始复习').fontSize(14).height(36).backgroundColor(AppConfig.primaryColor).borderRadius(8)
                  .onClick((): void => this.startReview(g))
              }.width('100%').padding(16).backgroundColor('#FFFFFF').borderRadius(12)
            }
          }, (g: CardGroup): string => g.id)
        }.width('100%').layoutWeight(1).padding(16).backgroundColor('#F5F5F5')
      }

      else if (this.page === 'review') {
        Column() {
          if (this.reviewDone) {
            Column() {
              Text('🎉').fontSize(48)
              Text('复习完成！').fontSize(24).fontWeight(700).fontColor('#1C1C1E').margin({ top: 12 })
              Text('已复习 ' + this.reviewCards.length + ' 张卡片').fontSize(16).fontColor('#888').margin({ top: 8 })
              Button('返回首页').fontSize(15).margin({ top: 24 }).onClick((): void => { this.page = 'home'; this.title = AppConfig.appName; })
            }.width('100%').layoutWeight(1).justifyContent(FlexAlign.Center)
          } else if (this.reviewCards.length > 0) {
            Column() {
              Text((this.reviewIndex + 1) + ' / ' + this.reviewCards.length).fontSize(14).fontColor('#888').margin({ top: 8, bottom: 16 })
              // 卡片
              Column() {
                Text(this.reviewCards[this.reviewIndex].front).fontSize(20).fontWeight(600).fontColor('#1C1C1E').textAlign(TextAlign.Center).width('100%').padding(24)
                if (this.showBack) {
                  Text(this.reviewCards[this.reviewIndex].back).fontSize(16).fontColor('#555').textAlign(TextAlign.Center).width('100%').padding({ left: 24, right: 24, bottom: 24 })
                } else {
                  Text('点击下方按钮查看答案').fontSize(14).fontColor('#AAA').padding(16)
                }
              }.width('90%').backgroundColor('#FFFFFF').borderRadius(16).shadow({ radius: 8, color: '#00000010', offsetX: 0, offsetY: 2 }).onClick((): void => this.flipCard())

              if (this.showBack) {
                Row({ space: 8 }) {
                  Button('忘记').fontSize(14).layoutWeight(1).height(44).backgroundColor('#FF3B30').borderRadius(8).onClick((): void => this.rateCard(0))
                  Button('困难').fontSize(14).layoutWeight(1).height(44).backgroundColor('#FF9500').borderRadius(8).onClick((): void => this.rateCard(3))
                  Button('良好').fontSize(14).layoutWeight(1).height(44).backgroundColor('#34C759').borderRadius(8).onClick((): void => this.rateCard(4))
                  Button('简单').fontSize(14).layoutWeight(1).height(44).backgroundColor('#007AFF').borderRadius(8).onClick((): void => this.rateCard(5))
                }.width('90%').margin({ top: 16 })
              } else {
                Button('翻转查看答案').fontSize(16).width('80%').height(48).backgroundColor(AppConfig.primaryColor).borderRadius(8).margin({ top: 16 }).onClick((): void => this.flipCard())
              }
            }.width('100%').layoutWeight(1).justifyContent(FlexAlign.Center).padding(16)
          } else {
            Column() {
              Text('暂无卡片').fontSize(18).fontColor('#888')
              Text('点击左上角返回').fontSize(14).fontColor('#AAA').margin({ top: 8 })
            }.width('100%').layoutWeight(1).justifyContent(FlexAlign.Center)
          }
        }.width('100%').layoutWeight(1).backgroundColor('#F5F5F5')
      }
    }.width('100%').height('100%')
  }
}
