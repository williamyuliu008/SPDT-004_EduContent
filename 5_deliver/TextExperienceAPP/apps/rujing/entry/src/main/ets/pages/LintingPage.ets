/**
 * 入境 APP · 临帖页
 * 支持描红模式和自由临摹模式
 *
 * v1.0（2026-07-21）：
 *   - 描红模式：田字格 + 参考字（AI识别/程序化）
 *   - 自由临摹：空白田字格
 *   - AI 反馈（需联网）
 */

import { router } from '@kit.ArkUI';
import { ai } from '../service/AIService';
import { AIAction } from '../model/DataModel';
import { fileIo } from '@kit.CoreFileKit';
import { util } from '@kit.ArkTS';

// ─── 数据模型 ─────────────────────────────────────

/** 笔画点坐标 */
interface Point {
  x: number;
  y: number;
}

/** 临帖字帖条目 */
interface LintItem {
  char: string           // 练习字
  font: string            // 字体（小篆/楷书/隶书）
  example: string         // 出处
  description: string     // 描述
  ep_chain?: string       // 对应集/链
}

/** 临帖模式 */
enum LintMode {
  TRACING = '描红',
  FREE = '自由临摹'
}

// ─── 字帖库（运行时加载）───────────────────────────────

// 默认字帖（fallback，不依赖 rawfile）
const DEFAULT_LIBRARY: LintItem[] = [
  { char: '永', font: '小篆', example: '王羲之·兰亭序', description: '永字八法：侧勒弩趯策掠啄磔' },
  { char: '山', font: '小篆', example: '《说文解字》', description: '象形字，山峰之形' },
  { char: '水', font: '小篆', example: '《说文解字》', description: '象形字，流水之形' },
  { char: '日', font: '小篆', example: '《说文解字》', description: '象形字，太阳之形' },
  { char: '月', font: '小篆', example: '《说文解字》', description: '象形字，月亮之形' },
  { char: '書', font: '楷书', example: '孙过庭·书谱', description: '书者，散也' },
  { char: '道', font: '小篆', example: '《说文解字》', description: '道者，路也' },
  { char: '法', font: '小篆', example: '唐人尚法', description: '法者，规矩也' },
  { char: '意', font: '小篆', example: '宋人尚意', description: '意者，心之所向' },
  { char: '風', font: '小篆', example: '《说文解字》', description: '风动虫生' },
  { char: '龍', font: '小篆', example: '李斯·峄山碑', description: '秦篆典范' },
  { char: '德', font: '小篆', example: '《说文解字》', description: '德者，得也' },
];

// ─── 组件 ──────────────────────────────────────────

/**
 * 田字格组件（Shape 实现，无需 Canvas API）
 * 红色横中线 + 蓝色竖中线 + 对角虚线
 */
@Component
struct TianZiGe {
  @Prop gridSizePx: number = 280;

  build() {
    Stack() {
      // 外框
      Rect()
        .width(this.size)
        .height(this.size)
        .stroke('#333333')
        .strokeWidth(2)
        .fill(Color.White)

      // 横中线（红色）
      Line({ width: this.gridSizePx, height: this.gridSizePx })
        .startPoint([0, this.gridSizePx / 2])
        .endPoint([this.gridSizePx, this.gridSizePx / 2])
        .stroke('#e57373')
        .strokeWidth(1)
        .zIndex(1)

      // 竖中线（蓝色）
      Line({ width: this.gridSizePx, height: this.gridSizePx })
        .startPoint([this.gridSizePx / 2, 0])
        .endPoint([this.gridSizePx / 2, this.gridSizePx])
        .stroke('#64b5f6')
        .strokeWidth(1)
        .zIndex(2)

      // 左上→右下对角虚线
      Line({ width: this.gridSizePx, height: this.gridSizePx })
        .startPoint([0, 0])
        .endPoint([this.gridSizePx, this.gridSizePx])
        .stroke('#dddddd')
        .strokeWidth(0.5)
        .zIndex(0)

      // 右上→左下对角虚线
      Line({ width: this.gridSizePx, height: this.gridSizePx })
        .startPoint([this.gridSizePx, 0])
        .endPoint([0, this.gridSizePx])
        .stroke('#dddddd')
        .strokeWidth(0.5)
        .zIndex(0)
    }
    .width(this.size)
    .height(this.size)
  }
}

@Component
struct TraceChar {
  @Prop char: string = '';
  @Prop charSize: number = 200;
  @Prop charOpacity: number = 0.18;
  @Prop font: string = '小篆';

