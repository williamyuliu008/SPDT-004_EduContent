# 3_render — 渲染生产层

## 定位

知识加工流水线的**多形态渲染引擎**。将 scene_v2 剧本转化为音频/视频/知识卡片等多形态交付物，是 CGM（内容生成方法论）的核心执行层。

## 核心职责

| 职责 | 说明 |
|:---|:---|
| **多形态渲染** | scene_v2 → audio MP3 / video MP4 / 知识卡片 |
| **CGM方法论执行** | Compositional Scene + Guidance Orchestration + Multi-channel Output |
| **视觉素材整合** | 调用 PT-039_CalligraphyVision 书法视觉素材 |
| **质量门禁** | 渲染产出的5项质量审计 |

## 目录结构

```
3_render/
├── SPDT-KTE/              ← 管线编排核心（interface_protocols/ + orchestrator/）
│   ├── interface_protocols/   # IF-A~IF-F 协议定义
│   ├── runners/                # daily/weekly/smoke/eventbus
│   └── integration/           # 跨PT注入桥
├── video_factory/          ← PT-VFX 视觉渲染引擎
│   ├── renderers/              # video/image/audio renderer
│   ├── models/                # voice/synthesis models
│   └── outputs/               # MP4/PNG/MP3
└── _output/                 ← 渲染输出（不进入Git）
```

## CGM 渲染管线

```
scene_v2 JSON
    │
    ├── [IF-A] scene_v2 JSON ──→ 文本分析器 ──→ 关键帧脚本
    │
    ├─→ 音频渲染 ──→ MP3（旁白+音效）
    ├─→ 视觉渲染 ──→ 书法素材 + AI图像 → 视频帧
    └─→ 卡片渲染 ──→ PNG知识卡（知识点/辨析卡）
```

## 渲染质量门禁

| 检查项 | 标准 |
|:---|:---|
| 音频完整性 | 无截断、无爆音、时长与scene匹配 |
| 视觉一致性 | 书法字形/人物朝代无穿帮 |
| 内容准确性 | 知识卡内容与scene_v2一致 |
| 格式合规性 | MP3≤128kbps / MP4≤1080P / PNG≤2MB |
| 版权清洁 | 书法碑帖/图像素材有合法授权 |

## 接口协议

| 协议 | 起点 | 终点 | 内容 |
|:---|:---|:---|:---|
| IF-A | 2_structure | 3_render | scene_v2 JSON |
| IF-B | 3_render | 4_adapt | video_package |
| IF-C | 3_render | 5_deliver | card_package |
| IF-E | 4_adapt | 3_render | 薄弱点反馈（重渲染指令） |

## 输出

- `audio/*.mp3` → D:/4_data/education/TextExperience/_output/
- `video/*.mp4` → D:/4_data/education/TextExperience/_output/
- `cards/*.png` → D:/4_data/education/TextExperience/_output/

## 当前状态

**运行中** — SPDT-KTE（maturity 0.7）+ video_factory（maturity 0.7）
