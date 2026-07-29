/**
 * 入境 APP · 链阅读器（核心页面）
 * 剧本式阅读 + 全屏沉浸卡片翻转
 */

import { router } from '@kit.ArkUI';
import { promptAction } from '@kit.ArkUI';
import { BusinessError } from '@kit.BasicServicesKit';
import { dlog } from '../service/DebugLogService';
import { util } from '@kit.ArkTS';
import { db } from '../service/DatabaseService';
import { getChainNarrative, findVideoForChain, VideoEpisode, SceneTimelineEntry } from '../service/ImportService';
import { mediaService, videoService, PlayState, MediaPlayerState, VideoErrorInfo, setLogContext } from '../service/MediaService';
import { Chain, Card, Maturity, MediaRef, MediaType } from '../model/DataModel';
import { window } from '@kit.ArkUI';

/** 设置窗口方向（横屏/竖屏） */
function setWindowOrientation(landscape: boolean): void {
  try {
    const ctx = getContext();
    const win = window.getLastWindow(ctx);
    // setPreferredOrientation 是 Promise 方法
    win.then((w: window.Window) => {
      w.setPreferredOrientation(landscape
        ? window.Orientation.LANDSCAPE
        : window.Orientation.PORTRAIT);
      dlog('ORIENT', landscape ? '→LANDSCAPE' : '→PORTRAIT');
    }).catch((e: BusinessError) => {
      dlog('ORIENT', 'FAIL: ' + e.code + ' ' + e.message);
    });
  } catch (e) {
    const err = e as BusinessError;
    dlog('ORIENT', 'FAIL: ' + err.code + ' ' + err.message);
  }
}

interface AudioMetaItem {
  ep: number
  ep_title: string
  audio_file: string
  chains: string[]
}

const AUDIO_BASE: string = '/data/storage/el2/base/files/rujing_audio/';
let audioMetaCache: AudioMetaItem[] | null = null;

@Entry
@Component
struct ChainReaderPage {
  @State chainId: string = '';
  @State chainTitle: string = '';
  @State narrative: string = '';
  @State cards: Card[] = [];
  @State rawCards: Card[] = [];
  @State currentCardIndex: number = -1;
  @State showCard: boolean = false;
  @State showBack: boolean = false;
  @State playState: PlayState = PlayState.IDLE;
  @State loading: boolean = true;

  @State audioFile: string = '';
  @State audioTitle: string = '';
  @State videoEpisode: VideoEpisode | null = null;
  @State videoFile: string = '';
  @State videoTitle: string = '';
  @State videoState: PlayState = PlayState.IDLE;
  @State videoError: VideoErrorInfo | null = null;
  @State showVideoOverlay: boolean = false;
  @State sceneTimeline: SceneTimelineEntry[] = [];
  @State jumpToTime: number = -1;  // ms, -1 = not jumping

  // ── Video 播放器专用状态（Video 系统组件）───────────────
  @State showVideoPlayer: boolean = false;
  @State videoCurTime: number = 0;    // 秒
  @State videoDuration: number = 0;   // 秒
  @State videoIsPlaying: boolean = false;
  @State isLandscape: boolean = false;  // 横屏状态
  videoController: VideoController = new VideoController();

  aboutToAppear(): void {
    const params: Record<string, Object> = router.getParams() as Record<string, Object>;
    this.chainId = (params['chain_id'] as string) ?? '';
    this.loadChain();
    mediaService.onStateChange((s: MediaPlayerState) => { this.playState = s.state; });
    videoService.onStateChange((s: MediaPlayerState) => { this.videoState = s.state; });
    // 注入 context 让 dlog 能正确写文件
    setLogContext(getContext(this));
    // 监听播放错误
    videoService.onError((e: VideoErrorInfo | null) => { this.videoError = e; });
  }