  // 将 0-1 opacity 转为 #AARRGGBB 格式
  private getOpacityColor(opacity: number): string {
    const alpha = Math.round(opacity * 255).toString(16).padStart(2, '0');
    return '#' + alpha + 'e0e0e0';
  }

  build() {
    Column() {
      Text(this.char)
        .fontSize(this.charSize * 0.72)
        .fontWeight(900)
        .fontColor(this.getOpacityColor(this.charOpacity))
        .fontFamily(this.font === '小篆' ? 'serif' : 'HarmonyOS Sans')
        .textAlign(TextAlign.Center)
        .width('100%')
        .height('100%')
    }
    .width(this.charSize)
    .height(this.charSize)
    .justifyContent(FlexAlign.Center)
    .alignItems(HorizontalAlign.Center)
  }
}

/**
 * 书写画布组件（Canvas API 实现）
 * 捕获触控轨迹，实时渲染笔画
 */
@Component
struct WritingCanvas {
  @Prop canvasSize: number = 280;
  @Link strokePoints: Array<Array<Point>>;
  @Link currentStroke: Array<Point>;
  onDrawStart: (x: number, y: number) => void = () => {};
  onDrawUpdate: (x: number, y: number) => void = () => {};
  onDrawEnd: () => void = () => {};

  // CanvasRenderingContext2D
  private ctx: CanvasRenderingContext2D = new CanvasRenderingContext2D();

  // 渲染上下文尺寸
  private dpr: number = 1;

  // 全量重绘（抹掉重画所有笔画）
  redrawAll(): void {
    const ctx2d = this.ctx;
    const size = this.canvasSize * this.dpr;

    // 清空画布（透明）
    ctx2d.clearRect(0, 0, size, size);

    // 绘制已完成的笔画
    ctx2d.lineCap = 'round';
    ctx2d.lineJoin = 'round';
    ctx2d.lineWidth = 4 * this.dpr;
    ctx2d.strokeStyle = '#333333';

    for (const stroke of this.strokePoints) {
      if (stroke.length < 2) continue;
      ctx2d.beginPath();
      ctx2d.moveTo(stroke[0].x * this.dpr, stroke[0].y * this.dpr);
      for (let i = 1; i < stroke.length; i++) {
        ctx2d.lineTo(stroke[i].x * this.dpr, stroke[i].y * this.dpr);
      }
      ctx2d.stroke();
    }

    // 绘制当前正在写的笔画
    if (this.currentStroke.length >= 2) {
      ctx2d.beginPath();
      ctx2d.moveTo(
        this.currentStroke[0].x * this.dpr,
        this.currentStroke[0].y * this.dpr
      );
      for (let i = 1; i < this.currentStroke.length; i++) {
        ctx2d.lineTo(
          this.currentStroke[i].x * this.dpr,
          this.currentStroke[i].y * this.dpr
        );
      }
      ctx2d.stroke();
    }
  }

  build() {
    Canvas(this.ctx)
      .width(this.canvasSize)
      .height(this.canvasSize)
      .backgroundColor(Color.Transparent)
      .onReady(() => {
        // DPR=1，简化处理；首次就绪时清空画布
        const size = this.canvasSize * this.dpr;
        this.ctx.clearRect(0, 0, size, size);
      })
      .gesture(
        // PanGesture：触控拖拽书写
        PanGesture()
          .onActionStart((event: PanGestureEvent) => {
            // fingerList[0].localX/localY 是相对于组件的坐标
            const px = event.fingerList[0].localX;
            const py = event.fingerList[0].localY;
            this.currentStroke = [{ x: px, y: py }];
            this.onDrawStart(px, py);
          })
          .onActionUpdate((event: PanGestureEvent) => {
            const px = event.fingerList[0].localX;
            const py = event.fingerList[0].localY;
            this.currentStroke.push({ x: px, y: py });
            this.onDrawUpdate(px, py);
            // 实时追加绘制当前笔画
            const ctx2d = this.ctx;
            const dpr = this.dpr;
            const len = this.currentStroke.length;
            if (len >= 2) {
              ctx2d.lineCap = 'round';
              ctx2d.lineJoin = 'round';
              ctx2d.lineWidth = 4 * dpr;
              ctx2d.strokeStyle = '#333333';
              ctx2d.beginPath();
              ctx2d.moveTo(
                this.currentStroke[len - 2].x * dpr,
                this.currentStroke[len - 2].y * dpr
              );
              ctx2d.lineTo(px * dpr, py * dpr);
              ctx2d.stroke();
            }
          })
          .onActionEnd(() => {
            if (this.currentStroke.length > 0) {
              this.strokePoints.push([...this.currentStroke]);
            }
            this.currentStroke = [];
            this.onDrawEnd();
          })
      )
  }
}

