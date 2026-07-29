/**
 * Index.ets — 学习教练 (thinkkit-coach) + Agent v2.1
 * Phase 2: common/agent-core 共享模块验证
 */
import { AppConfig } from '../app.config';
import { MOCK_KNOWLEDGE_TREE, KpNode, MOCK_PLAN, StudyTask, MOCK_DASHBOARD, CoachDashboard, generateFlashCards, FlashCard } from '../mock/coach_data';
import { AgentEngine, Insight } from '../common/agent/index';

interface TabItem { id: string; label: string; icon: string; }

@Entry
@Component
struct Index {
  @State tab: string = 'dashboard';
  @State title: string = AppConfig.appName;
  // 知识全景
  @State kpExpanded: string = '';
  @State kpDetail: KpNode | null = null;
  // 闪卡
  @State fcList: FlashCard[] = [];
  @State fcIndex: number = 0;
  @State fcShowBack: boolean = false;
  @State fcKp: string = '';
  // 计划
  @State showWizard: boolean = false;
  @State wizardStep: number = 0;

  // Agent v2.1
  private agent: AgentEngine = new AgentEngine({
    appId: 'thinkkit-coach', lobsterBaseUrl: 'http://localhost:8848/api/v1',
    mockMode: true, dimensions: ['A','B','C','D','G']
  });
  @State agentInsights: Insight[] = [];

  private tabs: TabItem[] = [
    { id: 'dashboard', label: '仪表盘', icon: '📊' } as TabItem,
    { id: 'plan', label: '计划', icon: '📋' } as TabItem,
    { id: 'knowledge', label: '全景', icon: '🗺' } as TabItem,
    { id: 'settings', label: '设置', icon: '⚙' } as TabItem,
  ];

  private showCards(kp: string): void {
    this.fcKp = kp; this.fcList = generateFlashCards(kp); this.fcIndex = 0; this.fcShowBack = false;
    this.tab = 'flashcard'; this.title = kp + ' · 闪卡';
  }

  aboutToAppear(): void { this.agent.init(); }

  build() {
    Column() {
      // Header
      Row() {
        if (this.tab === 'flashcard') {
          Text('←').fontSize(20).fontColor('#FFFFFF').onClick((): void => { this.tab = 'knowledge'; this.title = AppConfig.appName; })
        }
        Text(this.title).fontSize(18).fontWeight(700).fontColor('#FFFFFF').margin({ left: this.tab === 'flashcard' ? 8 : 0 })
        Blank()
        Text('数学').fontSize(13).fontColor('#FFFFFF').opacity(0.8)
      }.width('100%').height(52).padding({ left: 16, right: 16 }).backgroundColor(AppConfig.primaryColor)

      if (this.tab === 'flashcard') {
        this.buildFlashCard()
      } else if (this.tab === 'dashboard') {
        this.buildDashboard()
      } else if (this.tab === 'plan') {
        this.buildPlan()
      } else if (this.tab === 'knowledge') {
        this.buildKnowledge()
      } else if (this.tab === 'settings') {
        this.buildSettings()
      }

      // Bottom tabs
      Row() {
        ForEach(this.tabs, (t: TabItem) => {
          Column({ space: 2 }) {
            Text(t.icon).fontSize(18)
            Text(t.label).fontSize(10).fontColor(this.tab === t.id ? AppConfig.primaryColor : '#999')
          }.layoutWeight(1).padding({ top: 8, bottom: 8 }).onClick((): void => { this.tab = t.id; this.title = AppConfig.appName; })
        }, (t: TabItem): string => t.id)
      }.width('100%').height(56).backgroundColor('#FFFFFF').border({ width: { top: 0.5 }, color: '#E5E5E5' })
    }.width('100%').height('100%')
  }

