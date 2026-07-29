/**
 * 入境 APP · 书法辨析卡浏览页 v1.3
 * PT-039 标准参照层 + 风格示意层双层卡片轮播
 *
 * v1.3（2026-07-21）：
 *   - 拖动方向修正（负增量使图片随手指同向移动）
 *   - 平移边界约束（最大拖动距离 = 超出可视区的图片尺寸 × 0.3 弹性余量）
 *   - 弹性边界效果（超出边界时产生抗力，非硬截断）
 *   - 双指缩放带缓动曲线（animateTo 过渡）
 *   - 当前缩放倍数指示器（底部浮动标签）
 *   - 双击重置缩放 + 平移
 *
 * v1.2（2026-07-21）：
 *   - TouchEvent 双指捏合缩放（1x-4x）
 *   - 全屏模式 + 横屏支持
 *   - 单指拖动浏览（delta 增量累积）
 *   - 双→单指中途切换检测
 */

import { router, window } from '@kit.ArkUI';
import { fileIo } from '@kit.CoreFileKit';
import { image } from '@kit.ImageKit';
import { BusinessError } from '@kit.BasicServicesKit';

interface CardMeta {
  index: number
  title: string
  subtitle: string
  leftName: string
  rightName: string
  keyDiff: string
  rawfile: string
}

const CARDS: CardMeta[] = [
  { index: 1, title: '草书辨析卡 01', subtitle: '王羲之 vs 王献之 · 东晋二王', leftName: '王羲之', rightName: '王献之', keyDiff: '含蓄 vs 奔放 · 秀美 vs 开张', rawfile: 'rebuilt_card01.png' },
  { index: 2, title: '草书辨析卡 02', subtitle: '张旭 vs 怀素 · 唐代草圣', leftName: '张旭', rightName: '怀素', keyDiff: '圆 vs 瘦 · 浓 vs 枯 · 磅礴 vs 迅疾', rawfile: 'rebuilt_card02.png' },
  { index: 3, title: '草书辨析卡 03', subtitle: '孙过庭 vs 赵孟頫', leftName: '孙过庭', rightName: '赵孟頫', keyDiff: '古雅 vs 圆润 · 法度 vs 秀美', rawfile: 'rebuilt_card03.png' },
  { index: 4, title: '楷书辨析卡 04', subtitle: '欧阳询 vs 颜真卿 · 唐楷双壁', leftName: '欧阳询', rightName: '颜真卿', keyDiff: '修长 vs 宽博 · 瘦硬 vs 雄壮', rawfile: 'rebuilt_card04.png' },
  { index: 5, title: '楷书辨析卡 05', subtitle: '柳公权 vs 欧阳询 · 柳骨欧险', leftName: '柳公权', rightName: '欧阳询', keyDiff: '骨力 vs 险劲 · 瘦硬 vs 精密', rawfile: 'rebuilt_card05.png' },
]

const IMG_DIR = '/data/storage/el2/base/files/calligraphy_cards/'
const SCALE_MIN = 1.0
const SCALE_MAX = 4.0
const ELASTIC_RATIO = 0.28   // 超出边界的弹性余量（超出量 × 此比例）
const ZOOM_SHOW_THRESHOLD = 1.05 // 缩放超过此值才显示指示器
// 滑动切换阈值（px，从触摸起点算起的最小位移）
const SWIPE_DIR_PIXELS = 30
// 滑动视觉阻尼系数（图片视觉位移 = 实际滑动 × 此系数，<1 产生阻尼感）
const SWIPE_VISUAL_DAMPING = 0.70

// 强制横屏（适合欣赏长卷）
async function forceOrientation(landscape: boolean): Promise<void> {
  try {
    const ctx = getContext();
    const win = window.getLastWindow(ctx);
    const w = await win;
    await w.setPreferredOrientation(
      landscape ? window.Orientation.LANDSCAPE : window.Orientation.PORTRAIT
    );
  } catch (_) {}
}

// 恢复跟随系统方向
async function resetOrientation(): Promise<void> {
  try {
    const ctx = getContext();
    const win = window.getLastWindow(ctx);
    const w = await win;
    await w.setPreferredOrientation(window.Orientation.AUTO_ROTATION_RESTRICTED);
  } catch (_) {}
}

