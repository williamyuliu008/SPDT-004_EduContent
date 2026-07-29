/**
 * Index.ets — 律动习惯
 */
import { HNavBar } from '../common';
import { AppConfig } from '../app.config';

interface HabitItem { id: string; name: string; icon: string; color: string; streak: number; bestStreak: number; todayDone: boolean; totalDays: number; }

@Entry
@Component
struct Index {
  @State page: string = 'home';
  @State title: string = AppConfig.appName;
  @State habits: HabitItem[] = [
    { id: '1', name: '每日阅读', icon: '📖', color: '#5B8C5A', streak: 5, bestStreak: 12, todayDone: false, totalDays: 30 },
    { id: '2', name: '晨间冥想', icon: '🧘', color: '#7B68EE', streak: 3, bestStreak: 7, todayDone: true, totalDays: 15 },
    { id: '3', name: '健身 30 分钟', icon: '💪', color: '#FF6347', streak: 0, bestStreak: 21, todayDone: false, totalDays: 45 },
    { id: '4', name: '早睡 23:00', icon: '🌙', color: '#4A90D9', streak: 1, bestStreak: 5, todayDone: false, totalDays: 10 }
  ];
  @State selectedHabit: HabitItem | null = null;

  private navTo(p: string, t: string): void { this.page = p; this.title = t; }

  private toggleCheck(h: HabitItem): void { h.todayDone = !h.todayDone; if (h.todayDone) { h.streak++; h.totalDays++; if (h.streak > h.bestStreak) h.bestStreak = h.streak; } else { h.streak = Math.max(0, h.streak - 1); } }

  build() {
    Column() {
      HNavBar({ title: this.title, showBack: this.page !== 'home', navBgColor: AppConfig.primaryColor,
        onBack: (): void => { this.page = 'home'; this.title = AppConfig.appName; this.selectedHabit = null; } })

      if (this.page === 'home') {
        List({ space: 12 }) {
          ForEach(this.habits, (h: HabitItem) => {
            ListItem() {
              Column() {
                Row() {
                  Text(h.icon).fontSize(32)
                  Column() {
                    Text(h.name).fontSize(17).fontWeight(600).fontColor('#1C1C1E')
                    Text('连续 ' + h.streak + ' 天 · 最长 ' + h.bestStreak + ' 天').fontSize(13).fontColor('#888')
                  }.alignItems(HorizontalAlign.Start).layoutWeight(1).margin({ left: 14 })
                  Button(h.todayDone ? '✓ 已打卡' : '打卡').fontSize(13).height(32)
                    .backgroundColor(h.todayDone ? '#34C759' : AppConfig.primaryColor).borderRadius(16)
                    .onClick((): void => this.toggleCheck(h))
                }.width('100%')
                // 7 天进度条
                Row({ space: 3 }) {
                  ForEach([0, 1, 2, 3, 4, 5, 6], (day: number) => {
                    Row().width('12%').height(6).borderRadius(3).backgroundColor(day < h.streak % 7 ? h.color : '#E8E8E8')
                  }, (d: number): string => d.toString())
                }.width('100%').margin({ top: 12 })
              }.width('100%').padding(16).backgroundColor('#FFFFFF').borderRadius(12)
              .onClick((): void => { this.selectedHabit = h; this.navTo('detail', h.name); })
            }
          }, (h: HabitItem): string => h.id)
        }.width('100%').layoutWeight(1).padding(16).backgroundColor('#F5F5F5')
      }

      else if (this.page === 'detail' && this.selectedHabit) {
        Column() {
          Text(this.selectedHabit.icon).fontSize(64).margin({ top: 40 })
          Text(this.selectedHabit.name).fontSize(24).fontWeight(700).fontColor('#1C1C1E').margin({ top: 16 })
          Row({ space: 24 }) {
            Column() { Text(this.selectedHabit.streak.toString()).fontSize(36).fontWeight(700).fontColor(this.selectedHabit.color); Text('当前连续').fontSize(13).fontColor('#888') }
            Column() { Text(this.selectedHabit.bestStreak.toString()).fontSize(36).fontWeight(700).fontColor('#1C1C1E'); Text('最长记录').fontSize(13).fontColor('#888') }
            Column() { Text(this.selectedHabit.totalDays.toString()).fontSize(36).fontWeight(700).fontColor('#1C1C1E'); Text('总打卡').fontSize(13).fontColor('#888') }
          }.margin({ top: 24 })
          Button(this.selectedHabit.todayDone ? '✓ 今日已打卡' : '打卡').fontSize(16).width('60%').height(48).margin({ top: 32 })
            .backgroundColor(this.selectedHabit.todayDone ? '#34C759' : AppConfig.primaryColor).borderRadius(12)
            .onClick((): void => this.toggleCheck(this.selectedHabit!))
        }.width('100%').layoutWeight(1).backgroundColor('#F5F5F5')
      }
    }.width('100%').height('100%')
  }
}
