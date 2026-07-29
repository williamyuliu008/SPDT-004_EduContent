/**
 * Index.ets — GaokaoAgent V2 (G2 enhanced UI + Agent v2.1)
 * Phase 1A: 智能体维度 A+B+C+H 集成
 */
import { AppConfig } from '../app.config';
import { HRadarChart } from '../common/components/HRadarChart';
import { DomainProfile, DiagnosticQuestion, DiagnosticResult, TutoringQuestion, KnowledgeNode, DashboardData } from '../mock/data';
import { fetchDomains, fetchDiagnosticQuestions, submitDiagnostic, fetchTutoringQuestions, submitTutoring, TutorResult, fetchKnowledgeMap, fetchDashboard, getLastError } from '../services/api';
import { AgentProfile, IntentContext, InputAssist, EnvAwareness, OutputAction, LobsterClient, UndoManager, ActionRecord, PreSelection, ColdStartQuestion, ColdStartProgress, RecommendedAction, Insight } from '../common/agent/index';

type Tab = 'diagnostic' | 'tutoring' | 'knowledge' | 'dashboard' | 'subjects';
interface BoardScore { name: string; score: number; level: string; color: string; }
interface KnowledgeChild { name: string; mastery: number; type: string; }
interface WeakBoard { name: string; score: number; }
interface TabItem { id: Tab; label: string; icon: string; }
interface DiffTag { label: string; value: number; }
interface UndoAnswerPayload { questionId: string; answer: string; }

@Entry
@Component
struct Index {
  @State tab: Tab = 'diagnostic';
  @State loading: boolean = true;
  @State diagStep: number = 0;
  @State diagQuestions: DiagnosticQuestion[] = [];
  @State diagAnswers: number[] = [];
  @State diagResult: DiagnosticResult | null = null;
  @State diagCurrentQ: number = 0;
  @State tutorQuestions: TutoringQuestion[] = [];
  @State tutorFilteredQuestions: TutoringQuestion[] = [];
  @State tutorAnswer: string = '';
  @State tutorFeedback: string = '';
  @State tutorCorrect: boolean = false;
  @State tutorSubmitted: boolean = false;
  @State tutorCurrentQ: number = 0;
  @State tutorDiff: number = 0;
  @State tutorBoard: string = '';
  @State knowledgeNodes: KnowledgeNode[] = [];
  @State kmSelected: number = -1;
  @State dashData: DashboardData | null = null;
  @State domains: DomainProfile[] = [];
  @State selectedDomain: string = 'math';
  @State lobsterGenerating: boolean = false;
  @State lobsterQuestions: object[] = [];
  @State lobsterMode: boolean = false;

  // ---- Agent v2.1: 智能体维度 ----
  private agentProfile: AgentProfile = new AgentProfile();
  private agentIntent: IntentContext = new IntentContext();
  private agentInput: InputAssist = new InputAssist(this.agentProfile, this.agentIntent);
  private agentEnv: EnvAwareness = new EnvAwareness();
  private agentOutput: OutputAction = new OutputAction();
  private agentLobster: LobsterClient = new LobsterClient('http://localhost:8848/api/v1', true);
  private agentUndo: UndoManager = new UndoManager();
  @State insights: Insight[] = [];
  @State undoCount: number = 0;
  @State coldStartActive: boolean = false;
  @State coldStartQ: ColdStartQuestion | null = null;
  @State coldStartProgress: ColdStartProgress = { current: 0, total: 5 };
  @State coldStartFinished: boolean = false;
  @State agentActions: RecommendedAction[] = [];

  private tabs: TabItem[] = [
    { id: 'diagnostic', label: '诊断', icon: '🔍' } as TabItem,
    { id: 'tutoring', label: '刷题', icon: '✏️' } as TabItem,
    { id: 'knowledge', label: '地图', icon: '🗺' } as TabItem,
    { id: 'dashboard', label: '面板', icon: '📊' } as TabItem,
    { id: 'subjects', label: '学科', icon: '📚' } as TabItem,
  ];

  private diffTags: DiffTag[] = [
    { label: '全部', value: 0 } as DiffTag, { label: '★', value: 1 } as DiffTag,
    { label: '★★', value: 2 } as DiffTag, { label: '★★★', value: 3 } as DiffTag,
  ];

  aboutToAppear(): void {
    this.initAgent();
    this.loadTabData();
  }