  aboutToDisappear(): void {
    mediaService.release();
    videoService.release();
    // 离开页面时恢复竖屏
    if (this.showVideoPlayer || this.isLandscape) {
      setWindowOrientation(false);
    }
  }

  async loadChain(): Promise<void> {
    const chain = await db.getChain(this.chainId);
    if (chain) { this.chainTitle = chain.title; }
    this.narrative = getChainNarrative(this.chainId);
    this.cards = await db.getCardsByChain(this.chainId);
    this.rawCards = this.cards.filter(c => c.maturity === Maturity.RAW);
    await db.updateChainViewed(this.chainId);

    // 加载音频映射
    await this.loadAudioMeta();

    // 加载视频元数据（v2 新增）
    await this.loadVideoMeta();

    this.loading = false;
  }

  async loadAudioMeta(): Promise<void> {
    if (!audioMetaCache) {
      try {
        const ctx = getContext(this);
        const rawData: Uint8Array = await ctx.resourceManager.getRawFileContent('audio_meta.json');
        const decoder: util.TextDecoder = util.TextDecoder.create('utf-8', { ignoreBOM: true });
        audioMetaCache = JSON.parse(decoder.decodeToString(rawData)) as AudioMetaItem[];
      } catch (_) {
        audioMetaCache = [];
      }
    }

    for (const item of audioMetaCache ?? []) {
      if (item.chains.includes(this.chainId)) {
        this.audioFile = AUDIO_BASE + item.audio_file;
        this.audioTitle = 'Ep' + item.ep + ' ' + item.ep_title;
        return;
      }
    }
    this.audioFile = '';
    this.audioTitle = '';
  }

  async loadVideoMeta(): Promise<void> {
    // 从已导入的视频包中查找本 chain 对应的视频
    const ep = await findVideoForChain(this.chainId);
    if (ep) {
      this.videoEpisode = ep;
      // video_file 是沙箱绝对路径，Video 组件需要 file:// 前缀
      const rawPath = ep.video_file || '';
      this.videoFile = rawPath.startsWith('/data/') ? 'file://' + rawPath : rawPath;
      this.videoTitle = 'Ep' + ep.ep + ' ' + ep.title;
      this.sceneTimeline = ep.scene_timeline ?? [];
    } else {
      this.videoEpisode = null;
      this.videoFile = '';
      this.videoTitle = '';
      this.sceneTimeline = [];
    }
  }

  /**
   * 跳转到指定 scene（来自 scene_timeline）
   * 使用 Video 组件的 VideoController 直接跳转
   */
  jumpToScene(entry: SceneTimelineEntry): void {
    if (!this.videoController) return;
    // VideoController.setCurrentTime() 参数单位是毫秒，entry.time 是秒
    this.videoController.setCurrentTime(entry.time * 1000);
    this.showVideoOverlay = false;
  }

  /** 格式化时间显示 mm:ss */
  formatTime(seconds: number): string {
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    return m.toString().padStart(2, '0') + ':' + s.toString().padStart(2, '0');
  }

  pickCard(): void {
    this.rawCards = this.cards.filter(c => c.maturity === Maturity.RAW);
    if (this.rawCards.length > 0) {
      const idx = Math.floor(Math.random() * this.rawCards.length);
      this.currentCardIndex = this.cards.findIndex(c => c.card_id === this.rawCards[idx].card_id);
      this.showCard = true;
      this.showBack = true;
    }
  }

  async markMaturity(maturity: Maturity): Promise<void> {
    const card = this.cards[this.currentCardIndex];
    if (!card) return;
    await db.markMaturity(card.card_id, maturity);
    card.maturity = maturity;
    this.rawCards = this.cards.filter(c => c.maturity === Maturity.RAW);
    if (this.rawCards.length > 0) {
      setTimeout(() => this.pickCard(), 400);
    } else {
      this.showCard = false;
    }
  }

