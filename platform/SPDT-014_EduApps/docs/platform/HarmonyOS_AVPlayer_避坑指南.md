# HarmonyOS AVPlayer 视频播放 · 避坑指南

> 来源：官方文档 + 实机调试 2026-07-18
> 适用于：HarmonyOS NEXT / API 24+
> 更新：2026-07-18（XComponent SDK 限制说明）

---

## 状态机（官方流程）

```
idle ──url──> initialized ──prepare()──> prepared ──play()──> playing
                  ↑                          │
                  └──reset()─────────────────┘
```

**官方原文**：
> "需要播放器在 **idle 状态下、未调用设置资源接口前**完成设置监听"
> "调用 `prepare()` 使 AVPlayer 进入 **prepared 状态**，此时可获取 duration，并执行 `play()`"

---

## 必须遵守的 3 条铁律

### ① 监听器必须在设 URL 前注册（idle 状态）

```typescript
// ✅ 正确顺序
avPlayer = await media.createAVPlayer();
avPlayer.on('error', (err) => { ... });   // 先注册
avPlayer.on('stateChange', (state) => {   // 先注册
  if (state === 'initialized') {
    avPlayer.prepare();                     // 自动调用
  } else if (state === 'playing') { ... }
});
avPlayer.url = 'fd://123';                // 后设 URL

// ❌ 错误顺序（会导致 error 事件丢失、状态机错乱）
avPlayer.url = '...';                      // 先设 URL
avPlayer.on('error', ...);                 // 后注册监听
avPlayer.play();                           // 直接 play
```

### ② `play()` 前必须 `prepare()`（视频必做，音频建议也做）

视频：`prepared` 状态前调用 `play()` → 报错 `5400102`（状态不允许操作）→ `error` 状态 → "avplayer异常"

音频：HarmonyOS 对音频较宽容，`play()` 在 `initialized` 时会自动 prepare（但建议也显式做）

```typescript
// ✅ 标准流程（官方 Codelab 写法）
avPlayer.on('stateChange', (state) => {
  if (state === 'initialized') {
    avPlayer.surfaceId = surfaceId;  // 视频必须设置（来自 XComponent）
    avPlayer.prepare();                // 显式 prepare
  } else if (state === 'playing') {
    // 播放中
  }
});
avPlayer.url = '...';
```

### ③ 视频必须有 `surfaceId`（XComponent）

视频播放画面需要渲染 surface。`prepare()` 时若未设置 `surfaceId`，会静默失败或报错。

```typescript
// 获取 surfaceId（从 XComponent 组件）
XComponent({
  id: 'xComponentId',
  type: XComponentType.SURFACE,
  controller: this.xComponentController
})
.onLoad(() => {
  this.surfaceId = this.xComponentController.getXComponentSurfaceId();
})
```

**音频不需要 surfaceId**："设置显示画面，当播放的资源为纯音频时无需设置"

---

## ⚠️ XComponent SDK 限制（OpenHarmony SDK 6.1）

**问题**：`XComponent` 和 `XComponentController` 在 OpenHarmony SDK 6.1 的类型定义中不存在：
- SDK 路径：`D:\9_infra\DevEco\6.1\sdk\default\openharmony\ets\api\arkui\`
- 实际存在：`ComponentContent.d.ts`、`BuilderNode.d.ts`、`FrameNode.d.ts`
- 不存在：`XComponent.d.ts`、`XComponentController.d.ts`

**设备情况**：设备运行 HarmonyOS 6.1.0（API 24），运行时支持 XComponent，但编译时 SDK 缺少类型定义。

**当前状态**：VideoService 去掉了 XComponent 依赖，视频在 HarmonyOS 实机上可能仍然需要 surfaceId。

**若视频仍报错 "avplayer异常"**：需要解决 surfaceId 问题，方案：
1. **方案 A（推荐）**：在工程中添加本地类型声明文件 `entry/src/main/ets/types/xcomponent.d.ts`：
   ```typescript
   // 本地声明 XComponent（HarmonyOS 实机支持，但 OpenHarmony SDK 缺类型）
   declare class XComponent {
     constructor(options: object);
     onLoad(callback: () => void): XComponent;
   }
   declare class XComponentController {
     getXComponentSurfaceId(): string;
   }
   ```
2. **方案 B**：改用 `Video` 系统组件（ArkUI 内置），自动处理 surfaceId

---

## 常见错误码

| 错误码 | 含义 | 常见原因 |
|:---|:---|:---|
| `5400102` | Operate Not Permit（状态不允许） | 在 `idle`/`initialized` 状态调用 `play()`，未先 `prepare()` |
| `5400103` | 媒体与其他模块交互问题 | 网络/服务器限流 |
| `5400104` | 网络超时 | 访问超时，默认 15s |
| 第三方错误码 | fd 失效 | `fd://` 中的 fd 已关闭（`fileIo.closeSync` 提前关闭了 fd） |

---

## `fd://` 的正确姿势

fd（文件描述符）是有时效的，必须保证在播放期间 fd 保持打开：

```typescript
// ✅ 正确：fd 打开后全程保持，打开者在播放结束前不关闭
const f = fileIo.openSync(path, fileIo.OpenMode.READ_ONLY);
playUrl = 'fd://' + f.fd;
// ... 播放 ...
// 在 release() 时才关闭 fd
fileIo.closeSync(f.fd);

// ❌ 错误：提前 closeSync 导致 fd 失效
const f = fileIo.openSync(path, fileIo.OpenMode.READ_ONLY);
playUrl = 'fd://' + f.fd;
fileIo.closeSync(f.fd);  // 关闭后 fd 就失效了
avPlayer.url = playUrl;  // 播放失败
```

**推荐用 Promise 封装 prepare 流程**（而非直接 await），让状态机自动驱动：

```typescript
await new Promise<void>((resolve, reject) => {
  this.avPlayer!.on('stateChange', (state) => {
    if (state === 'initialized') {
      this.avPlayer!.prepare().then(resolve).catch(reject);
    }
  });
  this.avPlayer!.url = url;
});
await this.avPlayer!.play();
```

---

## 无 XComponent 时的备选方案

如果当前页面不需要视频画面（仅播放音频轨道，或调用系统播放器）：

```typescript
// 方案 A：用 wantAgent 拉起系统视频播放器
import { wantAgent } from '@kit.AbilityKit';
const wantAgentInfo = await wantAgent.getWantAgent({
  wants: [{
    uri: 'file://' + videoPath,
    action: 'android.intent.action.VIEW',
    type: 'video/mp4'
  }]
});
await wantAgent.startWantAgent(wantAgentInfo);

// 方案 B：先做音频（不需要 surfaceId），视频画面后续加 XComponent
```

---

## 沙箱文件路径参考

```
应用沙箱根目录：/data/storage/el2/base/files/
filesDir：        /data/storage/el2/base/files/
cacheDir：        /data/storage/el2/base/cache/
注意：application.getApplicationContext().filesDir ≠ 页面 getContext(this).filesDir
```

---

## 调试技巧

1. **看日志判断哪层失败**：`[VS]` = VideoService，`[AS]` = AudioService，`[PLAY]` = UI 层点击
2. **拉取 debug.log**：`hdc file recv /data/storage/el2/base/files/com.harmonystudio.rujing/debug.log .`
3. **实时 hilog**：`hdc shell "hilog -a | grep -i avplayer"` 或 `Select-String` 过滤
4. **用 DevEco Testing Hypium** 做 UI 自动化回归（`automation/` 目录）