  async initAgent(): Promise<void> {
    await this.agentProfile.init();
    // 恢复跨会话书签
    const bookmark = await this.agentIntent.restoreBookmark();
    if (bookmark !== null) {
      // 如果上次有未完成的冷启动，不恢复书签
      if (!this.agentProfile.isColdStartComplete()) {
        this.startColdStart();
      } else if (bookmark.lastTab && ['diagnostic','tutoring','knowledge','dashboard','subjects'].indexOf(bookmark.lastTab) >= 0) {
        this.tab = bookmark.lastTab as Tab;
      }
    }
    // 检查是否需要冷启动
    if (!this.agentProfile.isColdStartComplete() && !this.coldStartActive) {
      // 首次使用 → 稍后在诊断Tab中触发
    }
    // 环境感知
    this.agentEnv.onLowBattery(() => {
      console.info('[Agent] 低电量：暂停后台同步');
    });
    this.updateAgentActions();
  }

  startColdStart(): void {
    this.agentInput.startColdStartGuide();
    this.coldStartActive = true;
    this.coldStartFinished = false;
    this.coldStartQ = this.agentInput.getCurrentColdStartQuestion();
    this.coldStartProgress = this.agentInput.getColdStartProgress();
  }

  async updateAgentActions(): Promise<void> {
    this.agentActions = this.agentInput.getRecommendedActions();
    // 生成洞察 (D维度)
    const weaks = await this.agentProfile.getWeaknesses();
    const strongs = await this.agentProfile.getStrengths();
    const attr = this.agentProfile.getErrorAttribution();
    this.insights = this.agentOutput.generateInsights(weaks, strongs, attr.conceptual, attr.calculative, 0.6);
  }

  async loadTabData(): Promise<void> {
    this.loading = true;
    if (this.tab === 'diagnostic' && this.diagStep === 0) { const qs = await fetchDiagnosticQuestions(); this.diagQuestions = qs; }
    if (this.tab === 'tutoring') {
      const tqs = await fetchTutoringQuestions(); this.tutorQuestions = tqs; this.tutorFilteredQuestions = tqs;
      this.tutorSubmitted = false; this.tutorFeedback = ''; this.tutorDiff = 0; this.tutorBoard = '';
    }
    if (this.tab === 'knowledge') { const kn = await fetchKnowledgeMap(); this.knowledgeNodes = kn; }
    if (this.tab === 'dashboard') { const dd = await fetchDashboard(); this.dashData = dd; }
    if (this.tab === 'subjects') { const ds = await fetchDomains(); this.domains = ds; }
    this.loading = false;
  }

  switchTab(t: Tab): void {
    // 冷启动未完成 → 引导先完成
    if (!this.agentProfile.isColdStartComplete() && t !== 'diagnostic') {
      this.startColdStart();
      this.tab = 'diagnostic';
      return;
    }
    this.tab = t;
    this.agentIntent.setCurrentTab(t);
    this.updateAgentActions();
    this.loadTabData();
  }
  getDomainName(): string { for (let i = 0; i < this.domains.length; i++) { if (this.domains[i].id === this.selectedDomain) return this.domains[i].name; } return '数学'; }
  getStars(n: number): string { if (n <= 1) return '⭐'; if (n === 2) return '⭐⭐'; return '⭐⭐⭐'; }

  // 旧版诊断

  // 诊断
  selectDiagAnswer(idx: number): void {
    const a: number[] = []; for (let i = 0; i < this.diagAnswers.length; i++) a.push(this.diagAnswers[i]);
    a.push(idx); this.diagAnswers = a;
    if (this.diagCurrentQ < this.diagQuestions.length - 1) { this.diagCurrentQ++; }
    else { this.finishDiagnostic(); }
  }
  async finishDiagnostic(): Promise<void> { const r = await submitDiagnostic(this.diagAnswers); this.diagResult = r; this.diagStep = 2; }
  restartDiag(): void { this.diagStep = 0; this.diagCurrentQ = 0; this.diagAnswers = []; this.diagResult = null; this.diagQuestions = []; this.loadTabData(); }

  // 调用小龙虾生成练习集 (G维度)
  askLobster(): void {
    this.lobsterGenerating = true;
    this.agentLobster.generateQuestions('math', this.tutorDiff, 5).then((questions) => {
      this.lobsterQuestions = questions;
      this.lobsterMode = true;
      this.lobsterGenerating = false;
    });
  }

  // 退出小龙虾模式
  exitLobsterMode(): void {
    this.lobsterMode = false;
    this.lobsterQuestions = [];
  }
  filterTutorQuestions(): void {
    const result: TutoringQuestion[] = [];
    // Agent预选 (C维度)
    if (this.tutorDiff === 0 && this.tutorBoard === '') {
      const pre = this.agentInput.getPreSelection();
      if (pre.difficulty !== undefined) this.tutorDiff = pre.difficulty;
    }
    for (let i = 0; i < this.tutorQuestions.length; i++) {
      const q = this.tutorQuestions[i];
      const matchDiff = this.tutorDiff === 0 || q.difficulty === this.tutorDiff;
      const matchBoard = this.tutorBoard === '' || q.board === this.tutorBoard;
      if (matchDiff && matchBoard) { result.push(q); }
    }
    this.tutorFilteredQuestions = result;
    this.tutorCurrentQ = 0;
  }