  build() {
    Column() {
      Row() {
        Image($r('app.media.startIcon')).width(20).height(20).fillColor('#333')
          .onClick(() => { mediaService.release(); router.back(); })
        Text(this.chainTitle).fontSize(16).fontWeight(600).fontColor('#1a1a1a')
          .maxLines(1).textOverflow({ overflow: TextOverflow.Ellipsis })
          .layoutWeight(1).margin({ left: 8, right: 8 })
        Text('AI').fontSize(13).fontWeight(600).fontColor('#5B8C5A')
          .padding({ left: 10, right: 10, top: 4, bottom: 4 })
          .border({ width: 1, color: '#5B8C5A', radius: 12 })
          .onClick(() => router.pushUrl({
            url: 'pages/AIPanelPage',
            params: { chain_id: this.chainId, card_id: this.cards.length > 0 ? this.cards[0].card_id : '' }
          }))
      }
      .width('100%').padding(14)

      if (this.loading) {
        LoadingProgress().width(36).height(36).margin({ top: 100 })
      } else {
        Scroll() {
          Column({ space: 16 }) {
            // 叙事文本
            Column() {
              Text(this.narrative || '（暂无叙事文本，请导入链元数据）')
                .fontSize(15).fontColor('#333').lineHeight(26)
                .textAlign(TextAlign.Start).width('100%')
            }
            .width('100%').padding(20).backgroundColor(Color.White).borderRadius(12)

            // 卡片列表
            Column() {
              Text('知识点卡片 (' + this.cards.length + ' 张)')
                .fontSize(15).fontWeight(600).fontColor('#1a1a1a')
                .alignSelf(ItemAlign.Start).margin({ bottom: 10 })

              if (this.cards.length === 0) {
                Text('暂无卡片').fontSize(13).fontColor('#999')
                  .width('100%').textAlign(TextAlign.Center).padding(20)
              }

              ForEach(this.cards, (card: Card, index: number) => {
                Button() {
                  Row() {
                    Column() {
                      Text(card.front).fontSize(14).fontColor('#333')
                        .maxLines(2).textOverflow({ overflow: TextOverflow.Ellipsis })
                      Text(card.back_core).fontSize(12).fontColor('#999')
                        .maxLines(1).textOverflow({ overflow: TextOverflow.Ellipsis }).margin({ top: 4 })
                    }
                    .alignItems(HorizontalAlign.Start).layoutWeight(1)
                    Text(card.maturity === Maturity.RAW ? '生' : '熟').fontSize(12)
                      .fontColor(card.maturity === Maturity.RAW ? '#e67e22' : '#5B8C5A')
                      .padding({ left: 10, right: 10, top: 4, bottom: 4 })
                      .backgroundColor(card.maturity === Maturity.RAW ? '#fff3e0' : '#f0fdf4')
                      .borderRadius(10)
                  }.width('100%')
                }
                .type(ButtonType.Normal).backgroundColor(Color.Transparent)
                .width('100%').padding(12)
                .border({ width: { bottom: 1 }, color: '#f0f0f0' }).borderRadius(0)
                .onClick(() => { this.currentCardIndex = index; this.showCard = true; this.showBack = true; })
              }, (card: Card) => card.card_id)

              if (this.rawCards.length > 0) {
                Button('随机抽查 (' + this.rawCards.length + ' 张待复习)')
                  .fontSize(14).backgroundColor('#5B8C5A').borderRadius(20)
                  .width('70%').margin({ top: 16 }).onClick(() => this.pickCard())
              }
            }
            .width('100%').padding(16).backgroundColor(Color.White).borderRadius(12)

            this.videoBar()

            this.audioBar()
          }.padding({ top: 16, bottom: 32 })
        }
        .layoutWeight(1).scrollBar(BarState.Off)
      }

      // 全屏卡片
      if (this.showCard && this.currentCardIndex >= 0 && this.currentCardIndex < this.cards.length) {
        this.cardOverlay()
      }

      // scene_timeline 跳转浮层（IF-B v2）
      if (this.showVideoOverlay) {
        this.sceneTimelineOverlay()
      }

      // ── 全屏视频播放器（Video 系统组件，自动处理 surfaceId）────
      if (this.showVideoPlayer && this.videoFile) {
        this.videoPlayerOverlay()
      }
    }
    .width('100%').height('100%').backgroundColor('#F5F5F5')
  }

