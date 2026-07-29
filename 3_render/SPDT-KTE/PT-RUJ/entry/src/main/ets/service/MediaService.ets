/**
 * 入境 APP · 媒体服务
 * 音频播放（首版 P0）+ 视频接口预留（P1）
 */

import { MediaRef, MediaType } from '../model/DataModel';
import { media } from '@kit.MediaKit';
import { fileIo } from '@kit.CoreFileKit';
import { application } from '@kit.AbilityKit';
import { util } from '@kit.ArkTS';
import { BusinessError } from '@kit.BasicServicesKit';

// ─── Debug 日志（写入本地文件，供 hdc pull 读取）────────────────────
// 注意：必须用页面的 getContext(this) context，application.getApplicationContext() 的 filesDir 路径不同
let _logCtx: Context | null = null;

export function setLogContext(ctx: Context): void {
  _logCtx = ctx;
}

function dlog(tag: string, msg: string): void {
  try {
    const ctx = _logCtx;
    if (!ctx) return;
    const path = ctx.filesDir + '/debug.log';
    const ts = new Date().toISOString().substring(11, 23);
    const line = ts + ' [' + tag + '] ' + msg + '\n';
    const f = fileIo.openSync(path, fileIo.OpenMode.CREATE | fileIo.OpenMode.APPEND);
    fileIo.writeSync(f.fd as number, line);
    fileIo.closeSync(f.fd as number);
  } catch (e) {
    // silent — avoid cascading errors
  }
}

// ─── 类型扩展（HarmonyOS AVPlayer.seekTime 扩展）─────────────────────
/**
 * AVPlayer 的内部扩展方法，seekTime 不是公开 API 签名，
 * 但 HarmonyOS NEXT 实机可用。此接口用于绕过 arkts-no-any-unknown 限制。
 */
interface AVPlayerSeekable extends media.AVPlayer {
  seekTime(timeMs: number, mode: number): Promise<void>;
}

// ─── 播放器状态 ──────────────────────────────────

export enum PlayState {
  IDLE = 'idle',
  PLAYING = 'playing',
  PAUSED = 'paused',
  STOPPED = 'stopped'
}

export interface MediaPlayerState {
  state: PlayState
  currentMedia: MediaRef | null
  currentTime: number    // 毫秒
  duration: number       // 毫秒
}

// ─── 媒体服务 ────────────────────────────────────

export class MediaService {
  private avPlayer: media.AVPlayer | null = null;
  private _state: MediaPlayerState = {
    state: PlayState.IDLE,
    currentMedia: null,
    currentTime: 0,
    duration: 0
  };
  private stateCallbacks: Array<(s: MediaPlayerState) => void> = [];
  private progressTimer: number = -1;

  /** 获取当前播放状态 */
  get state(): MediaPlayerState {
    return this._state;
  }

  /** 注册状态变化回调 */
  onStateChange(callback: (s: MediaPlayerState) => void): void {
    this.stateCallbacks.push(callback);
  }

  private emitState(): void {
    const snapshot: MediaPlayerState = {
      state: this._state.state,
      currentMedia: this._state.currentMedia,
      currentTime: this._state.currentTime,
      duration: this._state.duration
    };
    for (const cb of this.stateCallbacks) {
      cb(snapshot);
    }
  }

