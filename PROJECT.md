# SPDT-004 项目总览 (PROJECT.md)

> **版本**: v1.0 (本轮)
> **范围**: 4 类型项目 + 5 阶段流水线 + 双窗口协作
> **更新**: 每次重要路线切换时更新

---

## 1. 项目愿景

为**上海文科艺术生**（高考 6 主科 + 国美校招）构建**自适应多媒体学习系统**：从知识卡片到策略库到 CGM 视频音频到 rujing APP 全链路。

**学生画像**: 上海高考 + 国美校招，排除理化生 3 科。

---

## 2. 4 类型活跃项目

| 类型 | 描述 | 负责人 | 频率 | 状态 |
|:---|:---|:---|:---|:---|
| **A. 教育核心 (P0)** | 知识图谱 + 策略卡 + 母题 + 元学习 | 宇兄端 | 高频 | ✅ P0-A/B/C/D 全线收官 (16 commits) |
| **B. CGM 多媒体 (P-CGM)** | 历史 15 张 + 5 学科 40 张 30s 视频 + TTS 音频 | 宇兄端 | 中频 | ✅ P-CGM.1~3.5 7 commits, 55 张 mp4 + 55 mp3 |
| **C. PT-030 真题挖掘** | 5 学科真题 PDF/docx → 母题库 | **雪薇端** (宇兄提供工具) | 低频 | ⏸ 工具就绪 (5 解析器 + 双 LLM), 雪薇端入库 |
| **D. 终端交付** | rujing Web demo + HarmonyOS APP | 宇兄 + 手机端 | 极低 | ⏸ Flask demo 跑通 (127.0.0.1:5050), HarmonyOS 第三方开发 |

---

## 3. 5 阶段流水线

```
1_ingest ────► 2_structure ────► 3_render ────► 4_adapt ────► 5_deliver
  原始素材       脚本化剧本       多媒体渲染       自适应平台       终端交付
 (PT-030)      (TextExperience) (manim + TTS)   (5Agent调度)   (rujing APP)
```

| 阶段 | 目录 | 角色 | 产出 |
|:---|:---|:---|:---|
| 1_ingest | `1_ingest/` | 原始素材采集 | PDF/题库/语料 |
| 2_structure | `2_structure/TextExperience/` (submodule) | 脚本化剧本 | ep_NN.py / 母题 JSON |
| 3_render | `3_render/` | 多媒体生成 | mp4 + mp3 (D:\4_data\work\media) |
| 4_adapt | `4_adapt/AdaptivePrepPlatform/` | 自适应学习 | 用户路径 / KG 节点 |
| 5_deliver | `5_deliver/TextExperienceAPP/` | 终端 APP | HarmonyOS rujing |

---

## 4. 双窗口协作

| 窗口 | 角色 | 工作范围 | 协作方式 |
|:---|:---|:---|:---|
| **宇兄端** (本机) | 开发助手 (mavis) | 工具链 + 算法 + rujing demo | 直接 git push |
| **雪薇端** (另一台机器 AI) | 学生 (知识/真题) | 知识卡片 + PT-030 真题 | `handoff/` 文档 + git PR |
| **手机端** (鸿蒙) | 真实学生 | APP 集成 | 第三方开发 |

**协作契约**:
- `handoff/` 是双窗口唯一接口
- `tools/` 是宇兄提供、雪薇可调用的脚本
- `D:\4_data\knowledge_cards\` 是知识卡 (git 外)
- `D:\4_data\work\media\` 是 CGM 多媒体产物 (git 外)

---

## 5. git 边界

| 位置 | git 状态 | 说明 |
|:---|:---|:---|
| `tools/`, `products/`, `handoff/`, `docs/`, `knowledge_graphs/` | ✅ git tracked | 工具/演示/双窗口文档/设计/KG JSON |
| `1_ingest/`, `2_structure/` (内容), `3_render/` (内容), `5_deliver/` | ❌ git 外 (内容/管线分离) | 内容产物在 D:\4_data\ 或各自模块 git |
| `D:\4_data\knowledge_cards\元学习/` | ❌ git 外 | 雪薇端 20 张卡 |
| `D:\4_data\work\media/renders/` | ❌ git 外 | CGM 视频/音频产物 |

---

## 6. 阶段路线 + 关键里程碑

| 阶段 | commit | 状态 |
|:---|:---|:---|
| P0-A 策略卡 + 元学习 + 5 学科母题 + crosslink v1.2 (100%) | 1c54ff2 | ✅ |
| P0-B 知识图谱 (math + multi_subject) + path_finder + rujing /kg | f31f26d + 439aa28 + 187e6fc | ✅ |
| P0-C 元学习 8→20 张 + chain_id 修复 | acf93e8 + 4267626 | ✅ |
| P0-D /learn 集成 4 区块 (策略 + 概念 + 元学习 + 视频) | 41241bf | ✅ |
| P1 rujing 雪薇端验收清单 + PT-030 数据规范 | f1fd5f4 | ✅ |
| P-CGM.1 历史 5 张 K 卡 → 30s 视频 | 193d36f | ✅ |
| P-CGM.2 历史 K 卡扩 10 集 | 2b56a9e | ✅ |
| P-CGM.3 5 学科母题 40 张 → 30s 视频 | 850a731 | ✅ |
| P-CGM.4 TTS 音频独立嵌入 | 6a3c766 | ✅ |
| P-CGM.5 kg_view 视频库 tab | d921ced | ✅ |
| P-CGM.3.5 通用视频/音频路由 + 30 概念挂载 | b9e674d | ✅ |
| **未来**: 数学 31 张母题视频 / PT-030 真题入库 / rujing APP 集成 | ⏳ | 待启动 |

---

## 7. 相关文档

- `OWNERS.md` — 各目录所有权矩阵
- `STATUS.md` — 当前活跃子任务快照
- `AGENTS.md` — 数据迁移路径
- `PT-030/` — 真题挖掘 (雪薇端主导)
- `4_adapt/AdaptivePrepPlatform/` — 5 Agent 调度 + CGM 融合方法论
- `handoff/` — 双窗口协作历史文档