  @Builder
  videoBar() {
    Row() {
      Image($r('app.media.startIcon')).width(20).height(20)
        .fillColor(this.videoState === PlayState.PLAYING ? '#5B8C5A' : '#999')

      if (this.videoFile) {
        Text((this.videoTitle || '配套视频') + ' [' + this.videoFile.slice(-30) + ']').fontSize(11).fontColor('#888')
          .margin({ left: 8 }).layoutWeight(1)

        if (this.videoError) {
          // 错误内联展示（T3 可测性设计）
          Text('⚠ ' + this.videoError.tier + ': ' + this.videoError.reason + ' | ' + this.videoError.detail)
            .fontSize(10).fontColor('#e74c3c')
            .width('100%').margin({ left: 8, top: 4 })
        }

        if (this.videoState === PlayState.PLAYING) {
          Button('暂停').fontSize(11).backgroundColor('#fff0f0').fontColor('#c0392b')
            .borderRadius(12).height(28).onClick(() => videoService.pause())
        } else if (this.videoState === PlayState.PAUSED) {
          Button('继续').fontSize(11).backgroundColor('#5B8C5A').fontColor(Color.White)
            .borderRadius(12).height(28).onClick(() => videoService.resume())
        } else {
          Button(this.videoError ? '播放失败↻' : '播放').fontSize(11)
            .backgroundColor(this.videoError ? '#fff3e0' : '#5B8C5A')
            .fontColor(this.videoError ? '#e67e22' : Color.White)
            .borderRadius(12).height(28)
            .onClick(() => {
              if (!this.videoEpisode || !this.videoFile) return;
              videoService.clearError();
              this.videoError = null;
              // 打开全屏 Video 播放器，初始化 duration
              this.videoCurTime = 0;
              this.videoDuration = this.videoEpisode.duration_seconds ?? 0;
              this.showVideoPlayer = true;
              // 视频是 1920x1080 横屏 → 自动切横屏播放
              this.isLandscape = true;
              setWindowOrientation(true);
              promptAction.showToast({ message: '正在打开视频播放器…', duration: 1500 });
              dlog('PLAY', 'open video player. file=' + this.videoFile + ' duration=' + this.videoDuration);
            })
        }

        if (this.sceneTimeline.length > 0) {
          Button('跳转复习(' + this.sceneTimeline.length + ')').fontSize(11)
            .backgroundColor('#f0f4ff').fontColor('#4a6cf7')
            .borderRadius(12).height(28)
            .onClick(() => { this.showVideoOverlay = true; })
        } else {
          Button('跳转复习').fontSize(11).backgroundColor('#f5f5f5').fontColor('#ccc')
            .borderRadius(12).height(28)
        }
      } else {
        Text('暂无配套视频').fontSize(13).fontColor('#aaa')
          .margin({ left: 8 }).layoutWeight(1)
      }
    }
    .width('100%').padding(12).backgroundColor(Color.White).borderRadius(10)
    .margin({ left: 20, right: 20 })
  }

