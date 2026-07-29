# 5_deliver — 触达交付层

## 定位

知识加工流水线的**多端触达终端**。将 `4_adapt/` 编排好的内容分发至 PC（知识图谱可视化）和手机端（知识卡片/音频/视频），实现"在哪里都能学"。

## 核心职责

| 职责 | 说明 |
|:---|:---|
| **PC端交付** | 知识图谱可视化 + 离线内容包管理 |
| **手机端交付** | HarmonyOS APP（rujing/gaokao-*） |
| **离线缓存** | D:/4_data/education/TextExperienceAPP/_cache/ |
| **内容包加载** | 解析 IF-C1/C2（card_package / audio_package） |

## 目录结构

```
5_deliver/
├── TextExperienceAPP/         ← HarmonyOS APP 开发平台
│   ├── apps/
│   │   ├── rujing/            ← 入境APP（书法/历史备考）
│   │   └── gaokao-*/          ← 高考系列APP
│   ├── src/                   ← 共用业务逻辑
│   └── build/                 ← HAP构建输出
└── _cache/                    ← 离线内容包缓存（不进入Git）
```

## 交付形态

| 终端 | 形态 | 内容来源 |
|:---|:---|:---|
| PC浏览器 | 知识图谱可视化 | 4_adapt/knowledge_graph/ |
| 手机APP | 知识点音频 | IF-C2 audio_package |
| 手机APP | 知识卡片 | IF-C1 card_package |
| 手机APP | 短视频 | IF-B video_package |

## 接口协议

| 协议 | 起点 | 终点 | 内容 |
|:---|:---|:---|:---|
| IF-C1 | 4_adapt | 5_deliver | card_package（知识点+薄弱点标注） |
| IF-C2 | 4_adapt | 5_deliver | audio_package（音频+学习指引） |
| IF-F | 4_adapt | 5_deliver | learning_path（下一步推荐） |

## 技术栈

- **手机端**：HarmonyOS（Stage模型）+ ArkTS
- **PC端**：Web（知识图谱可视化）
- **构建链**：
  - `DEVECO_SDK_HOME` / `OHOS_BASE_SDK_HOME`
  - `D:/2_products/education/SPDT-004_EduContent/platform/PT-037_AdaptivePrepPlatform/irc/`（IRC共享）

## 当前状态

**运行中** — TextExperienceAPP，Maturity: 0.6，13个APP