  async submitTutor(): Promise<void> {
    if (!this.tutorAnswer.trim() || this.tutorFilteredQuestions.length === 0) return;
    const q: TutoringQuestion = this.tutorFilteredQuestions[this.tutorCurrentQ];
    const r: TutorResult = await submitTutoring(q.id, this.tutorAnswer);
    this.tutorCorrect = r.correct; this.tutorFeedback = r.feedback; this.tutorSubmitted = true;

    // Agent: 记录答题 (B维度)
    this.agentIntent.recordAction({
      action: 'answered_question',
      targetId: q.id,
      timestamp: new Date().toISOString(),
      durationMs: 0, // TODO: 计时
      result: r.correct ? 'correct' : 'wrong'
    });
    // Agent: 更新掌握度 (A维度)
    await this.agentProfile.updateMastery(q.board, r.correct, 0);
    if (!r.correct) {
      await this.agentProfile.recordError(q.board, 'conceptual');
    }
    // Agent: 记录可撤销操作 (I维度)
    const undoPayload: UndoAnswerPayload = { questionId: q.id, answer: this.tutorAnswer };
    this.agentUndo.recordAction('answer_question', undoPayload);
    this.undoCount = this.agentUndo.getCount();
    this.updateAgentActions();
  }
  nextTutorQ(): void {
    if (this.tutorCurrentQ < this.tutorFilteredQuestions.length - 1) { this.tutorCurrentQ++; this.tutorSubmitted = false; this.tutorFeedback = ''; this.tutorAnswer = ''; }
  }

  build() {
    Column() {
      Row() {
        Text(AppConfig.appName).fontSize(18).fontWeight(700).fontColor('#FFFFFF')
        Blank()
        Text(this.getDomainName()).fontSize(13).fontColor('#FFFFFF').opacity(0.8)
      }.width('100%').height(52).padding({ left: 16, right: 16 }).backgroundColor(AppConfig.primaryColor)

      if (this.loading) {
        Column() { LoadingProgress().width(36).height(36).color(AppConfig.primaryColor); Text('加载中...').fontSize(14).fontColor('#888').margin({ top: 12 }) }.width('100%').layoutWeight(1).justifyContent(FlexAlign.Center)
      } else {
        Scroll() {
          if (this.tab === 'diagnostic') { this.buildDiagnostic() }
          else if (this.tab === 'tutoring') { this.buildTutoring() }
          else if (this.tab === 'knowledge') { this.buildKnowledgeMap() }
          else if (this.tab === 'dashboard') { this.buildDashboard() }
          else if (this.tab === 'subjects') { this.buildSubjects() }
        }.layoutWeight(1).backgroundColor('#F0F4F8')
      }

      Row() {
        ForEach(this.tabs, (t: TabItem) => {
          Column({ space: 2 }) {
            Text(t.icon).fontSize(18)
            Text(t.label).fontSize(10).fontColor(this.tab === t.id ? AppConfig.primaryColor : '#999').fontWeight(this.tab === t.id ? 600 : 400)
          }.layoutWeight(1).padding({ top: 8, bottom: 8 }).onClick((): void => this.switchTab(t.id))
        }, (t: TabItem): string => t.id)
      }.width('100%').height(56).backgroundColor('#FFFFFF').border({ width: { top: 0.5 }, color: '#E5E5E5' })
    }.width('100%').height('100%')
  }