  @Builder
  audioBar() {
    Row() {
      Image($r('app.media.startIcon')).width(20).height(20)
        .fillColor(this.playState === PlayState.PLAYING ? '#5B8C5A' : '#999')

      if (this.audioFile) {
        Text(this.audioTitle).fontSize(13).fontColor('#333')
          .margin({ left: 8 }).layoutWeight(1)

        if (this.playState === PlayState.PLAYING) {
          Button('暂停').fontSize(11).backgroundColor('#fff0f0').fontColor('#c0392b')
            .borderRadius(12).height(28).onClick(() => mediaService.pause())
        } else if (this.playState === PlayState.PAUSED) {
          Button('继续').fontSize(11).backgroundColor('#5B8C5A').fontColor(Color.White)
            .borderRadius(12).height(28).onClick(() => mediaService.resume())
        } else {
          Button('播放').fontSize(11).backgroundColor('#5B8C5A').fontColor(Color.White)
            .borderRadius(12).height(28)
            .onClick(() => {
              const ref: MediaRef = { type: MediaType.AUDIO, src: this.audioFile, title: this.audioTitle, chain_id: this.chainId };
              mediaService.playAudio(ref);
            })
        }
      } else {
        Text('暂无配套音频').fontSize(13).fontColor('#aaa')
          .margin({ left: 8 }).layoutWeight(1)
      }
    }
    .width('100%').padding(12).backgroundColor(Color.White).borderRadius(10).margin({ left: 20, right: 20 })
  }


  swipeNext(): void {
    if (this.currentCardIndex < this.cards.length - 1) {
      this.currentCardIndex++;
      this.showBack = true;
    }
  }