  // ==================== DASHBOARD ====================
  @Builder buildDashboard() {
    Scroll() {
      Column({ space: 12 }) {
        // KPI 卡片
        Row({ space: 8 }) {
          Column() { Text(MOCK_DASHBOARD.todayTasks.length.toString()).fontSize(28).fontWeight(700).fontColor('#1C1C1E'); Text('今日任务').fontSize(11).fontColor('#888') }.layoutWeight(1).padding(12).backgroundColor('#FFFFFF').borderRadius(10).alignItems(HorizontalAlign.Center)
          Column() { Text(MOCK_DASHBOARD.streak.toString()).fontSize(28).fontWeight(700).fontColor(AppConfig.primaryColor); Text('连续天数').fontSize(11).fontColor('#888') }.layoutWeight(1).padding(12).backgroundColor('#FFFFFF').borderRadius(10).alignItems(HorizontalAlign.Center)
          Column() { Text(MOCK_DASHBOARD.masteredKps + '/' + MOCK_DASHBOARD.totalKps).fontSize(28).fontWeight(700).fontColor('#F59E0B'); Text('已掌握').fontSize(11).fontColor('#888') }.layoutWeight(1).padding(12).backgroundColor('#FFFFFF').borderRadius(10).alignItems(HorizontalAlign.Center)
        }.width('100%')

        // 计划进度
        Column() {
          Row() { Text('📋 函数与导数 学习计划').fontSize(14).fontWeight(600).fontColor('#1C1C1E'); Blank(); Text(MOCK_DASHBOARD.planProgress + '%').fontSize(13).fontColor(AppConfig.primaryColor) }.width('100%').margin({ bottom: 8 })
          Row() { Row().width(MOCK_DASHBOARD.planProgress.toString() + '%').height(6).backgroundColor(AppConfig.primaryColor).borderRadius(3) }.width('100%').height(6).backgroundColor('#F0F0F0').borderRadius(3)
        }.width('100%').padding(14).backgroundColor('#FFFFFF').borderRadius(10)

        // 今日任务
        Column() {
          Text('📝 今日任务').fontSize(14).fontWeight(600).fontColor('#1C1C1E').margin({ bottom: 8 }).alignSelf(ItemAlign.Start)
          ForEach(MOCK_DASHBOARD.todayTasks, (t: StudyTask) => {
            Row() {
              Text(t.completed ? '☑' : '☐').fontSize(18).fontColor(t.completed ? AppConfig.primaryColor : '#CCC')
              Column() { Text(t.kp).fontSize(14).fontColor('#1C1C1E'); Text(['', '模板学习', '闪卡复习', '凌空刷题', '章节检测'][['', 'template', 'flashcard', 'lingkong', 'review'].indexOf(t.type)] ?? '任务').fontSize(11).fontColor('#888') }.alignItems(HorizontalAlign.Start).margin({ left: 10 }).layoutWeight(1)
            }.width('100%').padding({ top: 8, bottom: 8 })
          }, (t: StudyTask, i: number): string => i.toString())
        }.width('100%').padding(14).backgroundColor('#FFFFFF').borderRadius(10)

        // 本周活动
        Column() {
          Text('📈 本周学习').fontSize(14).fontWeight(600).fontColor('#1C1C1E').margin({ bottom: 8 }).alignSelf(ItemAlign.Start)
          Row({ space: 2 }) {
            ForEach(MOCK_DASHBOARD.weekActivity, (v: number, i: number) => {
              Column() { Text(v > 0 ? v.toString() : '').fontSize(9).fontColor('#888'); Row().width('100%').height(Math.max(4, v * 8)).backgroundColor(AppConfig.primaryColor).borderRadius({ topLeft: 2, topRight: 2 }) }.layoutWeight(1).alignItems(HorizontalAlign.Center).justifyContent(FlexAlign.End)
            }, (v: number, i: number): string => i.toString())
          }.width('100%').height(60)
        }.width('100%').padding(14).backgroundColor('#FFFFFF').borderRadius(10)
      }.width('100%').padding(16).padding({ bottom: 24 })
    }.layoutWeight(1).backgroundColor('#F1F5F0')
  }