  // ==================== DIAGNOSTIC ====================
  @Builder buildDiagnostic() {
    Column({ space: 16 }) {
      // 冷启动引导 (新增 · Agent C维度)
      if (this.coldStartActive && this.coldStartQ !== null) {
        Column({ space: 12 }) {
          Text('🧭 学习画像引导').fontSize(22).fontWeight(700).fontColor('#1C1C1E').margin({ top: 32 })
          Text('5道基础题，帮你快速建立学习画像').fontSize(15).fontColor('#666')
          Text('第 ' + this.coldStartProgress.current + ' / ' + this.coldStartProgress.total + ' 题').fontSize(13).fontColor('#888').padding({ top: 4 })
          Row() {
            Row().width(((this.coldStartProgress.current / this.coldStartProgress.total) * 100).toString() + '%').height(4).backgroundColor(AppConfig.primaryColor).borderRadius(2)
          }.width('100%').height(4).backgroundColor('#E5E5E5').borderRadius(2)

          // 题目
          Column() {
            Text(this.coldStartQ.text).fontSize(17).fontWeight(500).fontColor('#1C1C1E').padding(20).textAlign(TextAlign.Center)
          }.width('100%').backgroundColor('#FFFFFF').borderRadius(12).margin({ top: 8 })

          // 选项
          ForEach(this.coldStartQ.options, (opt: string, idx: number) => {
            Button(opt).fontSize(16).width('100%').height(48).fontColor('#1C1C1E').backgroundColor('#FFFFFF').border({ width: 1, color: '#E5E5E5', style: BorderStyle.Solid }).borderRadius(10)
            .onClick((): void => {
              const finished = this.agentInput.submitColdStartAnswer(idx);
              if (finished) {
                this.coldStartActive = false;
                this.coldStartFinished = true;
                this.updateAgentActions();
              } else {
                this.coldStartQ = this.agentInput.getCurrentColdStartQuestion();
                this.coldStartProgress = this.agentInput.getColdStartProgress();
              }
            })
          }, (opt: string, i: number): string => i.toString())
        }.width('100%').padding(16).alignItems(HorizontalAlign.Start)
      }

      // 冷启动完成 → 显示画像摘要
      else if (this.coldStartFinished && this.agentProfile.isColdStartComplete()) {
        Column({ space: 12 }) {
          Text('✅ 学习画像已建立').fontSize(20).fontWeight(700).fontColor('#34D399').margin({ top: 24 })
          Column() {
            Row() { Text('推荐难度').fontSize(13).fontColor('#888').width(80); Text(this.getStars(this.agentProfile.getProfile().preferredDifficulty)).fontSize(16) }.width('100%').padding({ top: 4, bottom: 4 })
            Row() {
              Text('薄弱板块').fontSize(13).fontColor('#888').width(80)
              Text(this.agentProfile.getProfile().weaknesses.length > 0 ? this.agentProfile.getProfile().weaknesses.join('、') : '待探索').fontSize(14).fontColor('#F87171')
            }.width('100%').padding({ top: 4, bottom: 4 })
            Row() {
              Text('错因倾向').fontSize(13).fontColor('#888').width(80)
              Text('概念' + Math.round(this.agentProfile.getErrorAttribution().conceptual * 100) + '% · 计算' + Math.round(this.agentProfile.getErrorAttribution().calculative * 100) + '% · 时间' + Math.round(this.agentProfile.getErrorAttribution().timePressure * 100) + '%').fontSize(13).fontColor('#555')
            }.width('100%').padding({ top: 4, bottom: 4 })
          }.width('100%').padding(14).backgroundColor('#FFFFFF').borderRadius(10)
          Button('开始学习 →').fontSize(16).width('70%').height(48).margin({ top: 12 }).backgroundColor(AppConfig.primaryColor).borderRadius(12)
            .onClick((): void => { this.switchTab('tutoring'); })
        }.width('100%').padding(16).alignItems(HorizontalAlign.Center)
      }

      // 原有15题诊断
      else if (this.diagStep === 0) {
        Column({ space: 12 }) {
          Text('🎯 冷启动诊断').fontSize(22).fontWeight(700).fontColor('#1C1C1E').margin({ top: 32 })
          Text('15 道题目覆盖 8 大板块\n帮你快速定位薄弱环节').fontSize(15).fontColor('#666').textAlign(TextAlign.Center)
          Text('预计用时：8-10 分钟').fontSize(13).fontColor('#999')
          Button('开始诊断').fontSize(16).width('70%').height(48).margin({ top: 24 }).backgroundColor(AppConfig.primaryColor).borderRadius(12)
            .onClick((): void => { this.diagStep = 1; })
        }.width('100%').alignItems(HorizontalAlign.Center)
      }
      else if (this.diagStep === 1 && this.diagQuestions.length > 0) {
        Column({ space: 12 }) {
          Row() {
            Text('第 ' + (this.diagCurrentQ + 1) + ' / ' + this.diagQuestions.length + ' 题').fontSize(13).fontColor('#888')
            Blank()
            Text(this.diagQuestions[this.diagCurrentQ].board).fontSize(12).fontColor(AppConfig.primaryColor).padding({ left: 8, right: 8, top: 3, bottom: 3 }).backgroundColor(AppConfig.primaryColor + '15').borderRadius(8)
          }.width('100%')
          Row() { Row().width((((this.diagCurrentQ + 1) / this.diagQuestions.length) * 100).toString() + '%').height(4).backgroundColor(AppConfig.primaryColor).borderRadius(2) }.width('100%').height(4).backgroundColor('#E5E5E5').borderRadius(2)
          Column() { Text(this.diagQuestions[this.diagCurrentQ].text).fontSize(17).fontWeight(500).fontColor('#1C1C1E').padding(20).textAlign(TextAlign.Center) }.width('100%').backgroundColor('#FFFFFF').borderRadius(12).margin({ top: 8 })
          ForEach(this.diagQuestions[this.diagCurrentQ].options, (opt: string, idx: number) => {
            Button(opt).fontSize(16).width('100%').height(48).fontColor('#1C1C1E').backgroundColor('#FFFFFF').border({ width: 1, color: '#E5E5E5', style: BorderStyle.Solid }).borderRadius(10).onClick((): void => this.selectDiagAnswer(idx))
          }, (opt: string, i: number): string => i.toString())
        }.width('100%').padding(16).alignItems(HorizontalAlign.Start)
      }
      else if (this.diagStep === 2 && this.diagResult !== null) {
        Column({ space: 12 }) {
          Text('📊 诊断结果').fontSize(20).fontWeight(700).fontColor('#1C1C1E').margin({ top: 16 })
          Row({ space: 8 }) {
            Column() { Text(this.diagResult.totalScore.toString()).fontSize(32).fontWeight(700).fontColor('#34D399'); Text('正确').fontSize(11).fontColor('#888') }.layoutWeight(1).padding(12).backgroundColor('#FFFFFF').borderRadius(10).alignItems(HorizontalAlign.Center)
            Column() { Text((this.diagResult.maxScore - this.diagResult.totalScore).toString()).fontSize(32).fontWeight(700).fontColor('#F87171'); Text('错误').fontSize(11).fontColor('#888') }.layoutWeight(1).padding(12).backgroundColor('#FFFFFF').borderRadius(10).alignItems(HorizontalAlign.Center)
            Column() { Text(Math.round(this.diagResult.totalScore / this.diagResult.maxScore * 100) + '%').fontSize(32).fontWeight(700).fontColor(AppConfig.primaryColor); Text('得分率').fontSize(11).fontColor('#888') }.layoutWeight(1).padding(12).backgroundColor('#FFFFFF').borderRadius(10).alignItems(HorizontalAlign.Center)
          }.width('100%')
          Text('各板块掌握情况').fontSize(14).fontWeight(600).fontColor('#1C1C1E').margin({ top: 8 }).alignSelf(ItemAlign.Start)
          ForEach(this.diagResult.boards, (b: BoardScore) => {
            Row() {
              Text(b.name).fontSize(13).fontColor('#1C1C1E').width(72)
              Row() { Row().width(b.score.toString() + '%').height(6).backgroundColor(b.color).borderRadius(3) }.width('50%').height(6).backgroundColor('#F0F0F0').borderRadius(3)
              Text(b.score.toString()).fontSize(12).fontColor(b.color).fontWeight(600).width(30).textAlign(TextAlign.End)
            }.width('100%')
          }, (b: BoardScore): string => b.name)
          Button('重新诊断').fontSize(14).margin({ top: 12 }).backgroundColor(AppConfig.primaryColor).borderRadius(8).onClick((): void => this.restartDiag())
        }.width('100%').padding(16).alignItems(HorizontalAlign.Start)
      }
    }.width('100%').padding({ bottom: 16 })
  }