  swipePrev(): void {
    if (this.currentCardIndex > 0) {
      this.currentCardIndex--;
      this.showBack = true;
    }
  }
  // ── 全屏视频播放器（Video 系统组件）────────────────────
  // Video 是 ArkUI 内置组件，自动处理 surfaceId，无需手动绑定
  // VideoController 控制播放，scene timeline 提供跳转
  @Builder
  videoPlayerOverlay() {
    Column() {
      // 顶部栏：关闭 + 标题
      Row() {
        Text('✕').fontSize(22).fontColor(Color.White)
          .onClick(() => {
            this.showVideoPlayer = false;
            this.videoIsPlaying = false;
            this.videoController.pause();
            this.isLandscape = false;
            setWindowOrientation(false);
          })
        Text(this.videoTitle || '配套视频').fontSize(15).fontColor(Color.White)
          .margin({ left: 12 }).layoutWeight(1)
          .maxLines(1).textOverflow({ overflow: TextOverflow.Ellipsis })
        // 横/竖屏切换
        Text(this.isLandscape ? '⊟' : '⊞').fontSize(18).fontColor(Color.White)
          .padding({ left: 8, right: 8 })
          .onClick(() => {
            this.isLandscape = !this.isLandscape;
            setWindowOrientation(this.isLandscape);
            dlog('ORIENT', 'manual toggle: ' + (this.isLandscape ? 'landscape' : 'portrait'));
          })
        // scene timeline 入口
        if (this.sceneTimeline.length > 0) {
          Text('跳转(' + this.sceneTimeline.length + ')').fontSize(12)
            .fontColor('#4a6cf7').backgroundColor(Color.White).borderRadius(10)
            .padding({ left: 10, right: 10, top: 4, bottom: 4 })
            .onClick(() => { this.showVideoOverlay = true; })
        }
      }
      .width('100%').padding(16)
      .backgroundColor('rgba(0,0,0,0.6)')

      // Video 播放器（全屏自适应）
      Column() {
        Video({
          src: this.videoFile,
          currentProgressRate: 1,
          controller: this.videoController
        })
          .width('100%')
          .layoutWeight(1)
          .autoPlay(false)
          .controls(false)   // 隐藏默认控件，用自定义
          .onPrepared((info: PreparedInfo) => {
            this.videoDuration = info.duration;
            dlog('VIDEO', 'onPrepared duration=' + info.duration + ' src=' + this.videoFile);
          })
          .onStart(() => {
            this.videoIsPlaying = true;
            dlog('VIDEO', 'onStart');
          })
          .onPause(() => {
            this.videoIsPlaying = false;
            dlog('VIDEO', 'onPause');
          })
          .onFinish(() => {
            this.videoIsPlaying = false;
            this.videoCurTime = 0;
            dlog('VIDEO', 'onFinish');
          })
          .onSeeking(() => {
            dlog('VIDEO', 'onSeeking');
          })
          .onSeeked(() => {
            dlog('VIDEO', 'onSeekDone');
          })
          .onError((err: BusinessError) => {
            const code = err.code !== undefined ? err.code : -1;
            const msg = err.message !== undefined ? err.message : String(err);
            dlog('VIDEO', 'onError code=' + code + ' msg=' + msg);
            promptAction.showToast({ message: '视频异常: [' + code + '] ' + msg, duration: 3000 });
          })
      }
      .width('100%').layoutWeight(1).backgroundColor(Color.Black)

      // 底部控制栏：播放/暂停 + 时间 + scene timeline
      Column() {
        // 进度条（点击/拖动可跳转，slider 交互时同步更新显示时间）
        Row() {
          Text(this.formatTime(this.videoCurTime)).fontSize(11).fontColor('#ccc')
          Slider({
            value: this.videoCurTime,
            min: 0,
            max: this.videoDuration > 0 ? this.videoDuration : 1,
            step: 1,
            style: SliderStyle.OutSet
          })
            .blockColor('#4a6cf7')
            .trackColor('#444')
            .selectedColor('#4a6cf7')
            .showTips(false)
            .onChange((value: number, mode: SliderChangeMode) => {
              // 拖动或松开时跳转；用户拖动时同步更新显示时间
              // 注意：setCurrentTime 期望毫秒，slider value 和 videoCurTime 都是秒
              if (mode === SliderChangeMode.End || mode === SliderChangeMode.Moving) {
                this.videoCurTime = value;
                this.videoController.setCurrentTime(value * 1000);
              }
            })
          Text(this.formatTime(this.videoDuration)).fontSize(11).fontColor('#ccc')
        }
        .width('100%').padding({ left: 16, right: 16 })

        // 播放/暂停 + scene timeline 快捷跳转
        Row() {
          // 播放/暂停
          if (this.videoIsPlaying) {
            Text('⏸ 暂停').fontSize(14).fontColor(Color.White)
              .padding({ left: 12, right: 12, top: 6, bottom: 6 })
              .backgroundColor('rgba(255,255,255,0.15)').borderRadius(8)
              .onClick(() => { this.videoIsPlaying = false; this.videoController.pause(); })
          } else {
            Text('▶ 播放').fontSize(14).fontColor(Color.White)
              .padding({ left: 12, right: 12, top: 6, bottom: 6 })
              .backgroundColor('#4a6cf7').borderRadius(8)
              .onClick(() => { this.videoIsPlaying = true; this.videoController.start(); })
          }

          // -10s / +10s 快捷
          Text('-10s').fontSize(12).fontColor('#ccc')
            .padding({ left: 8, right: 8, top: 4, bottom: 4 })
            .backgroundColor('rgba(255,255,255,0.1)').borderRadius(6)
            .onClick(() => {
              const t = Math.max(0, this.videoCurTime - 10);
              this.videoController.setCurrentTime(t * 1000);
            })
          Text('+10s').fontSize(12).fontColor('#ccc')
            .padding({ left: 8, right: 8, top: 4, bottom: 4 })
            .backgroundColor('rgba(255,255,255,0.1)').borderRadius(6)
            .onClick(() => {
              const t = Math.min(this.videoDuration, this.videoCurTime + 10);
              this.videoController.setCurrentTime(t * 1000);
            })

          Blank()

          Text('关闭').fontSize(13).fontColor('#ccc')
            .padding({ left: 12, right: 12, top: 6, bottom: 6 })
            .onClick(() => {
              this.showVideoPlayer = false;
              this.videoIsPlaying = false;
              this.videoController.pause();
              this.isLandscape = false;
              setWindowOrientation(false);
            })
        }
        .width('100%').padding({ left: 16, right: 16, top: 8, bottom: 16 })

        // scene timeline 横向滚动条
        if (this.sceneTimeline.length > 0) {
          Scroll() {
            Row({ space: 8 }) {
              ForEach(this.sceneTimeline, (entry: SceneTimelineEntry) => {
                Column() {
                  Text(this.formatTime(entry.time))
                    .fontSize(10).fontColor('#4a6cf7')
                    .backgroundColor('#f0f4ff').borderRadius(6)
                    .padding({ left: 6, right: 6, top: 2, bottom: 2 })
                  Text(entry.scene_name || ('Scene ' + entry.idx))
                    .fontSize(10).fontColor(Color.White)
                    .maxLines(1).textOverflow({ overflow: TextOverflow.Ellipsis })
                    .width('100%')
                }
                .alignItems(HorizontalAlign.Start)
                .padding(8)
                .backgroundColor('rgba(255,255,255,0.1)').borderRadius(8)
                .width(120)
                .onClick(() => {
                  this.videoController.setCurrentTime(entry.time);
                  this.showVideoOverlay = false;
                })
              }, (entry: SceneTimelineEntry) => entry.idx.toString())
            }
          }
          .width('100%').height(56)
          .scrollBar(BarState.Auto)
          .padding({ left: 16, right: 16, bottom: 16 })
        }
      }
      .width('100%')
      .backgroundColor('rgba(0,0,0,0.8)')
    }
    .width('100%').height('100%')
    .backgroundColor(Color.Black)
    .position({ x: 0, y: 0 })
  }