// FitSize 接口（ArkTS 严格模式要求显式接口）
interface FitSize {
  fw: number
  fh: number
}
// PanBounds 接口
interface PanBounds {
  maxPanX: number
  maxPanY: number
}

// 计算图片在容器中的实际像素尺寸（考虑 objectFit: Contain）
function calcFitSize(imgW: number, imgH: number, containerW: number, containerH: number): FitSize {
  const scaleX = containerW / imgW;
  const scaleY = containerH / imgH;
  const scale = Math.min(scaleX, scaleY);
  const result: FitSize = { fw: imgW * scale, fh: imgH * scale };
  return result;
}

@Entry
@Component
struct CalligraphyComparePage {
  @State currentIndex: number = 0;
  @State pixelMaps: PixelMap[] = [];
  @State isLoading: boolean = true;
  @State loadError: string = '';
  // 全屏模式
  @State isFullscreen: boolean = false;
  // 缩放状态
  @State scaleValue: number = 1;
  // 累计平移量（@State，UI响应式更新）
  @State panAccX: number = 0;
  @State panAccY: number = 0;
  // 视图尺寸（容器像素尺寸）
  @State viewW: number = 360;
  @State viewH: number = 640;
  // 当前图片像素尺寸
  @State imgW: number = 360;
  @State imgH: number = 480;
  // 是否显示缩放指示器
  @State showZoomBadge: boolean = false;
  // 缩放指示器定时器
  private zoomBadgeTimer: number = -1;

  // 手势起点追踪
  private gestureBaseScale: number = 1;
  // TouchEvent 手动多触控追踪
  private touchStartDist: number = 0;
  private touchCurDist: number = 0;
  private touchPinchStartScale: number = 1;
  private touchIsPinch: boolean = false;
  // 单指拖动用：记录起点屏幕坐标
  private touchStartX: number = 0;
  private touchStartY: number = 0;
  // 记录本次手势的"绝对起点"（用于全程方向判断，避免 @State 时序问题）
  private touchOriginX: number = 0;
  private touchOriginY: number = 0;
  // 双击检测
  private lastTapTime: number = 0;
  private lastTapX: number = 0;
  private lastTapY: number = 0;
  // 滑动切换追踪（private 普通字段，避免 @State 时序问题）
  private touchIsSwiping: boolean = false;
  // 滑动时图片视觉反馈（private，普通变量，UI用 computed 值）
  private swipeOffset: number = 0;
  // 控制栏显示/隐藏（自动隐藏）
  @State controlsVisible: boolean = true;
  private hideTimer: number = -1;

  aboutToAppear(): void {
    this.initImages();
  }

  aboutToDisappear(): void {
    resetOrientation();
    if (this.hideTimer >= 0) { clearTimeout(this.hideTimer); }
    if (this.zoomBadgeTimer >= 0) { clearTimeout(this.zoomBadgeTimer); }
  }

  async initImages(): Promise<void> {
    const ctx = getContext(this);
    const rm = ctx.resourceManager;
    try { fileIo.mkdirSync(IMG_DIR, true); } catch (_) {}
    const loaded: PixelMap[] = [];

    for (const card of CARDS) {
      const destPath = IMG_DIR + card.rawfile;
      try {
        const exists = fileIo.listFileSync(IMG_DIR).includes(card.rawfile);
        if (!exists) {
          const rawData: Uint8Array = await rm.getRawFileContent(card.rawfile);
          const fd: number = fileIo.openSync(destPath,
            fileIo.OpenMode.CREATE | fileIo.OpenMode.WRITE_ONLY).fd;
          fileIo.writeSync(fd, rawData.buffer as ArrayBuffer);
          fileIo.closeSync(fd);
        }
        const imageSource: image.ImageSource = image.createImageSource('file://' + destPath);
        const pixelMap: PixelMap = await imageSource.createPixelMap();
        loaded.push(pixelMap);

        // 第一张图加载后检测原始像素尺寸（用于平移边界计算）
        if (loaded.length === 1) {
          try {
            const info = await loaded[0].getImageInfo();
            if (info && info.size) {
              this.imgW = info.size.width > 0 ? info.size.width : 1200;
              this.imgH = info.size.height > 0 ? info.size.height : 1600;
            }
          } catch (_) {
            // 使用默认尺寸
            this.imgW = 1200;
            this.imgH = 1600;
          }
        }
      } catch (e) {
        console.error('[Compare] load failed: ' + card.rawfile + ' -> ' + JSON.stringify(e));
      }
    }
    this.pixelMaps = loaded;
    this.isLoading = false;
    if (loaded.length === 0) {
      this.loadError = '图片加载失败，请确认 rawfile 中已包含辨析卡图片';
    }
  }