@Component
struct LintCard {
  @Prop item: LintItem = { char: '', font: '', example: '', description: '' };
  @Prop selected: boolean = false;
  onSelect: () => void = () => {};

  build() {
    Column() {
      Text(this.item.char)
        .fontSize(32)
        .fontWeight(700)
        .fontColor(this.selected ? '#fff' : '#333')
        .fontFamily(this.item.font === '小篆' ? 'serif' : 'HarmonyOS Sans')

      Text(this.item.font)
        .fontSize(10)
        .fontColor(this.selected ? '#fff8' : '#999')

      Text(this.item.example)
        .fontSize(10)
        .fontColor(this.selected ? '#fff8' : '#aaa')
        .maxLines(1)
        .textOverflow({ overflow: TextOverflow.Ellipsis })
    }
    .width(80)
    .height(80)
    .backgroundColor(this.selected ? '#c0392b' : Color.White)
    .borderRadius(12)
    .border({
      width: 1,
      color: this.selected ? '#c0392b' : '#eee'
    })
    .shadow(this.selected ? {
      radius: 8,
      color: '#40000000',
      offsetX: 0,
      offsetY: 2
    } : { radius: 0 })
    .onClick(() => this.onSelect())
  }
}

// ─── 主页面 ─────────────────────────────────────────

@Entry
@Component
struct LintingPage {
  // 状态
  @State currentMode: LintMode = LintMode.TRACING;
  @State selectedItem: LintItem | null = null;
  @State gridSize: number = 280;       // 田字格大小
  @State traceOpacity: number = 0.18;  // 描红透明度
  @State aiResult: string = '';        // AI 反馈结果
  @State isAILoading: boolean = false;
  @State showAIFeedback: boolean = false;
  @State showCharPicker: boolean = false;

  // 字帖库
  @State lintLibrary: LintItem[] = DEFAULT_LIBRARY;

  // 选中的字帖索引
  @State selectedIndex: number = 0;

  // ── 书写笔画状态（触控绘制） ──────────────────────
  @State strokePoints: Array<Array<Point>> = [];
  @State currentStroke: Array<Point> = [];
  @State strokeCount: number = 0;   // 笔画计数

  // 使用单例 ai（已在 EntryAbility 中配置 API Key）

  aboutToAppear(): void {
    this.loadLintLibrary();
    // 默认选中第一个字帖
    if (this.lintLibrary.length > 0) {
      this.selectedItem = this.lintLibrary[0];
    }
  }

  async loadLintLibrary(): Promise<void> {
    try {
      const ctx = getContext(this);
      const rm = ctx.resourceManager;
      const rawData: Uint8Array = await rm.getRawFileContent('lint_library.json');
      const decoder: util.TextDecoder = util.TextDecoder.create('utf-8', { ignoreBOM: true });
      const text: string = decoder.decodeToString(rawData);
      const libData = JSON.parse(text) as Record<string, Object>;

      const allItems = libData['all_items'] as Array<Record<string, string>> | undefined;
      if (allItems && allItems.length > 0) {
        this.lintLibrary = allItems.map((item: Record<string, string>): LintItem => ({
          char: item['char'] ?? '',
          font: item['font'] ?? '小篆',
          example: item['example'] ?? item['source'] ?? '',
          description: item['description'] ?? '',
        } as LintItem));
      }
    } catch (_) {
      // 使用默认字帖库
      console.info('[LintingPage] 字帖库加载失败，使用默认字帖');
    }
  }