  // ── scene_timeline 跳转浮层（IF-B v2）────────────────
  @Builder
  sceneTimelineOverlay() {
    Column() {
      // 标题栏
      Row() {
        Text('跳转复习').fontSize(17).fontWeight(600).fontColor('#1a1a1a')
          .layoutWeight(1)
        Text('✕').fontSize(18).fontColor('#999')
          .onClick(() => { this.showVideoOverlay = false; })
      }
      .width('100%').padding({ left: 20, right: 16, top: 16, bottom: 12 })

      if (this.sceneTimeline.length === 0) {
        Column() {
          Text('暂无 scene_timeline 数据').fontSize(14).fontColor('#999')
          Text('请先在导入页导入视频包元数据').fontSize(12).fontColor('#ccc').margin({ top: 8 })
        }
        .width('100%').padding(40).alignItems(HorizontalAlign.Center)
      } else {
        Scroll() {
          Column({ space: 8 }) {
            ForEach(this.sceneTimeline, (entry: SceneTimelineEntry) => {
              Row() {
                // 时间标签
                Text(this.formatTime(entry.time))
                  .fontSize(12).fontColor('#4a6cf7')
                  .backgroundColor('#f0f4ff').borderRadius(6)
                  .padding({ left: 8, right: 8, top: 4, bottom: 4 })
                  .margin({ right: 12 })

                // scene 名称
                Column() {
                  Text(entry.scene_name || 'Scene ' + entry.idx.toString())
                    .fontSize(14).fontColor('#1a1a1a')
                    .maxLines(2).textOverflow({ overflow: TextOverflow.Ellipsis })
                    .width('100%').textAlign(TextAlign.Start)
                  if (entry.scene_type) {
                    Text(entry.scene_type)
                      .fontSize(11).fontColor('#aaa').margin({ top: 2 })
                  }
                }
                .alignItems(HorizontalAlign.Start).layoutWeight(1)

                // 五蕴提示（如果有）
                if (entry.five_skandha?.action_prompt) {
                  Text(entry.five_skandha.action_prompt)
                    .fontSize(10).fontColor('#5B8C5A')
                    .backgroundColor('#f0fdf4').borderRadius(6)
                    .padding({ left: 6, right: 6, top: 2, bottom: 2 })
                    .margin({ left: 8 })
                }

                Text('▶').fontSize(14).fontColor('#4a6cf7').margin({ left: 8 })
              }
              .width('100%').padding(12)
              .backgroundColor(Color.White).borderRadius(10)
              .border({ width: 1, color: '#f0f0f8' })
              .onClick(() => { this.jumpToScene(entry); })
            }, (entry: SceneTimelineEntry) => entry.idx.toString())
          }
          .padding({ left: 16, right: 16, bottom: 32 })
        }
        .layoutWeight(1).scrollBar(BarState.Auto)
      }
    }
    .width('100%').height('75%')
    .backgroundColor('#FAFAFA').borderRadius({ topLeft: 20, topRight: 20 })
    .position({ x: 0, y: '25%' })
  }