  // ==================== TUTORING (enhanced) ====================
  @Builder buildTutoring() {
    Column() {
      // 筛选栏
      Column({ space: 10 }) {
        Row({ space: 6 }) {
          ForEach(this.diffTags, (dt: DiffTag) => {
            Text(dt.label).fontSize(12).padding({ left: 10, right: 10, top: 5, bottom: 5 })
              .fontColor(this.tutorDiff === dt.value ? '#FFFFFF' : '#666')
              .backgroundColor(this.tutorDiff === dt.value ? AppConfig.primaryColor : '#FFFFFF')
              .border({ width: 1, color: this.tutorDiff === dt.value ? AppConfig.primaryColor : '#E0E0E0' })
              .borderRadius(14).onClick((): void => { this.tutorDiff = dt.value; this.filterTutorQuestions(); })
          }, (dt: DiffTag): string => dt.value.toString())
          Blank()
          Text(this.tutorFilteredQuestions.length + ' 题').fontSize(12).fontColor('#888')
        }.width('100%')
      }.width('100%').padding({ left: 16, right: 16, top: 12, bottom: 8 }).backgroundColor('#FFFFFF')

      // 小龙虾按钮 (G维度 · Phase 1B mock)
      Row() {
        if (this.lobsterMode) {
          Text('🦞 小龙虾推荐 · ' + this.lobsterQuestions.length + ' 题').fontSize(13).fontColor(AppConfig.primaryColor).fontWeight(600)
          Blank()
          Button('退出').fontSize(11).height(28).backgroundColor('#F0F0F0').fontColor('#666').borderRadius(14)
            .onClick((): void => this.exitLobsterMode())
        } else {
          Button() {
            Row() { Text('🦞 问小龙虾出题').fontSize(13).fontColor('#FFFFFF') }
          }.height(36).backgroundColor(AppConfig.primaryColor).borderRadius(18).padding({ left: 16, right: 16 })
          .enabled(!this.lobsterGenerating)
          .onClick((): void => this.askLobster())
        }
        Blank()
        if (this.undoCount > 0) {
          Text('↩ ' + this.undoCount + ' 步可撤销').fontSize(11).fontColor('#888')
        }
      }.width('100%').padding({ left: 16, right: 16, top: 4, bottom: 4 }).backgroundColor('#FFFFFF')

      // 题目区
      Column({ space: 12 }) {
        if (this.tutorFilteredQuestions.length === 0) {
          Column() { Text('暂无匹配题目').fontSize(16).fontColor('#888') }.width('100%').height(200).justifyContent(FlexAlign.Center)
        } else {
          Column({ space: 12 }) {
            Row() {
              Text(this.tutorFilteredQuestions[this.tutorCurrentQ].board + ' · ' + this.tutorFilteredQuestions[this.tutorCurrentQ].kp).fontSize(12).fontColor(AppConfig.primaryColor).padding({ left: 8, right: 8, top: 3, bottom: 3 }).backgroundColor(AppConfig.primaryColor + '12').borderRadius(8)
              Blank()
              Text('难度 ' + '⭐'.repeat(this.tutorFilteredQuestions[this.tutorCurrentQ].difficulty)).fontSize(12).fontColor('#F59E0B')
            }.width('100%')
            Text(this.tutorFilteredQuestions[this.tutorCurrentQ].text).fontSize(16).fontWeight(500).fontColor('#1C1C1E').padding({ top: 8, bottom: 8 })
            if (!this.tutorSubmitted) {
              TextArea({ placeholder: '写出你的解题思路...', text: this.tutorAnswer }).width('100%').height(100).fontSize(14).borderRadius(8).backgroundColor('#F8F8F8').border({ width: 1, color: '#E0E0E0' }).padding(12).onChange((v: string): void => { this.tutorAnswer = v; })
              Button('提交思路').fontSize(15).width('100%').height(44).backgroundColor(AppConfig.primaryColor).borderRadius(10).onClick((): void => { this.submitTutor(); })
            } else {
              Column({ space: 8 }) {
                Text(this.tutorCorrect ? '✅ 思路正确！' : '💡 需要改进').fontSize(16).fontWeight(600).fontColor(this.tutorCorrect ? '#34D399' : '#F59E0B')
                Text(this.tutorFeedback).fontSize(14).fontColor('#555').padding(12).backgroundColor('#F8F8F8').borderRadius(8).width('100%')
                Button('下一题 →').fontSize(14).width('100%').height(40).backgroundColor(AppConfig.primaryColor).borderRadius(10).onClick((): void => this.nextTutorQ())
              }.width('100%')
            }
          }.width('100%').padding(16).backgroundColor('#FFFFFF').borderRadius(12)
        }
      }.width('100%').padding(16)
    }.width('100%').padding({ bottom: 16 })
  }