  build() {
    Column() {
      // ── 顶部导航 ────────────────────────────────
      Row() {
        Text('← 返回')
          .fontSize(15)
          .fontColor('#c0392b')
          .onClick(() => router.back())

        Blank()

        Text('临帖')
          .fontSize(18)
          .fontWeight(600)
          .fontColor('#1a1a1a')

        Blank()

        Text('选字')
          .fontSize(14)
          .fontColor('#c0392b')
          .onClick(() => { this.showCharPicker = !this.showCharPicker; })
      }
      .width('100%')
      .padding({ left: 16, right: 16, top: 16, bottom: 12 })

      Scroll() {
        Column({ space: 20 }) {
          // ── 模式切换 ────────────────────────────
          Row() {
            this.modeButton('描红', LintMode.TRACING)
            this.modeButton('自由临摹', LintMode.FREE)
          }
          .width('100%')
          .padding({ left: 20, right: 20 })

          // ── 当前字帖信息 ────────────────────────
          if (this.selectedItem) {
            Column() {
              Text(this.selectedItem.char)
                .fontSize(16)
                .fontWeight(700)
                .fontColor('#333')
              Text(this.selectedItem.example + ' · ' + this.selectedItem.font)
                .fontSize(12)
                .fontColor('#888')
                .margin({ top: 2 })
              Text(this.selectedItem.description)
                .fontSize(11)
                .fontColor('#aaa')
                .margin({ top: 2 })
            }
            .width('100%')
            .padding(12)
            .backgroundColor('#fff8f0')
            .borderRadius(10)
            .margin({ left: 20, right: 20 })
          }

          // ── 田字格区域 ─────────────────────────
          Column() {
            Stack() {
              // 1) 田字格底（网格参考线）
              TianZiGe({ gridSizePx: this.gridSize })

              // 2) 描红参考字（仅描红模式）
              if (this.currentMode === LintMode.TRACING && this.selectedItem) {
                TraceChar({
                  char: this.selectedItem.char,
                  charSize: this.gridSize * 0.75,
                  charOpacity: this.traceOpacity,
                  font: this.selectedItem.font
                })
              }

              // 3) 触控书写画布（顶层，透明）
              WritingCanvas({
                canvasSize: this.gridSize,
                strokePoints: $strokePoints,
                currentStroke: $currentStroke,
                onDrawStart: (x: number, y: number) => {
                  // 可在此处追加书写前的处理
                },
                onDrawEnd: () => {
                  // 笔画完成时更新计数
                  animateTo({ duration: 100 }, () => {
                    this.strokeCount = this.strokePoints.length;
                  });
                }
              })
              .opacity(0.85)
            }
            .width(this.gridSize)
            .height(this.gridSize)
            .margin({ left: 'auto', right: 'auto' })

            // 透明度调节（仅描红模式）
            if (this.currentMode === LintMode.TRACING) {
              Column({ space: 8 }) {
                Row() {
                  Text('描红透明度')
                    .fontSize(12)
                    .fontColor('#888')
                  Text(Math.round(this.traceOpacity * 100) + '%')
                    .fontSize(12)
                    .fontColor('#c0392b')
                    .margin({ left: 8 })
                }
                .width('100%')

                Slider({
                  value: this.traceOpacity * 100,
                  min: 5,
                  max: 50,
                  step: 1,
                  style: SliderStyle.OutSet
                })
                  .blockColor('#c0392b')
                  .trackColor('#f0f0f0')
                  .selectedColor('#c0392b')
                  .showTips(false)
                  .onChange((val: number) => {
                    this.traceOpacity = val / 100;
                  })
              }
              .width(this.gridSize)
              .margin({ top: 16 })
            }
          }
          .width('100%')
          .padding(20)
          .backgroundColor(Color.White)
          .borderRadius(14)
          .margin({ left: 20, right: 20 })

          // ── 笔画计数提示 ───────────────────────
          Row() {
            Text('✍️')
              .fontSize(14)
            Text(`已写 ${this.strokeCount} 笔`)
              .fontSize(12)
              .fontColor('#888')
              .margin({ left: 4 })
            if (this.strokeCount > 0 && this.strokeCount < 8) {
              Text('💡 提示：篆书单字通常 5-15 笔')
                .fontSize(11)
                .fontColor('#c0392b')
                .margin({ left: 12 })
            }
            if (this.strokeCount >= 8) {
              Text('✅ 继续完成，或点击「拍照识别」让 AI 评分')
                .fontSize(11)
                .fontColor('#27ae60')
                .margin({ left: 12 })
            }
          }
          .width('100%')
          .padding({ left: 20, right: 20, top: 4, bottom: 4 })

          // ── 字帖选择栏 ─────────────────────────
          Column() {
            Text('字帖库（来自 cafa 配置包）')
              .fontSize(13)
              .fontWeight(600)
              .fontColor('#333')
              .alignSelf(ItemAlign.Start)

            List() {
              ForEach(this.lintLibrary, (item: LintItem, idx: number) => {
                ListItem() {
                  LintCard({
                    item: item,
                    selected: this.selectedIndex === idx,
                    onSelect: () => {
                      this.selectedIndex = idx;
                      this.selectedItem = item;
                      this.showCharPicker = false;
                      this.aiResult = '';
                      this.showAIFeedback = false;
                    }
                  })
                }
              })
            }
            .listDirection(Axis.Horizontal)
            .scrollBar(BarState.Off)
            .height(90)
          }
          .width('100%')
          .padding(16)
          .backgroundColor(Color.White)
          .borderRadius(14)
          .margin({ left: 20, right: 20 })

          // ── AI 反馈区 ─────────────────────────
          if (this.aiResult.length > 0) {
            Column() {
              Row() {
                Text('📝 AI 临帖反馈')
                  .fontSize(13)
                  .fontWeight(600)
                  .fontColor('#333')
                Blank()
                Text('✕')
                  .fontSize(16)
                  .fontColor('#999')
                  .onClick(() => { this.showAIFeedback = false; this.aiResult = ''; })
              }
              .width('100%')
              .margin({ bottom: 8 })

              Text(this.aiResult)
                .fontSize(13)
                .fontColor('#555')
                .lineHeight(22)
            }
            .width('100%')
            .padding(16)
            .backgroundColor('#fffbeb')
            .borderRadius(10)
            .border({ width: 1, color: '#ffe082' })
            .margin({ left: 20, right: 20 })
          }

          if (this.isAILoading) {
            Column() {
              LoadingProgress().width(32).height(32)
              Text('AI 分析中...')
                .fontSize(13)
                .fontColor('#888')
                .margin({ top: 8 })
            }
            .width('100%')
            .padding(20)
            .backgroundColor('#f8f8f8')
            .borderRadius(10)
            .margin({ left: 20, right: 20 })
          }

          // ── 操作按钮 ───────────────────────────
          Row({ space: 12 }) {
            Button('🗑 重置')
              .fontSize(14)
              .backgroundColor('#f5f5f5')
              .fontColor('#666')
              .borderRadius(20)
              .width('40%')
              .height(44)
              .onClick(() => {
                this.strokePoints = [];
                this.currentStroke = [];
                this.strokeCount = 0;
                this.aiResult = '';
                this.showAIFeedback = false;
              })

            Button('📷 拍照识别')
              .fontSize(14)
              .backgroundColor('#c0392b')
              .fontColor(Color.White)
              .borderRadius(20)
              .width('55%')
              .height(44)
              .onClick(() => this.askAIFeedback())
          }
          .width('100%')
          .padding({ left: 20, right: 20 })

          // ── 备考提示 ───────────────────────────
          Column() {
            Text('💡 备考提示')
              .fontSize(12)
              .fontWeight(600)
              .fontColor('#666')
              .alignSelf(ItemAlign.Start)
            Text('描红时先观察整体结构，再逐笔临写。永字八法是楷书基础：「侧（点）、勒（横）、努（竖）、趯（钩）、策（挑）、掠（长撇）、啄（短撇）、磔（捺）」。')
              .fontSize(11)
              .fontColor('#888')
              .lineHeight(18)
              .margin({ top: 6 })
          }
          .width('100%')
          .padding(16)
          .backgroundColor('#f9f9f9')
          .borderRadius(10)
          .margin({ left: 20, right: 20 })
        }
        .padding({ top: 0, bottom: 30 })
      }
      .layoutWeight(1)
      .scrollBar(BarState.Off)
    }
    .width('100%')
    .height('100%')
    .backgroundColor('#F5F5F5')
  }

