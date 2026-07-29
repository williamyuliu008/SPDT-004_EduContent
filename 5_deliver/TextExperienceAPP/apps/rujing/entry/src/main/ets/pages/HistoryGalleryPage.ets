/**
 * 入境 APP · 历史AI配图画廊页 v1.0
 * PT-039 墨骨山河 ep09 · 商鞅变法
 *
 * 功能：
 *   - ep09 商鞅变法 6 场景配图网格浏览
 *   - 点击查看大图（全屏 + 缩放）
 *   - 考点标签与场景说明
 *   - 书法×历史跨学科缝合展示
 */

import { router } from '@kit.ArkUI';
import { fileIo } from '@kit.CoreFileKit';
import { image } from '@kit.ImageKit';

interface GalleryItem {
  index: number
  sceneId: string
  sceneName: string
  actTitle: string
  description: string
  beatNote: string
  tags: string[]
  rawfile: string
  isSquare: boolean
}

const GALLERY_ITEMS: GalleryItem[] = [
  {
    index: 1,
    sceneId: '墨骨山河_09_1_1',
    sceneName: '求贤令',
    actTitle: '第一幕 · 栎阳求贤',
    description: '秦孝公颁布求贤令：宾客群臣有能出奇计强秦者，吾且尊官，与之分土。',
    beatNote: '历史考点：秦孝公求贤令的历史背景',
    tags: ['#古代史/商鞅变法', '#考频/⭐⭐⭐⭐⭐'],
    rawfile: 'pt039_ep09_01_求贤令.png',
    isSquare: false
  },
  {
    index: 2,
    sceneId: '墨骨山河_09_1_4',
    sceneName: '霸道定策',
    actTitle: '第一幕 · 栎阳求贤',
    description: '卫鞅三论：帝道 → 王道 → 霸道。秦孝公猛然站起：正合我意！',
    beatNote: '历史考点："治世不一道，便国不法古"',
    tags: ['#古代史/商鞅变法', '#诸子百家/法家', '#考频/⭐⭐⭐⭐⭐'],
    rawfile: 'pt039_ep09_02_霸道定策.png',
    isSquare: false
  },
  {
    index: 3,
    sceneId: '墨骨山河_09_2_1',
    sceneName: '南门立木',
    actTitle: '第二幕 · 南门立木',
    description: '栎阳南门，一根三丈高的木头。告示：移至北门，赏十金。没有人动。',
    beatNote: '历史考点：商鞅取信于民的政治智慧',
    tags: ['#古代史/商鞅变法', '#考频/⭐⭐⭐⭐⭐'],
    rawfile: 'pt039_ep09_03_南门立木.png',
    isSquare: false
  },
  {
    index: 4,
    sceneId: '墨骨山河_09_2_2',
    sceneName: '五十金之信',
    actTitle: '第二幕 · 南门立木',
    description: '赏金提高到五十金。一个穷汉搬走木头。五十金，一分不少，当场兑现。',
    beatNote: '历史考点：商鞅立木取信；法律必须被信仰',
    tags: ['#古代史/商鞅变法', '#考频/⭐⭐⭐⭐⭐'],
    rawfile: 'pt039_ep09_04_五十金兑现.png',
    isSquare: false
  },
  {
    index: 5,
    sceneId: '墨骨山河_09_2_4',
    sceneName: '渭水之刑',
    actTitle: '第二幕 · 南门立木',
    description: '太子犯法，商鞅刑其傅公子虔（劓刑）、师公孙贾（黥刑）。"法之不行，自上犯之。"',
    beatNote: '历史考点：法律面前人人平等；王子犯法与庶民同罪',
    tags: ['#古代史/商鞅变法', '#考频/⭐⭐⭐⭐⭐'],
    rawfile: 'pt039_ep09_05_渭水之刑.png',
    isSquare: false
  },
  {
    index: 6,
    sceneId: '墨骨山河_09_3_3',
    sceneName: '书同文 · 小篆',
    actTitle: '第三幕 · 法度山河',
    description: '秦始皇书同文，以小篆为标准字体。圆转均匀，对称平衡——法家美学在文字上的投影。',
    beatNote: '书法考点：小篆的书写特征 | 历史考点：书同文的历史意义',
    tags: ['#书法史/小篆', '#古代史/书同文', '#考频/⭐⭐⭐⭐'],
    rawfile: 'pt039_ep09_06_书同文.png',
    isSquare: true
  }
]