  // ==================== PLAN ====================
  @Builder buildPlan() {
    Scroll() {
      Column({ space: 12 }) {
        if (this.showWizard) {
          Column({ space: 12 }) {
            Text('🎯 新建学习计划').fontSize(18).fontWeight(700).fontColor('#1C1C1E')
            Text('告诉我你想提高什么，我来帮你规划').fontSize(13).fontColor('#888')
            // Step 1: 选目标
            if (this.wizardStep === 0) {
              Text('Step 1: 选择目标板块').fontSize(14).fontWeight(600).fontColor(AppConfig.primaryColor)
              Flex({ wrap: FlexWrap.Wrap }) {
                ForEach(['函数与导数', '解析几何', '数列', '概率统计', '三角函数', '立体几何', '向量', '不等式'], (kp: string) => {
                  Text(kp).fontSize(13).padding({ left: 12, right: 12, top: 6, bottom: 6 }).border({ width: 1, color: '#DCDCDC' }).borderRadius(16).margin({ right: 8, bottom: 8 })
                }, (s: string): string => s)
              }
              Button('下一步 →').fontSize(15).width('100%').height(44).margin({ top: 12 }).backgroundColor(AppConfig.primaryColor).borderRadius(10).onClick((): void => { this.wizardStep = 1; })
            }
            // Step 2: 预览计划
            else if (this.wizardStep === 1) {
              Text('Step 2: Agent 生成计划').fontSize(14).fontWeight(600).fontColor(AppConfig.primaryColor)
              Column() {
                Row() { Text('目标').fontSize(13).fontColor('#888'); Text('函数与导数').fontSize(14).fontColor('#1C1C1E').margin({ left: 8 }) }.width('100%').margin({ bottom: 4 })
                Row() { Text('周期').fontSize(13).fontColor('#888'); Text('14 天 · 每天40分钟').fontSize(14).fontColor('#1C1C1E').margin({ left: 8 }) }.width('100%').margin({ bottom: 4 })
                Row() { Text('考点').fontSize(13).fontColor('#888'); Text('4 个考点 · 18 个子考点').fontSize(14).fontColor('#1C1C1E').margin({ left: 8 }) }.width('100%')
              }.width('100%').padding(14).backgroundColor('#FFFFFF').borderRadius(10)
              Button('确认开始').fontSize(15).width('100%').height(44).margin({ top: 12 }).backgroundColor(AppConfig.primaryColor).borderRadius(10).onClick((): void => { this.showWizard = false; })
            }
          }.width('100%').padding(16).backgroundColor('#FFFFFF').borderRadius(12)
        } else {
          // 当前计划
          Column() {
            Row() { Text('📋 ' + MOCK_PLAN.goal).fontSize(16).fontWeight(600).fontColor('#1C1C1E'); Blank(); Text('进行中').fontSize(11).fontColor(AppConfig.primaryColor).padding({ left: 6, right: 6, top: 2, bottom: 2 }).backgroundColor(AppConfig.primaryColor + '15').borderRadius(8) }.width('100%')
            Text(MOCK_PLAN.durationDays + '天计划 · 每日' + MOCK_PLAN.dailyMinutes + '分钟').fontSize(13).fontColor('#888').margin({ top: 4 })
            Row() { Row().width((MOCK_PLAN.tasks.filter((t: StudyTask) => t.completed).length / MOCK_PLAN.tasks.length * 100).toString() + '%').height(6).backgroundColor(AppConfig.primaryColor).borderRadius(3) }.width('100%').height(6).backgroundColor('#F0F0F0').borderRadius(3).margin({ top: 8 })
          }.width('100%').padding(14).backgroundColor('#FFFFFF').borderRadius(10)
          // 任务列表
          ForEach(MOCK_PLAN.tasks, (t: StudyTask) => {
            Row() {
              Text(t.completed ? '✅' : '⬜').fontSize(16)
              Column() { Text('Day ' + t.day + ' · ' + t.kp).fontSize(14).fontColor('#1C1C1E'); Text(['', '模板学习', '闪卡复习', '凌空刷题', '章节检测'][['', 'template', 'flashcard', 'lingkong', 'review'].indexOf(t.type)] ?? '').fontSize(11).fontColor('#888') }.alignItems(HorizontalAlign.Start).margin({ left: 10 }).layoutWeight(1)
            }.width('100%').padding(12).backgroundColor('#FFFFFF').borderRadius(8)
          }, (t: StudyTask, i: number): string => i.toString())
          Button('+ 新建计划').fontSize(15).width('100%').height(44).margin({ top: 8 }).backgroundColor(AppConfig.primaryColor).borderRadius(10).onClick((): void => { this.showWizard = true; this.wizardStep = 0; })
        }
      }.width('100%').padding(16).padding({ bottom: 24 })
    }.layoutWeight(1).backgroundColor('#F1F5F0')
  }