  // ==================== KNOWLEDGE MAP ====================
  private getRadarDataJson(): string {
    let json: string = '[';
    for (let i: number = 0; i < this.knowledgeNodes.length; i++) {
      const n: KnowledgeNode = this.knowledgeNodes[i];
      const c: string = n.mastery >= 70 ? '#34D399' : n.mastery >= 40 ? '#FBBF24' : '#F87171';
      json += '{"name":"' + n.name + '","value":' + n.mastery + ',"color":"' + c + '"}';
      if (i < this.knowledgeNodes.length - 1) json += ',';
    }
    return json + ']';
  }

  @Builder buildKnowledgeMap() {
    Column({ space: 12 }) {
      Text('知识地图').fontSize(20).fontWeight(700).fontColor('#1C1C1E').margin({ top: 8 })
      // Radar chart
      if (this.knowledgeNodes.length > 0) {
        Column() {
          HRadarChart({ data: this.getRadarDataJson(), chartSize: 280, levels: 4, maxValue: 100 })
          Text('8 大板块全景雷达').fontSize(12).fontColor('#888').margin({ top: 4 })
        }.width('100%').padding(16).backgroundColor('#FFFFFF').borderRadius(12).alignItems(HorizontalAlign.Center)
      }
      ForEach(this.knowledgeNodes, (node: KnowledgeNode, idx: number) => {
        Column({ space: 6 }) {
          Row() {
            Text(node.name).fontSize(15).fontWeight(600).fontColor('#1C1C1E')
            Blank()
            Text(node.completedCount + '/' + node.kpCount).fontSize(12).fontColor('#888')
            Text(node.mastery + '%').fontSize(14).fontWeight(700).fontColor(node.mastery >= 70 ? '#34D399' : node.mastery >= 40 ? '#FBBF24' : '#F87171').margin({ left: 8 })
          }.width('100%').onClick((): void => { this.kmSelected = this.kmSelected === idx ? -1 : idx; })
          Row() { Row().width(node.mastery.toString() + '%').height(6).backgroundColor(node.mastery >= 70 ? '#34D399' : node.mastery >= 40 ? '#FBBF24' : '#F87171').borderRadius(3) }.width('100%').height(6).backgroundColor('#F0F0F0').borderRadius(3)
          if (this.kmSelected === idx) {
            ForEach(node.children, (child: KnowledgeChild) => {
              Row() {
                Text(child.name).fontSize(13).fontColor('#555').layoutWeight(1)
                Text(child.type).fontSize(10).fontColor('#FFF').padding({ left: 6, right: 6, top: 2, bottom: 2 }).backgroundColor(child.type === '陷阱' ? '#F87171' : child.type === '方法' ? '#818CF8' : '#34D399').borderRadius(6)
                Text(child.mastery + '%').fontSize(12).fontWeight(600).fontColor(child.mastery >= 70 ? '#34D399' : '#F87171').width(40).textAlign(TextAlign.End)
              }.width('100%').padding({ left: 12, top: 4, bottom: 4 })
            }, (c: KnowledgeChild): string => c.name)
          }
        }.width('100%').padding(12).backgroundColor('#FFFFFF').borderRadius(10)
      }, (n: KnowledgeNode): string => n.name)
    }.width('100%').padding(16).padding({ bottom: 24 })
  }