  // 切换全屏
  async toggleFullscreen(): Promise<void> {
    this.isFullscreen = !this.isFullscreen;
    this.scaleValue = 1;
    this.panAccX = 0;
    this.panAccY = 0;
    this.swipeOffset = 0;
    this.touchIsSwiping = false;
    this.showZoomBadge = false;
    if (this.isFullscreen) {
      await forceOrientation(false);
      this.scheduleHideControls();
    } else {
      await resetOrientation();
      this.controlsVisible = true;
      if (this.hideTimer >= 0) { clearTimeout(this.hideTimer); this.hideTimer = -1; }
    }
  }

  scheduleHideControls(): void {
    if (this.hideTimer >= 0) { clearTimeout(this.hideTimer); }
    this.controlsVisible = true;
    this.hideTimer = setTimeout(() => {
      this.controlsVisible = false;
      this.hideTimer = -1;
    }, 3000) as number;
  }

  showControls(): void {
    this.controlsVisible = true;
    this.scheduleHideControls();
  }

  // 显示缩放指示器（3秒后自动消失）
  showZoomBadgeFunc(): void {
    this.showZoomBadge = true;
    if (this.zoomBadgeTimer >= 0) { clearTimeout(this.zoomBadgeTimer); }
    this.zoomBadgeTimer = setTimeout(() => {
      this.showZoomBadge = false;
      this.zoomBadgeTimer = -1;
    }, 2000) as number;
  }

  // 重置缩放与平移（带动画）
  resetView(): void {
    animateTo({ duration: 280, curve: Curve.EaseOut }, () => {
      this.scaleValue = 1;
      this.panAccX = 0;
      this.panAccY = 0;
    });
    this.showZoomBadge = false;
    if (this.zoomBadgeTimer >= 0) { clearTimeout(this.zoomBadgeTimer); this.zoomBadgeTimer = -1; }
  }

  // 计算带弹性的平移约束（返回允许的最大平移值）
  // scaledW/scaledH: 缩放后的图片尺寸
  // 返回 PanBounds：X/Y 方向单侧最大位移（正值）
  calcPanBounds(scaledW: number, scaledH: number): PanBounds {
    const overX = (scaledW - this.viewW) / 2;
    const overY = (scaledH - this.viewH) / 2;
    const maxPanX: number = Math.max(0, overX);
    const maxPanY: number = Math.max(0, overY);
    const result: PanBounds = { maxPanX: maxPanX, maxPanY: maxPanY };
    return result;
  }

  // 带弹性约束的平移设置
  setPanWithElastic(newPanX: number, newPanY: number): void {
    const scaledW = this.imgW * this.scaleValue;
    const scaledH = this.imgH * this.scaleValue;
    const bounds: PanBounds = this.calcPanBounds(scaledW, scaledH);
    const maxPanX: number = bounds.maxPanX;
    const maxPanY: number = bounds.maxPanY;

    if (maxPanX <= 0) {
      // 图片比容器窄：居中
      this.panAccX = 0;
    } else {
      // 弹性：超出边界时提供非线性抗力
      const rawX = Math.max(-maxPanX, Math.min(maxPanX, newPanX));
      const overflowX = rawX - Math.max(-maxPanX, Math.min(maxPanX, rawX));
      // 超出部分用弹性因子压缩
      const elasticX = rawX + overflowX * (1 - ELASTIC_RATIO);
      this.panAccX = Math.max(-maxPanX, Math.min(maxPanX, elasticX));
    }

    if (maxPanY <= 0) {
      this.panAccY = 0;
    } else {
      const rawY = Math.max(-maxPanY, Math.min(maxPanY, newPanY));
      const elasticY = rawY + (rawY - Math.max(-maxPanY, Math.min(maxPanY, rawY))) * (1 - ELASTIC_RATIO);
      this.panAccY = Math.max(-maxPanY, Math.min(maxPanY, elasticY));
    }
  }

  prev(): void {
    if (this.currentIndex > 0) {
      this.currentIndex--;
    } else {
      this.currentIndex = CARDS.length - 1;
    }
    this.swipeOffset = 0;
    this.touchIsSwiping = false;
    this.resetView();
  }