  @Builder
  modeButton(label: string, mode: LintMode) {
    Text(label)
      .fontSize(14)
      .fontWeight(this.currentMode === mode ? 600 : 400)
      .fontColor(this.currentMode === mode ? '#c0392b' : '#888')
      .backgroundColor(this.currentMode === mode ? '#fff0f0' : '#f5f5f5')
      .borderRadius(20)
      .padding({ left: 20, right: 20, top: 8, bottom: 8 })
      .onClick(() => {
        animateTo({ duration: 200, curve: 'easeInOut' }, () => {
          this.currentMode = mode;
        })
      })
  }

  // ── AI 反馈 ──────────────────────────────────────

  async askAIFeedback(): Promise<void> {
    if (!this.selectedItem) {
      return;
    }
    this.isAILoading = true;
    this.aiResult = '';
    this.showAIFeedback = true;

    try {
      const char = this.selectedItem.char;
      const font = this.selectedItem.font;
      const example = this.selectedItem.example;
      const prompt = `你是一位书法老师。` +
        `请对练习者临写的「${char}」字（${font}体，出自${example}）给出反馈。` +
        `请从以下维度评价：1）整体结构是否端正；2）笔画是否有力；3）重心是否平稳；` +
        `4）有无常见错误。请用100字以内简洁回答，重点指出1-2个可改进之处。`;

      const response = await ai.sendMessage(
        AIAction.QA,
        prompt,
        `当前临帖字：${char}，字体：${font}，出处：${example}`,
        []
      );
      this.aiResult = response || '（AI 未能返回有效反馈，请检查网络连接）';
    } catch (e) {
      this.aiResult = '⚠️ 网络错误，请检查 AI 服务配置';
    } finally {
      this.isAILoading = false;
    }
  }
}
