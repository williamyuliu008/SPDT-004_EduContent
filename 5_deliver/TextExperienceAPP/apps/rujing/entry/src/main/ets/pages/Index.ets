/**
 * 入境 APP · 首页仪表盘
 * 显示学习概况：总卡片/生熟比/学科分布
 */

import { router } from '@kit.ArkUI';
import { db } from '../service/DatabaseService';

@Entry
@Component
struct Index {
  @State totalCards: number = 0;
  @State totalChains: number = 0;
  @State rawCount: number = 0;
  @State cookedCount: number = 0;
  @State loading: boolean = true;

  aboutToAppear(): void {
    this.loadStats();
  }

  async loadStats(): Promise<void> {
    try {
      const stats = await db.getDashboardStats();
      this.totalCards = stats.total_cards;
      this.totalChains = stats.total_chains;
      this.rawCount = stats.raw_count;
      this.cookedCount = stats.cooked_count;
    } catch (_) {}
    this.loading = false;
  }

  build() {
    Column() {
      // 顶部
      Row() {
        Text('入境')
          .fontSize(28)
          .fontWeight(700)
          .fontColor('#1a1a1a')
        Blank()
        Text('导入')
          .fontSize(14)
          .fontColor('#5B8C5A')
          .onClick(() => {
            router.pushUrl({ url: 'pages/ImportPage' });
          })
      }
      .width('100%')
      .padding({ left: 20, right: 20, top: 12 })

      if (this.loading) {
        LoadingProgress()
          .width(36)
          .height(36)
          .margin({ top: 80 })
      } else if (this.totalCards === 0) {
        // 空状态
        Column({ space: 16 }) {
          Text('📭')
            .fontSize(48)
          Text('还没有知识卡片')
            .fontSize(16)
            .fontColor('#888')
          Text('点击右上角"导入"按钮，从 PT-038 导入卡片包')
            .fontSize(13)
            .fontColor('#aaa')
            .textAlign(TextAlign.Center)
            .width('80%')
          Button('开始导入')
            .onClick(() => {
              router.pushUrl({ url: 'pages/ImportPage' });
            })
        }
        .width('100%')
        .margin({ top: 100 })
      } else {
        Scroll() {
          Column({ space: 16 }) {
            // 统计卡片
            Row({ space: 12 }) {
              this.statCard('总卡片', this.totalCards.toString())
              this.statCard('待复习', this.rawCount.toString())
              this.statCard('已掌握', this.cookedCount.toString())
            }
            .width('100%')
            .padding({ left: 20, right: 20 })

            // 掌握进度条
            Column() {
              Row() {
                Text('掌握进度')
                  .fontSize(14)
                  .fontColor('#555')
                Blank()
                Text(this.cookedCount.toString() + ' / ' + this.totalCards.toString())
                  .fontSize(14)
                  .fontWeight(500)
                  .fontColor('#5B8C5A')
              }
              .width('100%')
              .margin({ bottom: 8 })

              Progress({
                value: this.totalCards > 0 ? this.cookedCount / this.totalCards * 100 : 0,
                total: 100,
                type: ProgressType.Linear
              })
                .color('#5B8C5A')
                .width('100%')
                .height(8)
                .style({ strokeWidth: 8, strokeRadius: 4 })
            }
            .width('100%')
            .padding(20)
            .backgroundColor(Color.White)
            .borderRadius(12)
            .margin({ left: 20, right: 20 })

            // 学科入口
            Text('学科')
              .fontSize(16)
              .fontWeight(600)
              .alignSelf(ItemAlign.Start)
              .padding({ left: 20 })

            this.subjectEntry('历史', '历史', '#C44536', '历史剧本链')
            this.subjectEntry('古诗文', '古诗文', '#8B4513', '高考古诗文通关')
            this.subjectEntry('书法', '书法', '#2D2D2D', '墨骨山河系列')
            this.subjectEntry('地理', '地理', '#5B8C5A', '地理山河系列')
            this.subjectEntry('政治', '政治', '#3B82B0', '即将上线')

            // ── 临帖专区 ──────────────────────────────
            Text('临帖实践')
              .fontSize(16)
              .fontWeight(600)
              .alignSelf(ItemAlign.Start)
              .padding({ left: 20, top: 12 })

            Row() {
              Column() {
                Text('🖌')
                  .fontSize(28)
                Text('临帖')
                  .fontSize(16)
                  .fontWeight(600)
                  .fontColor('#c0392b')
                Text('描红 + 自由临摹')
                  .fontSize(12)
                  .fontColor('#888')
                  .margin({ top: 2 })
              }
              .alignItems(HorizontalAlign.Center)
              .layoutWeight(1)
              .padding(12)
              .backgroundColor('#fff5f5')
              .borderRadius(12)
              .border({ width: 1, color: '#ffcccc' })
              .onClick(() => {
                router.pushUrl({ url: 'pages/LintingPage' });
              })

              Column() {
                Text('📖')
                  .fontSize(28)
                Text('AI 问答')
                  .fontSize(16)
                  .fontWeight(600)
                  .fontColor('#4a6cf7')
                Text('书法史论助手')
                  .fontSize(12)
                  .fontColor('#888')
                  .margin({ top: 2 })
              }
              .alignItems(HorizontalAlign.Center)
              .layoutWeight(1)
              .padding(12)
              .backgroundColor('#f0f4ff')
              .borderRadius(12)
              .border({ width: 1, color: '#c0d0ff' })
              .onClick(() => {
                router.pushUrl({ url: 'pages/AIPanelPage' });
              })

              Column() {
                Text('📜')
                  .fontSize(28)
                Text('辨析卡')
                  .fontSize(16)
                  .fontWeight(600)
                  .fontColor('#1A0E08')
                Text('5张风格对照')
                  .fontSize(12)
                  .fontColor('#888')
                  .margin({ top: 2 })
              }
              .alignItems(HorizontalAlign.Center)
              .layoutWeight(1)
              .padding(12)
              .backgroundColor('#F5EDD8')
              .borderRadius(12)
              .border({ width: 1, color: '#D4B87A' })
              .onClick(() => {
                router.pushUrl({ url: 'pages/CalligraphyComparePage' });
              })

              Column() {
                Text('🏛')
                  .fontSize(28)
                Text('历史配图')
                  .fontSize(16)
                  .fontWeight(600)
                  .fontColor('#C44536')
                Text('ep09 商鞅变法')
                  .fontSize(12)
                  .fontColor('#888')
                  .margin({ top: 2 })
              }
              .alignItems(HorizontalAlign.Center)
              .layoutWeight(1)
              .padding(12)
              .backgroundColor('#fff5f5')
              .borderRadius(12)
              .border({ width: 1, color: '#ffcccc' })
              .onClick(() => {
                router.pushUrl({ url: 'pages/HistoryGalleryPage' });
              })
            }
            .width('100%')
            .margin({ left: 20, right: 20 })
            .padding({ left: 20, right: 20 })
          }
        }
        .layoutWeight(1)
        .scrollBar(BarState.Off)
      }
    }
    .width('100%')
    .height('100%')
    .backgroundColor('#F5F5F5')
  }

  @Builder
  statCard(label: string, value: string) {
    Column() {
      Text(value)
        .fontSize(24)
        .fontWeight(700)
        .fontColor('#1a1a1a')
      Text(label)
        .fontSize(12)
        .fontColor('#999')
        .margin({ top: 4 })
    }
    .width('30%')
    .padding(16)
    .backgroundColor(Color.White)
    .borderRadius(12)
  }

  @Builder
  subjectEntry(name: string, subject: string, color: string, desc: string) {
    Row() {
      Column() {
        Text(name)
          .fontSize(16)
          .fontWeight(600)
          .fontColor('#1a1a1a')
        Text(desc)
          .fontSize(12)
          .fontColor('#999')
          .margin({ top: 2 })
      }
      .alignItems(HorizontalAlign.Start)

      Blank()

      Image($r('app.media.startIcon'))
        .width(16)
        .height(16)
        .fillColor('#ccc')
    }
    .width('100%')
    .padding(16)
    .backgroundColor(Color.White)
    .borderRadius(12)
    .border({ width: { left: 3 }, color: color })
    .margin({ left: 20, right: 20 })
    .onClick(() => {
      router.pushUrl({
        url: 'pages/ChainListPage',
        params: { subject: subject }
      });
    })
  }
}