  // ==================== DASHBOARD (enhanced 2x2) ====================
  @Builder buildDashboard() {
    Column({ space: 12 }) {
      if (this.dashData !== null) {
        // 2x2 KPI Grid
        Row({ space: 8 }) {
          Column() {
            Text('📈 本周掌握').fontSize(12).fontColor('#888'); Text('+5').fontSize(28).fontWeight(700).fontColor('#34D399'); Text('考点').fontSize(11).fontColor('#888')
          }.layoutWeight(1).padding(14).backgroundColor('#FFFFFF').borderRadius(10)
          Column() {
            Text('📋 完成进度').fontSize(12).fontColor('#888'); Text(this.dashData.weekTrend[6] + '/' + this.dashData.weekTrend[6]).fontSize(28).fontWeight(700).fontColor(AppConfig.primaryColor); Text(Math.round(this.dashData.todayCorrect / Math.max(1, this.dashData.todayQuestions) * 100) + '%').fontSize(11).fontColor('#888')
          }.layoutWeight(1).padding(14).backgroundColor('#FFFFFF').borderRadius(10)
        }.width('100%')
        Row({ space: 8 }) {
          Column() {
            Text('⏱ 学习时长').fontSize(12).fontColor('#888'); Text(this.dashData.totalHours + 'h').fontSize(28).fontWeight(700).fontColor('#8B5CF6'); Text('累计').fontSize(11).fontColor('#888')
          }.layoutWeight(1).padding(14).backgroundColor('#FFFFFF').borderRadius(10)
          Column() {
            Text('🎯 适应难度').fontSize(12).fontColor('#888'); Text('3.0').fontSize(28).fontWeight(700).fontColor('#F59E0B'); Text('目标60-80%').fontSize(11).fontColor('#888')
          }.layoutWeight(1).padding(14).backgroundColor('#FFFFFF').borderRadius(10)
        }.width('100%')

        // 倒计时
        Row() {
          Text('📅').fontSize(24)
          Column() { Text('距离高考').fontSize(12).fontColor('#888'); Text(this.dashData.daysLeft + ' 天').fontSize(22).fontWeight(700).fontColor('#1C1C1E') }.alignItems(HorizontalAlign.Start).margin({ left: 10 }).layoutWeight(1)
          Text('连续 ' + this.dashData.streak + ' 天').fontSize(13).fontColor(AppConfig.primaryColor).fontWeight(600)
        }.width('100%').padding(14).backgroundColor('#FFFFFF').borderRadius(10)

        // 薄弱板块
        Column() {
          Text('⚠️ 薄弱板块').fontSize(14).fontWeight(600).fontColor('#1C1C1E').margin({ bottom: 8 }).alignSelf(ItemAlign.Start)
          ForEach(this.dashData.weakBoards, (wb: WeakBoard) => {
            Row() { Text(wb.name).fontSize(14).fontColor('#555').layoutWeight(1); Text(wb.score + '%').fontSize(14).fontWeight(600).fontColor('#F87171') }.width('100%').padding({ top: 6, bottom: 6 })
          }, (wb: WeakBoard): string => wb.name)
        }.width('100%').padding(14).backgroundColor('#FFFFFF').borderRadius(10)

        // 智能体洞察 (新增 · D维度)
        if (this.insights.length > 0) {
          Column() {
            Text('🧠 学习洞察').fontSize(14).fontWeight(600).fontColor('#1C1C1E').margin({ bottom: 8 }).alignSelf(ItemAlign.Start)
            ForEach(this.insights.slice(0, 3), (ins: Insight) => {
              Row() {
                Column() {
                  Text(ins.title).fontSize(13).fontWeight(600).fontColor('#1C1C1E');
                  Text(ins.description).fontSize(11).fontColor('#888')
                }.alignItems(HorizontalAlign.Start).layoutWeight(1)
                if (ins.action !== undefined && ins.action !== null) {
                  Button('→').fontSize(14).width(32).height(32).backgroundColor(AppConfig.primaryColor).borderRadius(16)
                    .onClick((): void => { this.switchTab(ins.action!.targetTab as Tab); })
                }
              }.width('100%').padding({ top: 4, bottom: 4 })
            }, (ins: Insight, i: number): string => i.toString())
          }.width('100%').padding(14).backgroundColor('#F0FFF4').borderRadius(10)
        }

        // 智能体推荐 (C维度)
        if (this.agentActions.length > 0) {
          Column() {
            Text('💡 智能推荐').fontSize(14).fontWeight(600).fontColor('#1C1C1E').margin({ bottom: 8 }).alignSelf(ItemAlign.Start)
            ForEach(this.agentActions, (act: RecommendedAction) => {
              Row() {
                Text('→').fontSize(16).fontColor(AppConfig.primaryColor).fontWeight(700).width(24)
                Column() { Text(act.label).fontSize(14).fontWeight(500).fontColor('#1C1C1E'); Text(act.reason).fontSize(11).fontColor('#888') }.layoutWeight(1).alignItems(HorizontalAlign.Start)
              }.width('100%').padding({ top: 6, bottom: 6 }).onClick((): void => { this.switchTab(act.targetTab as Tab); })
            }, (act: RecommendedAction, i: number): string => i.toString())
          }.width('100%').padding(14).backgroundColor('#F0F7FF').borderRadius(10)
        }

        // 环境状态 (新增 · H维度)
        Column() {
          Text('🔋 设备状态').fontSize(14).fontWeight(600).fontColor('#1C1C1E').margin({ bottom: 8 }).alignSelf(ItemAlign.Start)
          Row() {
            Text(this.agentEnv.getBatteryStatusText()).fontSize(13).fontColor('#555')
            Blank()
            if (this.agentEnv.shouldThrottleSync()) {
              Text('省电模式').fontSize(11).fontColor('#F59E0B').padding({ left: 8, right: 8, top: 3, bottom: 3 }).backgroundColor('#FEF3C7').borderRadius(8)
            }
          }.width('100%')
        }.width('100%').padding(14).backgroundColor('#FFFFFF').borderRadius(10)

        // 本周趋势图
        Column() {
          Text('📈 本周刷题趋势').fontSize(14).fontWeight(600).fontColor('#1C1C1E').margin({ bottom: 8 }).alignSelf(ItemAlign.Start)
          Row({ space: 2 }) {
            ForEach(this.dashData.weekTrend, (v: number, i: number) => {
              Column() { Text(v.toString()).fontSize(10).fontColor('#888'); Row().width('100%').height(v * 2).backgroundColor(AppConfig.primaryColor).borderRadius({ topLeft: 3, topRight: 3 }) }.layoutWeight(1).alignItems(HorizontalAlign.Center).justifyContent(FlexAlign.End)
            }, (v: number, i: number): string => i.toString())
          }.width('100%').height(80)
        }.width('100%').padding(14).backgroundColor('#FFFFFF').borderRadius(10)
      }
    }.width('100%').padding(16).padding({ bottom: 24 })
  }