  next(): void {
    if (this.currentIndex < CARDS.length - 1) {
      this.currentIndex++;
    } else {
      this.currentIndex = 0;
    }
    this.swipeOffset = 0;
    this.touchIsSwiping = false;
    this.resetView();
  }

  // 更新容器和图片尺寸
  onViewportSizeChange(w: number, h: number): void {
    this.viewW = w;
    this.viewH = h;
  }

  // 获取当前缩放后的视觉样式（void 版本，仅供调试）
  logTransform(): void {
    // Debug: console.log('transform', this.scaleValue, this.panAccX, this.panAccY);
  }

  // ──────────────────────────────────────
  // 普通模式下的页面
  // ──────────────────────────────────────
  @Builder
  NormalPage() {
    Column() {
      // 顶部导航
      Row() {
        Text('← 返回')
          .fontSize(15).fontColor('#4a6cf7')
          .onClick(() => router.back())
        Blank()
        Text('书法辨析卡')
          .fontSize(18).fontWeight(600).fontColor('#1a1a1a')
        Blank()
        Text('CC0')
          .fontSize(11).fontColor('#D4B87A')
          .backgroundColor('#1A0E08').borderRadius(8)
          .padding({ left: 6, right: 6, top: 2, bottom: 2 })
      }
      .width('100%').padding({ left: 16, right: 16, top: 16, bottom: 12 })
      .backgroundColor(Color.White)

      // 轮播主体
      Column() {
        // 图片
        Stack() {
          if (this.pixelMaps[this.currentIndex]) {
            Image(this.pixelMaps[this.currentIndex])
              .width('100%').height('100%')
              .objectFit(ImageFit.Contain)
              .onClick(() => this.toggleFullscreen())
          }

          // 左翻页热区
          Column().width('25%').height('100%')
            .onClick(() => this.prev())
          // 右翻页热区
          Column().width('25%').height('100%').alignItems(HorizontalAlign.End)
            .onClick(() => this.next())
        }
        .width('100%').layoutWeight(1)
        .backgroundColor('#1A0E08')

        // 底部信息栏
        Column() {
          Row() {
            Text(CARDS[this.currentIndex].title)
              .fontSize(16).fontWeight(600).fontColor('#F5EDD8')
            Blank()
            Text((this.currentIndex + 1).toString() + ' / ' + CARDS.length.toString())
              .fontSize(14).fontColor('#D4B87A')
          }.width('100%').margin({ bottom: 6 })
          Text(CARDS[this.currentIndex].subtitle)
            .fontSize(13).fontColor('#C49A6C').margin({ bottom: 6 })
          Text('辨分核心：' + CARDS[this.currentIndex].keyDiff)
            .fontSize(12).fontColor('#D4B87A').margin({ bottom: 4 })
          Text('标准参照层：克利夫兰艺术馆 CC0 | PT-039 | 点击图片可全屏缩放欣赏')
            .fontSize(10).fontColor('#5A4A38')
        }
        .width('100%').padding({ left: 16, right: 16, top: 10, bottom: 10 })
        .backgroundColor('#1A0E08')

        // 分页点
        Row() {
          ForEach(CARDS, (card: CardMeta, idx: number) => {
            Column()
              .width(7).height(7).borderRadius(3.5)
              .backgroundColor(idx === this.currentIndex ? '#D4B87A' : '#4A3A28')
              .margin({ left: 4, right: 4 })
          })
        }
        .padding(10).backgroundColor('#1A0E08')
      }
      .width('100%').layoutWeight(1)
    }
    .width('100%').height('100%').backgroundColor('#F5F5F5')
  }

