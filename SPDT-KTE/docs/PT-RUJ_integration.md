# PT-RUJ 入境 App · SPDT-KTE 接入规范

> **版本**：v1.0 | **PT**：PT-RUJ | **对接管线**：SPDT-KTE

---

## 一、PT-RUJ 在管线中的角色

PT-RUJ 是 SPDT-KTE 的**移动交付终端**——接收 PT-038 的 Flashcard 包（IF-C）和 PT-VFX 的视频包（IF-B），在鸿蒙手机上提供链阅读、Flashcard 复习和视频播放服务。

---

## 二、管线输入规范

### 2.1 IF-C：Card Package JSON（来自 PT-038）

**来源**：`PT-038/ebooks/{series}_cards.json`

**PT-RUJ ImportService 职责**：
- 解析 v3.0.0 schema（含 node_cards / strategy_cards / chain_cards 三型）
- 兼容 v1/v2 扁平格式（`cards[]` 数组）
- 写入本地 RDB（DatabaseService）
- 叙事文本写入 `/data/storage/el2/base/files/rujing/narratives/`

**音频映射（audio_meta.json）**：
- 当前硬编码在 `resources/base/rawfile/audio_meta.json`
- **建议升级**：迁移到 DB 存储，ImportService 导入时写入，实现热更新

### 2.2 IF-B：Video Package Metadata（来自 PT-VFX）

**来源**：PT-VFX series_builder.py 输出的 `metadata.json`

**PT-RUJ ImportService 职责**（待实现）：
```typescript
// ImportService.ets 新增函数
async importVideoPackage(
  metadataJson: string,
  mp4FilePaths: string[]
): Promise<number>
```
- 解析 v1.0.0 schema
- 复制 MP4 到沙箱目录：`/data/storage/el2/base/files/rujing_videos/`
- 解析 `scene_timeline`，存入 DB（用于"跳转至 scene"功能）
- 返回导入的 episode 数量

### 2.3 PT-RUJ → PT-038 音频映射升级

当前 `audio_meta.json` 结构：
```json
[
  { "ep": 1, "ep_title": "...", "audio_file": "ep01.wav", "chains": ["墨骨山河_ep01"] }
]
```

**建议升级为 DB 表**：
```typescript
// DatabaseService.ets 新增表
interface VideoPackageRecord {
  ep_id: number
  ep_title: string
  video_path: string
  audio_path: string
  duration: number
  chains: string[]
  timeline: string   // JSON stringified scene_timeline
}
```

---

## 三、MediaService 视频播放规范

### 3.1 VideoPlayerInterface 实现（当前为空桩）

**目标**：实现 `MediaService.ets` 中的 `VideoPlayerInterface`：

```typescript
// MediaService.ets
export async function playVideo(mediaRef: MediaRef): Promise<void> {
  // 使用 media.createAVPlayer() 播放本地 MP4
  // 复用现有音频状态机（PlayState）
  // 支持 seekTo(scene_idx) 基于 scene_timeline
}
```

### 3.2 跳转至特定 Scene

基于 PT-VFX 传入的 `scene_timeline`，PT-RUJ 实现：

```typescript
async seekToScene(sceneIdx: number): Promise<void> {
  const timeline = getSceneTimeline(); // from DB
  const entry = timeline.find(t => t.idx === sceneIdx);
  if (entry) {
    await this.avPlayer.seek(entry.time * 1000); // 毫秒
  }
}
```

---

## 四、ChainReaderPage 视频集成规范

### 4.1 视频入口 UI

ChainReaderPage 在音频播放按钮旁增加"视频播放"入口：

```
┌─────────────────────────────────────┐
│  乾元元年·蒲州的墨与血               │
│  ━━━━━━━━━━○────────── 02:36/03:36  │
│  [🔊 播放音频]  [🎬 播放视频]       │
└─────────────────────────────────────┘
```

### 4.2 视频内互动

基于 `scene_timeline` 中的 `five_skandha` 快照：
- 视频播放至特定 scene 时，底部弹出该 scene 的 `action_prompt`（行蕴触发提示）
- 用户点击"我记住了" → 标记该 scene 对应的卡片为"生/熟"
- 实现 **视频观看 → 行蕴激活** 的无缝衔接

---

## 五、IF-D 学习行为反馈（Phase C）

Phase C 阶段，PT-RUJ 将记录学习行为日志，回传给 PT-038：

```typescript
interface LearningFeedback {
  card_id: string
  recognition_time: number      // Unix timestamp
  review_count: number           // 复习次数
  avg_interval_days: number      // 平均复习间隔
  recognition_stable: boolean     // 连续3次正确
  bottleneck_node: string | null  // 高频错知识点
}
```

PT-RUJ DatabaseService 在每次 Flashcard 复习后追加此记录，PT-038 在生成新内容前读取并分析。

---

## 六、跨 PT 协调规范

- PT-RUJ 是 IF-B（video_package_metadata）和 IF-C（card_package）的 **consumer**
- PT-RUJ 是 IF-D（learning_feedback）的 **producer**
- 接口协议（IF-B/C/D）变更需 PT-RUJ 评估 HarmonyOS 适配成本
- PT-RUJ 无权单方面变更已有接口，必须通过 SPDT-KTE DRC 流程