  // ==================== SUBJECTS ====================
  @Builder buildSubjects() {
    Column({ space: 12 }) {
      Text('选择学科').fontSize(20).fontWeight(700).fontColor('#1C1C1E').margin({ top: 8 })
      Text('切换学科后，诊断/刷题/知识地图将加载对应内容').fontSize(13).fontColor('#888')
      ForEach(this.domains, (d: DomainProfile) => {
        Row() {
          Text(d.icon).fontSize(32)
          Column() { Text(d.name).fontSize(17).fontWeight(600).fontColor('#1C1C1E'); Text(d.kpCount + ' 考点 · ' + d.questionCount + ' 题目').fontSize(13).fontColor('#888') }.alignItems(HorizontalAlign.Start).layoutWeight(1).margin({ left: 14 })
          if (this.selectedDomain === d.id) { Text('✓').fontSize(20).fontColor(AppConfig.primaryColor).fontWeight(700) }
        }.width('100%').padding(16).backgroundColor('#FFFFFF').borderRadius(12)
        .border({ width: this.selectedDomain === d.id ? 2 : 0, color: AppConfig.primaryColor })
        .onClick((): void => { this.selectedDomain = d.id; })
      }, (d: DomainProfile): string => d.id)
    }.width('100%').padding(16).padding({ bottom: 24 })
  }
}