  // ==================== KNOWLEDGE ====================
  @Builder buildKnowledge() {
    Scroll() {
      Column({ space: 8 }) {
        Text('知识全景').fontSize(18).fontWeight(700).fontColor('#1C1C1E')
        Text('点击板块展开考点，点击考点生成闪卡').fontSize(13).fontColor('#888')
        ForEach(MOCK_KNOWLEDGE_TREE, (node: KpNode, idx: number) => {
          Column({ space: 4 }) {
            // L1 板块
            Row() {
              Text(node.name).fontSize(15).fontWeight(600).fontColor('#1C1C1E')
              Blank()
              Text(node.mastery + '%').fontSize(14).fontWeight(700).fontColor(node.mastery >= 70 ? '#34D399' : node.mastery >= 40 ? '#FBBF24' : '#F87171')
            }.width('100%').padding(12).backgroundColor('#FFFFFF').borderRadius(10)
            .onClick((): void => { this.kpExpanded = this.kpExpanded === node.name ? '' : node.name; this.kpDetail = null; })
            // 进度条
            Row() { Row().width(node.mastery.toString() + '%').height(4).backgroundColor(node.mastery >= 70 ? '#34D399' : node.mastery >= 40 ? '#FBBF24' : '#F87171').borderRadius(2) }.width('100%').height(4).backgroundColor('#F0F0F0').borderRadius(2)
            // L2/L3 子考点
            if (this.kpExpanded === node.name) {
              ForEach(node.children, (child: KpNode) => {
                Column() {
                  Row() {
                    Text('  ' + child.name).fontSize(13).fontColor('#555').layoutWeight(1)
                    Text(child.mastery + '%').fontSize(12).fontWeight(600).fontColor(child.mastery >= 70 ? '#34D399' : '#F87171')
                    Text('🃏').fontSize(14).margin({ left: 8 }).onClick((): void => this.showCards(child.name))
                  }.width('100%').padding({ top: 6, bottom: 6 })
                  if (child.children.length > 0) {
                    ForEach(child.children, (sub: KpNode) => {
                      Row() {
                        Text('    ' + sub.name).fontSize(12).fontColor('#888').layoutWeight(1)
                        Text(sub.mastery + '%').fontSize(11).fontColor(sub.mastery >= 70 ? '#34D399' : '#F87171')
                      }.width('100%').padding({ top: 3, bottom: 3 })
                    }, (s: KpNode): string => s.name)
                  }
                  // 陷阱提示
                  if (child.classicTrap) {
                    Text('⚠ ' + (child.classicTrap ?? '')).fontSize(11).fontColor('#F59E0B').padding({ left: 16, top: 2, bottom: 4 })
                  }
                }.width('100%')
              }, (c: KpNode): string => c.name)
            }
          }.width('100%')
        }, (n: KpNode): string => n.name)
      }.width('100%').padding(16).padding({ bottom: 24 })
    }.layoutWeight(1).backgroundColor('#F1F5F0')
  }