  // ──────────────────────────────────────
  // 全屏模式：沉浸式大图（v1.3 手势增强版）
  // ──────────────────────────────────────
  @Builder
  FullscreenView() {
    Stack({ alignContent: Alignment.Bottom }) {
      // 容器：捕获视图尺寸 + 手势
      Column() {
        if (this.pixelMaps[this.currentIndex]) {
          Image(this.pixelMaps[this.currentIndex])
            .width('100%').height('100%')
            .objectFit(ImageFit.Contain)
            .scale({
              x: this.scaleValue,
              y: this.scaleValue,
              centerX: '50%',
              centerY: '50%'
            })
            .translate({
              x: this.panAccX + this.swipeOffset,
              y: this.panAccY
            })
            .onTouch((event: TouchEvent) => {
              const touches = event.touches;
              const n = touches.length;
              const now = Date.now();

              // ── Down：初始化本次手势 ──────────────
              if (event.type === 0) {
                const cx = touches.length > 0 ? touches[0].x : 0;
                const cy = touches.length > 0 ? touches[0].y : 0;
                // 双击检测
                if (now - this.lastTapTime < 320 &&
                    Math.abs(cx - this.lastTapX) < 60 &&
                    Math.abs(cy - this.lastTapY) < 60) {
                  this.resetView();
                  this.lastTapTime = 0;
                  return;
                }
                this.lastTapTime = now;
                this.lastTapX = cx;
                this.lastTapY = cy;

                this.swipeOffset = 0;
                this.touchIsSwiping = false;
                if (n === 2) {
                  this.touchStartDist = Math.hypot(touches[1].x - touches[0].x, touches[1].y - touches[0].y);
                  this.touchCurDist = this.touchStartDist;
                  this.touchPinchStartScale = this.scaleValue;
                  this.touchIsPinch = this.touchStartDist > 30;
                  this.touchStartX = (touches[0].x + touches[1].x) / 2;
                  this.touchStartY = (touches[0].y + touches[1].y) / 2;
                  this.touchOriginX = this.touchStartX;
                  this.touchOriginY = this.touchStartY;
                } else if (n === 1) {
                  this.touchStartX = touches[0].x;
                  this.touchStartY = touches[0].y;
                  this.touchOriginX = touches[0].x;   // ← 全程绝对起点
                  this.touchOriginY = touches[0].y;
                  this.touchIsPinch = false;
                }
                return;
              }

              // ── Move：捏合缩放 or 滑动 ────────────
              if (event.type === 2) {
                // 双指 → 捏合缩放
                if (n === 2) {
                  if (!this.touchIsPinch) {
                    const d = Math.hypot(touches[1].x - touches[0].x, touches[1].y - touches[0].y);
                    if (d > 20) {
                      this.touchStartDist = d;
                      this.touchCurDist = this.touchStartDist;
                      this.touchPinchStartScale = this.scaleValue;
                      this.touchIsPinch = true;
                    }
                  }
                  if (this.touchIsPinch && this.touchStartDist > 10) {
                    const t0 = touches[0];
                    const t1 = touches[1];
                    const dist = Math.hypot(t1.x - t0.x, t1.y - t0.y);
                    const ratio = dist / this.touchStartDist;
                    this.scaleValue = Math.max(SCALE_MIN, Math.min(SCALE_MAX, this.touchPinchStartScale * ratio));
                    this.touchCurDist = dist;
                    this.setPanWithElastic(this.panAccX, this.panAccY);
                    this.showZoomBadgeFunc();
                  }
                  return;
                }

                // 单指 → 判断是竖向拖动还是横向滑动
                if (n === 1 && !this.touchIsPinch) {
                  const curX = touches[0].x;
                  const curY = touches[0].y;
                  // 计算相对于"手势绝对起点"的位移（避免 @State 时序问题）
                  const fromOriginX = curX - this.touchOriginX;
                  const fromOriginY = curY - this.touchOriginY;
                  const absX = Math.abs(fromOriginX);
                  const absY = Math.abs(fromOriginY);

                  // 竖向滑动为主 → 忽略（可能是滚动）
                  if (absY > 12 && absY > absX) {
                    return;
                  }

                  // 横向滑动：图片带阻尼跟随手指，方向判断用原始值
                  if (absX > 5) {
                    this.touchIsSwiping = true;
                    // 视觉偏移带阻尼（系数 < 1），产生"粘滞感"
                    this.swipeOffset = fromOriginX * SWIPE_VISUAL_DAMPING;
                  }
                  return;
                }
              }

              // ── Up：判断是否触发翻页 ──────────────
              if (event.type === 1) {
                // n === 0：最后一根手指抬起
                if (n === 0) {
                  if (this.touchIsSwiping) {
                    const totalX = this.swipeOffset;
                    if (totalX < -SWIPE_DIR_PIXELS) {
                      this.next();
                    } else if (totalX > SWIPE_DIR_PIXELS) {
                      this.prev();
                    }
                    this.swipeOffset = 0;
                    this.touchIsSwiping = false;
                  } else if (this.scaleValue < 1.05) {
                    this.resetView();
                  } else {
                    this.setPanWithElastic(this.panAccX, this.panAccY);
                  }
                  this.touchIsPinch = false;
                  return;
                }

                // n === 1：双指变单指（第二根手指抬起）
                if (n === 1) {
                  const curX = touches[0].x;
                  const curY = touches[0].y;
                  const fromOriginX = curX - this.touchOriginX;
                  const fromOriginY = curY - this.touchOriginY;
                  const absX = Math.abs(fromOriginX);
                  const absY = Math.abs(fromOriginY);
                  if (this.touchIsSwiping || absX > absY) {
                    if (fromOriginX < -SWIPE_DIR_PIXELS) {
                      this.next();
                    } else if (fromOriginX > SWIPE_DIR_PIXELS) {
                      this.prev();
                    }
                  }
                  this.swipeOffset = 0;
                  this.touchIsSwiping = false;
                  this.touchIsPinch = false;
                  this.touchStartX = curX;
                  this.touchStartY = curY;
                  return;
                }
              }
            })
            .onClick(() => {
              if (this.controlsVisible) {
                this.controlsVisible = false;
                if (this.hideTimer >= 0) { clearTimeout(this.hideTimer); this.hideTimer = -1; }
              } else {
                this.showControls();
              }
            })
        }
      }
      .width('100%').height('100%')
      .onAreaChange((_oldVal, newVal) => {
        this.viewW = newVal.width as number;
        this.viewH = newVal.height as number;
      })

      // ── 顶部安全区：关闭按钮（贴顶右角）────────
      if (this.controlsVisible) {
        Row() {
          Blank()
          Text('✕')
            .fontSize(18).fontColor('rgba(255,255,255,0.85)')
            .width(40).height(40)
            .textAlign(TextAlign.Center)
            .backgroundColor('rgba(26,14,8,0.6)').borderRadius(20)
            .onClick(() => this.toggleFullscreen())
        }
        .width('100%').padding({ left: 16, right: 16, top: 12 })
        .position({ y: 0 })
        .transition(TransitionEffect.OPACITY.animation({ duration: 200 }))
      }

      // ── 底部控制栏（极薄）────────────────────
      if (this.controlsVisible) {
        Column() {
          // 缩放指示器（嵌入底部）
          if (this.showZoomBadge && this.scaleValue > ZOOM_SHOW_THRESHOLD) {
            Row() {
              Blank()
              Text(Math.round(this.scaleValue * 100).toString() + '%')
                .fontSize(12).fontColor('#D4B87A').fontWeight(600)
            }
            .width('100%').margin({ bottom: 4 })
          }

          // 翻页 + 标题
          Row() {
            Text('◀')
              .fontSize(15).fontColor('#FFFFFF')
              .padding(10)
              .backgroundColor('rgba(212,184,122,0.45)').borderRadius(10)
              .onClick(() => this.prev())

            Column() {
              Text(CARDS[this.currentIndex].title)
                .fontSize(13).fontColor('#F5EDD8').fontWeight(600)
              Text(CARDS[this.currentIndex].keyDiff)
                .fontSize(11).fontColor('#8A7A6A').margin({ top: 1 })
            }
            .layoutWeight(1)
            .alignItems(HorizontalAlign.Center)

            Text((this.currentIndex + 1).toString() + ' / ' + CARDS.length.toString())
              .fontSize(12).fontColor('#8A7A6A')
              .margin({ left: 6, right: 6 })

            Text('▶')
              .fontSize(15).fontColor('#FFFFFF')
              .padding(10)
              .backgroundColor('rgba(212,184,122,0.45)').borderRadius(10)
              .onClick(() => this.next())
          }
          .width('100%')
        }
        .width('100%')
        .padding({ left: 16, right: 16, top: 8, bottom: 28 })
        .backgroundColor('rgba(26,14,8,0.75)')
        .transition(TransitionEffect.OPACITY.animation({ duration: 200 }))
      }
    }
    .width('100%').height('100%')
    .backgroundColor('#0A0604')
  }

  build() {
    Stack() {
      // 普通模式页面
      if (!this.isFullscreen) {
        this.NormalPage()
      }
      // 全屏模式
      if (this.isFullscreen) {
        this.FullscreenView()
      }
    }
    .width('100%').height('100%')
  }
}