  /** 播放音频 */
  async playAudio(mediaRef: MediaRef): Promise<void> {
    if (mediaRef.type !== MediaType.AUDIO) return;
    await this.stop();

    try {
      this.avPlayer = await media.createAVPlayer();

      // 解决播放 URL
      let playUrl: string = '';
      try {
        const fd: number = fileIo.openSync(mediaRef.src, fileIo.OpenMode.READ_ONLY).fd as number;
        playUrl = 'fd://' + fd.toString();
      } catch (_) {
        playUrl = 'file://' + mediaRef.src;
      }

      let prepareResolve: (() => void) | null = null;
      let prepareReject: ((e: BusinessError) => void) | null = null;

      // error 监听器（在 idle 状态注册，官方要求）
      this.avPlayer.on('error', (err: BusinessError) => {
        dlog('AS', 'error: code=' + err.code + ' msg=' + err.message);
        if (prepareReject) {
          const rej = prepareReject;
          prepareResolve = null;
          prepareReject = null;
          rej(err);
        }
      });

      // stateChange 监听器（在 idle 状态注册）
      this.avPlayer.on('stateChange', (state: string) => {
        dlog('AS', 'stateChange=' + state);
        if (state === 'initialized') {
          dlog('AS', 'initialized→prepare()');
          this.avPlayer!.prepare().then(() => {
            if (prepareResolve) {
              const res = prepareResolve;
              prepareResolve = null;
              prepareReject = null;
              res();
            }
          }).catch((e: BusinessError) => {
            dlog('AS', 'prepare rejected: ' + e.code);
            if (prepareReject) {
              const rej = prepareReject;
              prepareResolve = null;
              prepareReject = null;
              rej(e);
            }
          });
        } else if (state === 'prepared') {
          // ready
        } else if (state === 'playing') {
          this._state.state = PlayState.PLAYING;
          this.emitState();
        } else if (state === 'paused') {
          this._state.state = PlayState.PAUSED;
          this.emitState();
        } else if (state === 'stopped' || state === 'completed') {
          this._state.state = PlayState.STOPPED;
          this._state.currentTime = 0;
          this.stopProgressTimer();
          this.emitState();
        } else if (state === 'error') {
          this._state.state = PlayState.IDLE;
          this.emitState();
        }
      });

      this.avPlayer.on('durationUpdate', (duration: number) => {
        this._state.duration = duration;
        this.emitState();
      });

      this._state.currentMedia = mediaRef;
      this._state.state = PlayState.PLAYING;
      this.emitState();

      // 设置 URL（触发 idle→initialized）
      dlog('AS', 'set url=' + playUrl);
      this.avPlayer.url = playUrl;

      // 等待 prepared 状态
      await new Promise<void>((resolve, reject) => {
        prepareResolve = resolve;
        prepareReject = reject;
        setTimeout(() => {
          if (prepareReject) {
            const rej = prepareReject;
            prepareResolve = null;
            prepareReject = null;
            rej({ code: -1, message: 'prepare timeout (5s)' } as BusinessError);
          }
        }, 5000);
      });

      await this.avPlayer!.play();
      this.startProgressTimer();
    } catch (e) {
      dlog('AS', 'FAIL: ' + String(e));
      this._state.state = PlayState.IDLE;
      this.emitState();
    }
  }

  /** 暂停 */
  async pause(): Promise<void> {
    if (this.avPlayer && this._state.state === PlayState.PLAYING) {
      await this.avPlayer.pause();
    }
  }

  /** 恢复播放 */
  async resume(): Promise<void> {
    if (this.avPlayer && this._state.state === PlayState.PAUSED) {
      await this.avPlayer.play();
    }
  }

  /** 停止 */
  async stop(): Promise<void> {
    this.stopProgressTimer();
    if (this.avPlayer) {
      try {
        await this.avPlayer.stop();
        await this.avPlayer.release();
      } catch (_) {}
      this.avPlayer = null;
    }
    this._state = {
      state: PlayState.IDLE,
      currentMedia: null,
      currentTime: 0,
      duration: 0
    };
    this.emitState();
  }

  /** 释放资源 */
  async release(): Promise<void> {
    await this.stop();
    this.stateCallbacks = [];
  }

  // ─── 进度 ──────────────────────────────────────

  private startProgressTimer(): void {
    this.progressTimer = setInterval(() => {
      if (this.avPlayer && this._state.state === PlayState.PLAYING) {
        try {
          this._state.currentTime = this.avPlayer.currentTime;
          this.emitState();
        } catch (_) {}
      }
    }, 500);
  }

  private stopProgressTimer(): void {
    if (this.progressTimer > 0) {
      clearInterval(this.progressTimer);
      this.progressTimer = -1;
    }
  }
}

