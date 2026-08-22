# 3_render 渲染层 (L1 · Evolutionary)

> **层级**：L1 (Evolutionary) — 通过 L0 接口消费能力
> **窗口**：W_mid (每天/每周)
> **关联**：[LAYERS.md](../LAYERS.md) §3.2 / [ISOLATION.md](ISOLATION.md)

## 1. 定位

5 阶段流水线的 **第 3 阶段**（1_ingest → 2_structure → **3_render** → 4_adapt → 5_deliver），将结构化剧本（scene_v2 JSON / ep 脚本）转化为多模态产物（视频 / 音频 / 视觉素材），服务 4 大真产品中的 P-001 视频和 P-004 音频。

## 2. 现有子模块

| 子模块 | 状态 | 阶段 | 说明 |
|:---|:---:|:---|:---|
| `P-001_video/` | ✅ v0.1.1 | W27-W28 | 视频渲染管线（manim + edge-tts + ffmpeg）|
| (历史) `SPDT-KTE/` | 🗑️ | 已迁 | 跨项目数据，已迁到 D:\4_data\work\media\renders\ |
| (历史) `video_factory/` | 🗑️ | 已迁 | 跨项目数据，已迁到 D:\4_data\work\media\renders\ |

## 3. P-001 视频渲染管线（W28 落地）

### 3.1 链路
```
scene_v2 (ep 脚本)
    ↓ importlib.util
SCRIPT 字典 (events[5] + title + subtitle)
    ↓ manim -ql
无声视频 mp4 (480p, h264)
    ↓ edge-tts (rate=-18%)
配音 mp3 (zh-CN-YunjianNeural)
    ↓ ffmpeg -c:a aac
成品 mp4 (h264 + aac, ~3 分钟)
```

### 3.2 关键脚本
- `P-001_video/test_scenes.py` — 3 个 manim 基础示例
- `P-001_video/build_p001_v0_1.py` — 5 段叙事场景（manim Scene 类）
- `P-001_video/build_p001_full.py` — TTS 生成 + ffmpeg 合成（一键出片）
- `P-001_video/batch_render.py` — 批量渲染（10 支历史素材，W28 100% PASS）
- `P-001_video/batch_audit_p001.py` — P-001 准确性批量审计（W29 9 GOLD + 1 SILVER）

### 3.3 渲染产物
- `P-001_video/media/videos/<build>/480p15/<Scene>.mp4` — 中间产物
- `P-001_video/media/audio/<ep>_narration.mp3` — 配音
- `P-001_video/media/final/<P001_Ep...>.mp4` — 成品
- `P-001_video/media/batch/w28/` — W28 批量报告 + 10 支 mp4

## 4. 升级路径

按 [LAYERS.md §5](../LAYERS.md#5-升级路径l2--l1--l0)：

- **L1 → L0 准入**（v3.0 末评估）：
  - [ ] 持续稳定 ≥ 3 个月
  - [ ] 完整单元测试 + 集成测试
  - [ ] CHANGELOG 记录所有变更
  - [ ] 至少 1 个真实业务案例（v3.0 4 真产品联合验收）
  - [ ] willi 拍板

## 5. 已知限制

- **画面单调**：仅字幕 + 几何装饰线，无真实图像/地图（演示级，v3.0 可接受）
- **字幕时间轴硬编码**：`wait(self._estimate_speech_time(...))` 估算配音时长，与实际 TTS 偏差
- **M-003 视觉素材未集成**：PT-039_CalligraphyVision 的书法图未接入 P-001 视频
- **P-004 音频产品未独立化**：当前 edge-tts 仅服务 P-001 视频，独立的 P-004 音频管线待 v3.0+