const IMG_DIR = '/data/storage/el2/base/files/history_gallery/'
const SCALE_MIN = 1.0
const SCALE_MAX = 4.0
// 滑动切换阈值（px，从触摸起点算起的最小位移）
const SWIPE_DIR_PIXELS = 30
// 滑动视觉阻尼系数（图片视觉位移 = 实际滑动 × 此系数，<1 产生阻尼感）
const SWIPE_VISUAL_DAMPING = 0.70

@Entry
@Component
struct HistoryGalleryPage {
  @State pixelMaps: PixelMap[] = [];
  @State isLoading: boolean = true;
  @State loadError: string = '';
  // 全屏查看
  @State fullscreenIndex: number = -1;
  @State isFs: boolean = false;
  @State scaleValue: number = 1;
  @State panAccX: number = 0;
  @State panAccY: number = 0;
  @State viewW: number = 360;
  @State viewH: number = 640;
  @State imgW: number = 1200;
  @State imgH: number = 800;
  @State showZoomBadge: boolean = false;
  private zoomBadgeTimer: number = -1;
  // 手势追踪
  private touchStartDist: number = 0;
  private touchPinchStartScale: number = 1;
  private touchIsPinch: boolean = false;
  private touchStartX: number = 0;
  private touchStartY: number = 0;
  // 滑动切换追踪（private 普通字段，避免 @State 时序问题）
  private touchIsSwiping: boolean = false;
  // 记录本次手势的"绝对起点"（用于全程方向判断）
  private touchOriginX: number = 0;
  private touchOriginY: number = 0;
  // 滑动时图片视觉反馈（private，普通变量，UI用 computed 值）
  private swipeOffset: number = 0;
  private hideTimer: number = -1;
  private controlsVisible: boolean = true;

  aboutToAppear(): void {
    this.initImages();
  }

  aboutToDisappear(): void {
    if (this.hideTimer >= 0) { clearTimeout(this.hideTimer); }
    if (this.zoomBadgeTimer >= 0) { clearTimeout(this.zoomBadgeTimer); }
  }

  async initImages(): Promise<void> {
    const ctx = getContext(this);
    const rm = ctx.resourceManager;
    try { fileIo.mkdirSync(IMG_DIR, true); } catch (_) {}
    const loaded: PixelMap[] = [];

    for (let i = 0; i < GALLERY_ITEMS.length; i++) {
      const item = GALLERY_ITEMS[i];
      const destPath = IMG_DIR + item.rawfile;
      try {
        const exists = fileIo.listFileSync(IMG_DIR).includes(item.rawfile);
        if (!exists) {
          const rawData: Uint8Array = await rm.getRawFileContent(item.rawfile);
          const fd: number = fileIo.openSync(destPath,
            fileIo.OpenMode.CREATE | fileIo.OpenMode.WRITE_ONLY).fd;
          fileIo.writeSync(fd, rawData.buffer as ArrayBuffer);
          fileIo.closeSync(fd);
        }
        const imageSource: image.ImageSource = image.createImageSource('file://' + destPath);
        const pixelMap: PixelMap = await imageSource.createPixelMap();
        loaded.push(pixelMap);

        // 第一张加载后取尺寸
        if (loaded.length === 1) {
          try {
            const info = await loaded[0].getImageInfo();
            if (info && info.size) {
              this.imgW = info.size.width > 0 ? info.size.width : 1200;
              this.imgH = info.size.height > 0 ? info.size.height : 800;
            }
          } catch (_) {}
        }
      } catch (e) {
        console.error('[Gallery] load failed: ' + item.rawfile + ' -> ' + JSON.stringify(e));
      }
    }

    this.pixelMaps = loaded;
    this.isLoading = false;
    if (loaded.length === 0) {
      this.loadError = '图片加载失败，请确认 rawfile 中已包含历史配图资源';
    }
  }

  openFullscreen(index: number): void {
    this.fullscreenIndex = index;
    this.isFs = true;
    this.scaleValue = 1;
    this.panAccX = 0;
    this.panAccY = 0;
    this.swipeOffset = 0;
    this.touchIsSwiping = false;
    this.scheduleHideControls();
  }

