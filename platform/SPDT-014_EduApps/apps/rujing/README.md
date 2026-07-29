# 入境 (RùJìng)

> 沉浸式学习 · 高考文科知识卡片APP | SPDT-001_Harmony · SPDT-004_EduContent 配套

## 定位

"入境"——进入历史场景、进入专注状态、进入学与习的认知循环。

50条知识链构成场景沉浸，音视频+文字卡片构成感官沉浸，学然后习构成认知过程的沉浸。

## 核心特性

- **📖 剧本式学习**：先读链的叙事文本（理解），再抽查节点卡（记忆）
- **🤖 AI 内置**：问答/制卡/答案转卡片，自动注入当前上下文
- **🎵 媒体集成**：首版支持音频播放，预留视频接口
- **⚡ 极简管理**：仅生/熟二态标记，无复杂元数据

## 技术栈

- 平台：HarmonyOS NEXT (API 14+)
- UI：ArkUI + ArkTS
- 存储：RDB + 文件系统
- AI：多后端抽象层（默认智谱GLM）

## 项目结构

```
rujing/entry/src/main/ets/
├── entryability/EntryAbility.ts    # 入口，初始化数据库
├── pages/
│   ├── Index.ets                  # 仪表盘
│   ├── ChainListPage.ets          # 学科→链列表
│   ├── ChainReaderPage.ets        # 链阅读器（核心）
│   ├── AIPanelPage.ets            # AI 对话面板
│   └── ImportPage.ets             # 数据导入
├── model/DataModel.ets            # 类型定义
├── service/
│   ├── DatabaseService.ets        # RDB 数据库
│   ├── ImportService.ets          # PT-038 导入
│   ├── AIService.ets              # AI 多后端
│   └── MediaService.ets           # 音频/视频
└── prompt/                        # Prompt 模板（P2）
```

## 数据来源

内容由 SPDT-004_EduContent / PT-038_TextExperience 管线生产：
- 卡片包 JSON（node_cards + strategy_cards + chain_cards）
- 链元数据 JSON（叙事文本 + 关联关系）
- 配套音频 MP3（BGM 混音）
- 配套视频（video_factory 后续接入）

## 品牌

- **名称**：入境
- **bundleName**：com.harmonystudio.rujing
- **色彩**：待定