// ─── 视频播放接口（预留） ──────────────────────────

/**
 * 视频播放器占位接口
 * 后续 video_factory 产出 MP4 后接入
 * 使用 media.createAVPlayer() 播放视频（API 已支持）
 */
export interface VideoPlayerInterface {
  /** 初始化视频播放器 */
  init(src: string): Promise<void>;
  /** 播放 */
  play(): Promise<void>;
  /** 暂停 */
  pause(): Promise<void>;
  /** 跳转到指定位置（毫秒） */
  seekTo(timeMs: number): Promise<void>;
  /** 释放 */
  release(): Promise<void>;
}

// ─── 视频播放器（v2 实现）─────────────────────────

export interface VideoRef {
  src: string
  title: string
  durationMs: number
  chain_id: string
}

export interface VideoErrorInfo {
  tier: string   // 'S1'|'S2'|'S3'|'AVPlayer'|'unknown'
  reason: string
  detail: string
}

export class VideoService {
  private avPlayer: media.AVPlayer | null = null;
  private _state: MediaPlayerState = {
    state: PlayState.IDLE,
    currentMedia: null,
    currentTime: 0,
    duration: 0
  };
  private stateCallbacks: Array<(s: MediaPlayerState) => void> = [];
  private progressTimer: number = -1;
  private _lastError: VideoErrorInfo | null = null;
  private _errorCallbacks: Array<(e: VideoErrorInfo | null) => void> = [];

  /** 最近一次播放错误 */
  get lastError(): VideoErrorInfo | null { return this._lastError; }

  /** 注册错误回调 */
  onError(callback: (e: VideoErrorInfo | null) => void): void {
    this._errorCallbacks.push(callback);
  }

  private emitError(err: VideoErrorInfo | null): void {
    for (const cb of this._errorCallbacks) { cb(err); }
  }

  /** 清除错误状态 */
  clearError(): void {
    this._lastError = null;
    this.emitError(null);
  }

  /** 获取当前播放状态 */
  get state(): MediaPlayerState {
    return this._state;
  }

  /** 注册状态变化回调 */
  onStateChange(callback: (s: MediaPlayerState) => void): void {
    this.stateCallbacks.push(callback);
  }

  private emitState(): void {
    const snapshot: MediaPlayerState = {
      state: this._state.state,
      currentMedia: this._state.currentMedia,
      currentTime: this._state.currentTime,
      duration: this._state.duration
    };
    for (const cb of this.stateCallbacks) {
      cb(snapshot);
    }
  }