  closeFullscreen(): void {
    this.isFs = false;
    this.fullscreenIndex = -1;
    this.scaleValue = 1;
    this.panAccX = 0;
    this.panAccY = 0;
    this.swipeOffset = 0;
    this.touchIsSwiping = false;
    if (this.hideTimer >= 0) { clearTimeout(this.hideTimer); this.hideTimer = -1; }
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

  resetView(): void {
    animateTo({ duration: 250, curve: Curve.EaseOut }, () => {
      this.scaleValue = 1;
      this.panAccX = 0;
      this.panAccY = 0;
    });
    this.showZoomBadge = false;
  }

  setPanWithElastic(newPanX: number, newPanY: number): void {
    const scaledW = this.imgW * this.scaleValue;
    const scaledH = this.imgH * this.scaleValue;
    const overX = (scaledW - this.viewW) / 2;
    const overY = (scaledH - this.viewH) / 2;
    const maxPanX = Math.max(0, overX);
    const maxPanY = Math.max(0, overY);
    if (maxPanX > 0) {
      this.panAccX = Math.max(-maxPanX, Math.min(maxPanX, newPanX));
    } else {
      this.panAccX = 0;
    }
    if (maxPanY > 0) {
      this.panAccY = Math.max(-maxPanY, Math.min(maxPanY, newPanY));
    } else {
      this.panAccY = 0;
    }
  }

  showZoomBadgeFunc(): void {
    this.showZoomBadge = true;
    if (this.zoomBadgeTimer >= 0) { clearTimeout(this.zoomBadgeTimer); }
    this.zoomBadgeTimer = setTimeout(() => {
      this.showZoomBadge = false;
      this.zoomBadgeTimer = -1;
    }, 2000) as number;
  }

  prevFs(): void {
    if (this.fullscreenIndex > 0) {
      this.fullscreenIndex--;
    } else {
      this.fullscreenIndex = GALLERY_ITEMS.length - 1;
    }
    this.swipeOffset = 0;
    this.touchIsSwiping = false;
    this.resetView();
  }

  nextFs(): void {
    if (this.fullscreenIndex < GALLERY_ITEMS.length - 1) {
      this.fullscreenIndex++;
    } else {
      this.fullscreenIndex = 0;
    }
    this.swipeOffset = 0;
    this.touchIsSwiping = false;
    this.resetView();
  }

  @Builder
  FullscreenView() {
    Stack({ alignContent: Alignment.Bottom }) {
      // ── 图片层（全区域）─────────────────────
      Column() {
        if (this.pixelMaps[this.fullscreenIndex]) {
          Image(this.pixelMaps[this.fullscreenIndex])
            .width('100%').height('100%')
            .objectFit(ImageFit.Contain)
            .scale({ x: this.scaleValue, y: this.scaleValue, centerX: '50%', centerY: '50%' })
            .translate({ x: this.panAccX + this.swipeOffset, y: this.panAccY })
            .onTouch((event: TouchEvent) => {
              const touches = event.touches;
              const n = touches.length;

              // ── Down：初始化本次手势 ──────────────
              if (event.type === 0) {
                this.swipeOffset = 0;
                this.touchIsSwiping = false;
                if (n === 2) {
                  this.touchStartDist = Math.hypot(touches[1].x - touches[0].x, touches[1].y - touches[0].y);
                  this.touchPinchStartScale = this.scaleValue;
                  this.touchIsPinch = this.touchStartDist > 30;
                  // 两指时也记录起点（备用）
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
                      this.touchPinchStartScale = this.scaleValue;
                      this.touchIsPinch = true;
                    }
                  }
                  if (this.touchIsPinch && this.touchStartDist > 10) {
                    const dist = Math.hypot(touches[1].x - touches[0].x, touches[1].y - touches[0].y);
                    const ratio = dist / this.touchStartDist;
                    this.scaleValue = Math.max(SCALE_MIN, Math.min(SCALE_MAX, this.touchPinchStartScale * ratio));
                    this.setPanWithElastic(this.panAccX, this.panAccY);
                    this.showZoomBadgeFunc();
                  }
                  return;
                }

                // 单指 → 判断是竖向拖动还是横向滑动
                if (n === 1 && !this.touchIsPinch) {
                  const curX = touches[0].x;
                  const curY = touches[0].y;
                  // 计算相对于"手势绝对起点"的位移
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
                    // 用"当前X - 绝对起点X"判断全程方向
                    // 注意：curX 在 UP 时拿不到，用 swipeOffset（即 fromOriginX）
                    const totalX = this.swipeOffset;
                    if (totalX < -SWIPE_DIR_PIXELS) {
                      this.nextFs();
                    } else if (totalX > SWIPE_DIR_PIXELS) {
                      this.prevFs();
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
                // 此时 first finger 还在，也需要判断方向
                if (n === 1) {
                  const curX = touches[0].x;
                  const curY = touches[0].y;
                  const fromOriginX = curX - this.touchOriginX;
                  const fromOriginY = curY - this.touchOriginY;
                  const absX = Math.abs(fromOriginX);
                  const absY = Math.abs(fromOriginY);
                  // 如果单指时已有明显横向滑动，抬起时也判断
                  if (this.touchIsSwiping || absX > absY) {
                    if (fromOriginX < -SWIPE_DIR_PIXELS) {
                      this.nextFs();
                    } else if (fromOriginX > SWIPE_DIR_PIXELS) {
                      this.prevFs();
                    }
                  }
                  this.swipeOffset = 0;
                  this.touchIsSwiping = false;
                  // 切换为单指拖动模式
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
      .onAreaChange((_old, newVal) => {
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
            .onClick(() => this.closeFullscreen())
        }
        .width('100%').padding({ left: 16, right: 16, top: 12 })
        .position({ y: 0 })
        .transition(TransitionEffect.OPACITY.animation({ duration: 200 }))
      }

      // ── 底部控制栏（极薄）────────────────────
      if (this.controlsVisible) {
        Column() {
          // 缩放指示器（嵌入底部栏）
          if (this.showZoomBadge && this.scaleValue > 1.05) {
            Row() {
              Blank()
              Text(Math.round(this.scaleValue * 100).toString() + '%')
                .fontSize(12).fontColor('#D4B87A').fontWeight(600)
            }
            .width('100%').margin({ bottom: 6 })
          }

          // 翻页 + 场景信息
          Row() {
            Text('◀')
              .fontSize(15).fontColor('#FFFFFF')
              .padding(10)
              .backgroundColor('rgba(212,184,122,0.45)').borderRadius(10)
              .onClick(() => this.prevFs())

            Column() {
              Text(GALLERY_ITEMS[this.fullscreenIndex].sceneName)
                .fontSize(13).fontColor('#F5EDD8').fontWeight(600)
              Text(GALLERY_ITEMS[this.fullscreenIndex].actTitle)
                .fontSize(11).fontColor('#8A7A6A').margin({ top: 1 })
            }
            .layoutWeight(1)
            .alignItems(HorizontalAlign.Center)

            Text((this.fullscreenIndex + 1).toString() + ' / ' + GALLERY_ITEMS.length.toString())
              .fontSize(12).fontColor('#8A7A6A')
              .margin({ left: 6, right: 6 })

            Text('▶')
              .fontSize(15).fontColor('#FFFFFF')
              .padding(10)
              .backgroundColor('rgba(212,184,122,0.45)').borderRadius(10)
              .onClick(() => this.nextFs())
          }
          .width('100%')
        }
        .width('100%')
        .padding({ left: 16, right: 16, top: 8, bottom: 28 })
        .backgroundColor('rgba(26,14,8,0.75)')
        .transition(TransitionEffect.OPACITY.animation({ duration: 200 }))
      }
    }
    .width('100%').height('100%').backgroundColor('#0A0604')
  }

  @Builder
  GalleryGrid() {
    Column() {
      // 顶部导航
      Row() {
        Text('← 返回')
          .fontSize(15).fontColor('#C44536')
          .onClick(() => router.back())
        Blank()
        Text('历史AI配图')
          .fontSize(18).fontWeight(600).fontColor('#1a1a1a')
        Blank()
        Text('AI')
          .fontSize(11).fontColor('#C44536')
          .backgroundColor('#fff0f0').borderRadius(8)
          .padding({ left: 6, right: 6, top: 2, bottom: 2 })
      }
      .width('100%').padding({ left: 16, right: 16, top: 16, bottom: 12 })
      .backgroundColor(Color.White)

      if (this.isLoading) {
        Column() {
          LoadingProgress().width(40).height(40)
          Text('加载历史配图中...')
            .fontSize(13).fontColor('#aaa').margin({ top: 12 })
        }
        .width('100%').margin({ top: 100 })
      } else if (this.loadError) {
        Column() {
          Text('⚠ ' + this.loadError)
            .fontSize(13).fontColor('#C44536').textAlign(TextAlign.Center)
        }
        .width('100%').margin({ top: 80 })
      } else {
        Scroll() {
          Column() {
            // ep09 标题卡
            Column() {
              Text('墨骨山河 · 第九集')
                .fontSize(10).fontColor('#D4B87A').letterSpacing(2)
              Text('南门之木')
                .fontSize(22).fontWeight(700).fontColor('#F5EDD8').margin({ top: 4 })
              Text('商鞅变法 · 战国秩序的诞生')
                .fontSize(13).fontColor('#C49A6C').margin({ top: 2 })
              Text('公元前359年 · 秦国栎阳 · 高考考点：HIS-AS-004/005/006/010')
                .fontSize(11).fontColor('#8A7A6A').margin({ top: 6 })
            }
            .width('100%').padding(20)
            .backgroundColor('#1A0E08').borderRadius(16)
            .margin({ left: 16, right: 16, bottom: 16 })

            // 网格
            Column() {
              ForEach(GALLERY_ITEMS, (item: GalleryItem, idx: number) => {
                Column() {
                  // 缩略图
                  Stack() {
                    if (this.pixelMaps[idx]) {
                      Image(this.pixelMaps[idx])
                        .width('100%')
                        .aspectRatio(item.isSquare ? 1 : 16 / 9)
                        .objectFit(ImageFit.Cover)
                    } else {
                      Column() {
                        Text('图' + (idx + 1).toString())
                          .fontSize(20).fontColor('#3a2a1a')
                      }
                      .width('100%')
                      .aspectRatio(item.isSquare ? 1 : 16 / 9)
                      .backgroundColor('#2a1a0a')
                    }

                    // 剧幕角标
                    Text(item.actTitle)
                      .fontSize(10).fontColor('#F5EDD8')
                      .backgroundColor('rgba(26,14,8,0.75)').borderRadius(6)
                      .padding({ left: 6, right: 6, top: 2, bottom: 2 })
                      .position({ x: 8, y: 8 })

                    // 播放图标
                    Column() {
                      Text('▶')
                        .fontSize(18).fontColor('rgba(255,255,255,0.85)')
                    }
                    .width(36).height(36)
                    .backgroundColor('rgba(0,0,0,0.5)').borderRadius(18)
                    .alignItems(HorizontalAlign.Center).justifyContent(FlexAlign.Center)
                    .position({ x: '50%', y: '50%' }).translate({ x: -18, y: -18 })
                  }
                  .width('100%')
                  .borderRadius(12)
                  .clip(true)
                  .onClick(() => this.openFullscreen(idx))

                  // 场景说明
                  Column() {
                    Row() {
                      Text(item.index.toString() + '.')
                        .fontSize(11).fontColor('#D4B87A').fontWeight(600)
                      Text(item.sceneName)
                        .fontSize(14).fontWeight(600).fontColor('#F5EDD8').margin({ left: 4 })
                    }.width('100%').margin({ bottom: 4 })

                    Text(item.description)
                      .fontSize(12).fontColor('#8A7A6A').lineHeight(18)

                    Text(item.beatNote)
                      .fontSize(11).fontColor('#5A4A38').margin({ top: 4 })

                    // 标签
                    Row() {
                      ForEach(item.tags, (tag: string) => {
                        Text(tag)
                          .fontSize(10).fontColor('#8A7A6A')
                          .backgroundColor('#2a1a0a').borderRadius(6)
                          .padding({ left: 6, right: 6, top: 2, bottom: 2 })
                          .margin({ right: 4 })
                      })
                    }
                    .margin({ top: 6 })
                  }
                  .width('100%').padding({ left: 4, right: 4, top: 10, bottom: 4 })
                }
                .width('100%')
                .backgroundColor('#1A0E08').borderRadius(16)
                .margin({ bottom: 12 })
                .padding(12)
              })
            }
            .padding({ left: 16, right: 16, bottom: 24 })

            // 底部说明
            Column() {
              Text('本页面为 PT-039 AI 配图探索窗口产出')
                .fontSize(11).fontColor('#5A4A38')
              Text('AI-generated illustration, for educational reference only · 墨骨山河 ep09 · 商鞅变法 · 高考历史 × 书法史跨学科缝合')
                .fontSize(10).fontColor('#3a2a1a').margin({ top: 4 })
            }
            .width('100%').padding({ left: 16, right: 16, bottom: 32 })
            .alignItems(HorizontalAlign.Center)
          }
        }
        .layoutWeight(1).scrollBar(BarState.Off)
      }
    }
    .width('100%').height('100%').backgroundColor('#F5F0E8')
  }

  build() {
    Stack() {
      this.GalleryGrid()
      if (this.isFs) {
        this.FullscreenView()
      }
    }
    .width('100%').height('100%')
  }
}