  // ==================== FLASHCARD ====================
  @Builder buildFlashCard() {
    Column() {
      if (this.fcList.length > 0) {
        Column() {
          Text((this.fcIndex + 1) + ' / ' + this.fcList.length).fontSize(13).fontColor('#888').margin({ top: 8, bottom: 16 })
          // 卡片
          Column() {
            Text(this.fcList[this.fcIndex].front).fontSize(18).fontWeight(600).fontColor('#1C1C1E').textAlign(TextAlign.Center).width('100%').padding(32)
            if (this.fcShowBack) {
              Text(this.fcList[this.fcIndex].back).fontSize(15).fontColor('#555').textAlign(TextAlign.Center).width('100%').padding({ left: 24, right: 24, bottom: 24 })
            } else {
              Text('点击翻转查看答案').fontSize(14).fontColor('#AAA').padding(20)
            }
          }.width('88%').backgroundColor('#FFFFFF').borderRadius(16).shadow({ radius: 8, color: '#00000010', offsetX: 0, offsetY: 2 })
          .onClick((): void => { this.fcShowBack = !this.fcShowBack; })

          if (this.fcShowBack) {
            Row({ space: 12 }) {
              Button('忘记').fontSize(14).layoutWeight(1).height(40).backgroundColor('#F87171').borderRadius(8)
              Button('困难').fontSize(14).layoutWeight(1).height(40).backgroundColor('#FBBF24').borderRadius(8)
              Button('掌握').fontSize(14).layoutWeight(1).height(40).backgroundColor('#34D399').borderRadius(8)
              Button('简单').fontSize(14).layoutWeight(1).height(40).backgroundColor('#3B82F6').borderRadius(8)
            }.width('88%').margin({ top: 16 })
          } else {
            Button('翻转查看答案').fontSize(16).width('70%').height(48).margin({ top: 16 }).backgroundColor(AppConfig.primaryColor).borderRadius(8)
            .onClick((): void => { this.fcShowBack = !this.fcShowBack; })
          }
        }.width('100%').layoutWeight(1).justifyContent(FlexAlign.Center)
      } else {
        Column() {
          Text('暂无闪卡').fontSize(16).fontColor('#888')
        }.width('100%').layoutWeight(1).justifyContent(FlexAlign.Center)
      }
    }.width('100%').layoutWeight(1).backgroundColor('#F1F5F0')
  }

  // ==================== SETTINGS ====================
  @Builder buildSettings() {
    List({ space: 0 }) {
      ListItem() { Row() { Text('学科切换').fontSize(15).fontColor('#1C1C1E'); Blank(); Text('数学 ›').fontSize(13).fontColor('#888') }.width('100%').padding(16).backgroundColor('#FFFFFF') }
      ListItem() { Row() { Text('学习提醒').fontSize(15).fontColor('#1C1C1E'); Blank(); Text('每天 19:00 ›').fontSize(13).fontColor('#888') }.width('100%').padding(16).backgroundColor('#FFFFFF') }
      ListItem() { Row() { Text('数据导出').fontSize(15).fontColor('#1C1C1E'); Blank(); Text('›').fontSize(18).fontColor('#CCC') }.width('100%').padding(16).backgroundColor('#FFFFFF') }
      ListItem() { Row().width('100%').height(8).backgroundColor('#F1F5F0') }
      ListItem() { Row() { Text('关于').fontSize(15).fontColor('#1C1C1E'); Blank(); Text(AppConfig.appName + ' v1.0').fontSize(13).fontColor('#888') }.width('100%').padding(16).backgroundColor('#FFFFFF') }
    }.width('100%').layoutWeight(1).divider({ strokeWidth: 0.5, color: '#F0F0F0' })
  }
}