  /** 播放视频（沙箱 fd:// → file:// → rawfile 兜底） */
  async playVideo(videoRef: VideoRef): Promise<void> {
    await this.stop();

    try {
      // ── Step 1: 创建实例 ───────────────────────────
      this.avPlayer = await media.createAVPlayer();
      dlog('VS', 'avPlayer created');

      const mediaRef: MediaRef = {
        type: MediaType.VIDEO,
        src: videoRef.src,
        title: videoRef.title,
        chain_id: videoRef.chain_id
      };
      this._state.currentMedia = mediaRef;

      // ── Step 2: 解决播放 URL（三层策略） ────────────
      let playUrl: string = '';
      let sourceLabel: string = '';

      try {
        const fd: number = fileIo.openSync(videoRef.src, fileIo.OpenMode.READ_ONLY).fd as number;
        playUrl = 'fd://' + fd.toString();
        sourceLabel = 'S1-fd:// fd=' + fd.toString();
        dlog('VS', 'S1 OK: ' + sourceLabel);
      } catch (_) {
        try {
          const stat = fileIo.statSync(videoRef.src);
          playUrl = 'file://' + videoRef.src;
          sourceLabel = 'S2-file:// size=' + stat.size;
          dlog('VS', 'S2 OK: ' + sourceLabel);
        } catch (_2) {
          try {
            dlog('VS', 'S3 rawfile try');
            const ctx3 = application.getApplicationContext();
            const rawData: Uint8Array = await ctx3.resourceManager.getRawFileContent('ep01_pipeline.mp4');
            dlog('VS', 'S3 rawfile read size=' + rawData.byteLength);
            const cachePath = ctx3.cacheDir + '/ep01_pipeline.mp4';
            const fdW: number = fileIo.openSync(cachePath,
              fileIo.OpenMode.CREATE | fileIo.OpenMode.WRITE_ONLY).fd as number;
            fileIo.writeSync(fdW, rawData.buffer as ArrayBuffer);
            fileIo.closeSync(fdW);
            const fdR: number = fileIo.openSync(cachePath, fileIo.OpenMode.READ_ONLY).fd as number;
            playUrl = 'fd://' + fdR.toString();
            sourceLabel = 'S3-rawfile fd=' + fdR.toString();
            dlog('VS', 'S3 OK: ' + sourceLabel);
          } catch (_3) {
            playUrl = '';
            sourceLabel = 'ALL FAILED';
            const err3 = _3 as BusinessError;
            dlog('VS', 'S3 FAILED: ' + err3.code + ' ' + err3.message);
            this._lastError = { tier: 'S3', reason: 'rawfile→cache 失败', detail: err3.code + ' ' + err3.message };
            this.emitError(this._lastError);
          }
        }
      }

      if (!playUrl) {
        dlog('VS', 'FAIL: no playUrl, source=' + sourceLabel);
        this._state.state = PlayState.IDLE;
        this._state.currentMedia = null;
        const err: VideoErrorInfo = { tier: 'S3', reason: '三层策略全部失败', detail: sourceLabel + ' | src=' + videoRef.src };
        this._lastError = err;
        this.emitError(err);
        this.emitState();
        return;
      }

      // ── Step 3: 在 idle 状态下注册所有监听器（官方要求）───
      let prepareResolve: (() => void) | null = null;
      let prepareReject: ((e: BusinessError) => void) | null = null;
      let isError = false;
      let errorCode = 0;
      let errorMsg = '';

      // error 监听器（官方要求：在 idle 状态、未设 URL 前注册）
      this.avPlayer.on('error', (err: BusinessError) => {
        isError = true;
        errorCode = err.code;
        errorMsg = err.message;
        dlog('VS', 'error event: code=' + err.code + ' msg=' + err.message);
        // 拒绝 prepare promise
        if (prepareReject) {
          const rej = prepareReject;
          prepareReject = null;
          prepareResolve = null;
          rej(err);
        }
      });

      // stateChange 监听器
      this.avPlayer.on('stateChange', (state: string) => {
        dlog('VS', 'stateChange=' + state);
        if (state === 'initialized') {
          // idle → initialized：调用 prepare()，然后等待 prepared 状态
          dlog('VS', 'initialized: calling prepare()');
          this.avPlayer!.prepare().then(() => {
            dlog('VS', 'prepare() resolved, triggering resolve');
            if (prepareResolve) {
              const res = prepareResolve;
              prepareResolve = null;
              prepareReject = null;
              res();
            }
          }).catch((e: BusinessError) => {
            dlog('VS', 'prepare() rejected: ' + e.code + ' ' + e.message);
            if (prepareReject) {
              const rej = prepareReject;
              prepareResolve = null;
              prepareReject = null;
              rej(e);
            }
          });
        } else if (state === 'prepared') {
          // 已进入 prepared，可以播放了（但 play 会在下面主动调用）
        } else if (state === 'playing') {
          this._state.state = PlayState.PLAYING;
          this.emitState();
        } else if (state === 'paused') {
          this._state.state = PlayState.PAUSED;
          this.emitState();
        } else if (state === 'stopped' || state === 'completed') {
          this._state.state = PlayState.STOPPED;
          this._state.currentTime = 0;
          this.stopProgressTimer();
          this.emitState();
        } else if (state === 'error') {
          isError = true;
          dlog('VS', 'state=error: ' + playUrl);
          this._state.state = PlayState.IDLE;
          if (prepareReject) {
            const rej = prepareReject;
            prepareResolve = null;
            prepareReject = null;
            rej({ code: errorCode || -1, message: errorMsg || 'unknown' } as BusinessError);
          }
          this.emitState();
        }
      });

      // durationUpdate 监听器
      this.avPlayer.on('durationUpdate', (duration: number) => {
        this._state.duration = duration;
        this.emitState();
      });

      // ── Step 4: 设置 URL（触发 idle→initialized）───
      dlog('VS', 'set url=' + playUrl + ' label=' + sourceLabel);
      this.avPlayer.url = playUrl;

      // ── Step 5: 等待 prepared 状态，然后 play ─────────────────────
      this._state.state = PlayState.PLAYING;
      this._state.duration = videoRef.durationMs;
      this.emitState();

      await new Promise<void>((resolve, reject) => {
        prepareResolve = resolve;
        prepareReject = reject;
        // 8 秒超时兜底
        setTimeout(() => {
          if (prepareReject) {
            const rej = prepareReject;
            prepareResolve = null;
            prepareReject = null;
            isError = true;
            rej({ code: -1, message: 'prepare timeout (8s)' } as BusinessError);
          }
        }, 8000);
      });

      if (isError) {
        const err: VideoErrorInfo = { tier: 'AVPlayer', reason: 'AVPlayer 异常', detail: errorCode + ' ' + errorMsg };
        this._lastError = err;
        this._state.state = PlayState.IDLE;
        this.emitError(err);
        this.emitState();
        return;
      }

      dlog('VS', 'calling avPlayer.play()');
      await this.avPlayer!.play();
      dlog('VS', 'avPlayer.play() returned OK');
      this.startProgressTimer();
    } catch (e) {
      const be = e as BusinessError;
      dlog('VS', 'FAIL catch: ' + be.code + ' ' + be.message + ' src=' + videoRef.src);
      this._state.state = PlayState.IDLE;
      const err: VideoErrorInfo = { tier: 'AVPlayer', reason: 'AVPlayer 异常', detail: be.code + ' ' + be.message };
      this._lastError = err;
      this.emitError(err);
      this.emitState();
      return;
    }
  }

