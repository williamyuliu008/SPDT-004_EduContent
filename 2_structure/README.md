# 2_structure — 结构化加工层

## 定位

知识加工流水线的**核心生产引擎**。将摄入的原料转化为结构化的场景剧本（scene_v2 JSON），构建知识图谱，生成多形态内容的"母版"。

## 核心职责

| 职责 | 说明 |
|:---|:---|
| **知识结构化** | 从原料提取实体、关系、时序，构建知识图谱 |
| **场景剧本生成** | 将知识点转化为叙事单元（scene_v2 JSON） |
| **墨骨山河系列** | 书法史+历史双学科融合沉浸式微剧本 |
| **古史知识链** | 高考历史通史+专题知识链 |
| **跨学科缝合** | 书法史 × 历史 × 文学 × 地理的多维连接 |

## 关键产出

### scene_v2 Schema

```json
{
  "id": "ep01_scene_03",
  "type": "narrative|analysis|drill",
  "title": "乾元元年·蒲州的墨与血",
  "knowledge_nodes": ["颜真卿", "安史之乱", "唐隶", "平判事"],
  "timeline": { "year": 758, "month": 3, "location": "蒲州" },
  "roles": [...],
  "segments": [...],
  "cgm_metadata": { "output_formats": ["audio", "card", "ebook"] }
}
```

### 墨骨山河系列（书法备考）

| 剧集 | 历史人物 | 核心知识点 | 状态 |
|:---|:---|:---|:---|
| Ep01 | 颜真卿 | 安史之乱+楷书+行书 | ✅ 完成 |
| Ep02 | 王羲之 | 兰亭序+东晋门阀 | 🔨 规划中 |
| Ep03 | 苏轼 | 宋代文人+尚意书风 | 🔨 规划中 |
| Ep04 | 阮元 | 碑学兴起+清代书法 | 🔨 规划中 |
| Ep05 | 张旭/怀素 | 狂草+唐代草书 | 🔨 规划中 |
| Ep06 | 李斯 | 小篆+秦代书同文 | 🔨 规划中 |
| Ep07 | 康有为 | 碑学理论+近代书法 | 🔨 规划中 |
| Ep08 | 许慎 | 说文解字+六书 | 🔨 规划中 |

### 古史知识链系列（历史备考）

| 卷次 | 内容 | 状态 |
|:---|:---|:---|
| v1 | 先秦政治 | ✅ 220卡 |
| v2 | 秦汉制度 | ✅ 220卡 |
| v3 | 魏晋南北朝 | ✅ (规划) |
| v4 | 隋唐五代 | ✅ (规划) |

## 输入

- `1_ingest/` 输出的 `*.ingested.json`

## 输出

- `scene_v2/*.json` → 送入 `3_render/`
- `_source/` 脚本镜像 → D:/4_data/education/TextExperience/_source/
- `_intermediate/` 中间产物 → D:/4_data/education/TextExperience/_intermediate/

## 技术栈

- Python 3.x + LLM API（DeepSeek-v4-flash）
- JSON Schema：scene_v2（见 `schemas/scene_v2.schema.json`）
- 配置包：`cafa_calligraphy_2026/`（国美书法备考专用）

## 当前状态

**运行中** — TextExperience 主体位于此目录，Maturity: 0.8