  @Builder
  cardOverlay() {
    Column() {
      Row() {
        Text('← 返回').fontSize(14).fontColor('#999')
          .onClick(() => { this.showCard = false; })
        Blank()
        Text(this.showBack ? '看问题' : '看答案').fontSize(14).fontColor('#5B8C5A')
          .padding({ left: 12, right: 12, top: 6, bottom: 6 })
          .border({ width: 1, color: '#5B8C5A', radius: 14 })
          .onClick(() => { this.showBack = !this.showBack; })
      }.width('100%').padding(16)

      Column() {
        if (!this.showBack) {
          Text(this.cards[this.currentCardIndex].front)
            .fontSize(22).fontWeight(600).fontColor('#1a1a1a')
            .textAlign(TextAlign.Center).width('100%').lineHeight(32)
        } else {
          Scroll() {
            Column({ space: 16 }) {
              Text(this.cards[this.currentCardIndex].back_core || this.cards[this.currentCardIndex].back_detail || '（暂无内容）')
                .fontSize(18).fontWeight(600).fontColor('#1a1a1a')
                .textAlign(TextAlign.Center).width('100%').lineHeight(28)
              if (this.cards[this.currentCardIndex].back_detail && this.cards[this.currentCardIndex].back_detail !== this.cards[this.currentCardIndex].back_core) {
                Text(this.cards[this.currentCardIndex].back_detail)
                  .fontSize(14).fontColor('#666').textAlign(TextAlign.Start)
                  .width('100%').lineHeight(24)
              }
            }.width('100%')
          }.layoutWeight(1)
        }
      }
      .layoutWeight(1).justifyContent(FlexAlign.Center).padding(24)

      // 上一张 / 下一张
      Row({ space: 8 }) {
        Text('◀ 上一张').fontSize(13).fontColor('#999')
          .padding({ left: 12, right: 12, top: 8, bottom: 8 })
          .onClick(() => { this.swipePrev(); })
        Text(this.currentCardIndex + 1 + ' / ' + this.cards.length).fontSize(13).fontColor('#ccc')
          .textAlign(TextAlign.Center).layoutWeight(1)
        Text('下一张 ▶').fontSize(13).fontColor('#5B8C5A')
          .padding({ left: 12, right: 12, top: 8, bottom: 8 })
          .onClick(() => { this.swipeNext(); })
      }.width('100%').padding({ left: 20, right: 20, bottom: 8 })

      if (this.showBack) {
        Row({ space: 16 }) {
          Button('不熟').fontSize(16).backgroundColor('#fff0f0').fontColor('#c0392b')
            .borderRadius(24).layoutWeight(1).height(48)
            .onClick(() => this.markMaturity(Maturity.RAW))
          Button('熟了').fontSize(16).backgroundColor('#5B8C5A').fontColor(Color.White)
            .borderRadius(24).layoutWeight(1).height(48)
            .onClick(() => this.markMaturity(Maturity.COOKED))
        }.width('100%').padding({ left: 20, right: 20, bottom: 40 })
      }
    }
    .width('100%').height('100%').backgroundColor('#FAFAFA')
    .position({ x: 0, y: 0 })
  }
}