  /** 暂停视频 */
  async pause(): Promise<void> {
    if (this.avPlayer && this._state.state === PlayState.PLAYING) {
      await this.avPlayer.pause();
    }
  }

  /** 恢复播放 */
  async resume(): Promise<void> {
    if (this.avPlayer && this._state.state === PlayState.PAUSED) {
      await this.avPlayer.play();
    }
  }

  /** 停止并释放 */
  async stop(): Promise<void> {
    this.stopProgressTimer();
    if (this.avPlayer) {
      try {
        await this.avPlayer.stop();
        await this.avPlayer.release();
      } catch (_) {}
      this.avPlayer = null;
    }
    this._state = {
      state: PlayState.IDLE,
      currentMedia: null,
      currentTime: 0,
      duration: 0
    };
    this.emitState();
  }

  /** 跳转到指定时间（毫秒） */
  async seekTo(timeMs: number): Promise<void> {
    if (this.avPlayer) {
      try {
        await (this.avPlayer as AVPlayerSeekable).seekTime(timeMs / 1000, 0);
        this._state.currentTime = timeMs;
        this.emitState();
      } catch (_) {}
    }
  }

  /** 释放资源 */
  async release(): Promise<void> {
    await this.stop();
    this.stateCallbacks = [];
  }

  // ─── 进度 ──────────────────────────────────────

  private startProgressTimer(): void {
    this.progressTimer = setInterval(() => {
      if (this.avPlayer && this._state.state === PlayState.PLAYING) {
        try {
          this._state.currentTime = this.avPlayer.currentTime;
          this.emitState();
        } catch (_) {}
      }
    }, 500);
  }

  private stopProgressTimer(): void {
    if (this.progressTimer > 0) {
      clearInterval(this.progressTimer);
      this.progressTimer = -1;
    }
  }
}

// 单例
export const mediaService = new MediaService();
export const videoService = new VideoService();
