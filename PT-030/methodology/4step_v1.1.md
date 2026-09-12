# 4 步法 v1.0 + 母题构建 v1.1 (PT-030 methodology)

> **来源**：共同仓 `handoff/MATH_001_4步法_概念-母题-变形-综合_v1.0.md` + `handoff/MATH_004_母题构建方法论_v1.1.md`
> **作者**：宇兄端
> **雪薇端用法**：PT-030 真题卡内容生产 + 4 步法数学 56 张 v1.1 卡 (commit c480706)

---

## 一、4 步法 v1.0 框架 (MATH_001)

**核心循环**：概念 → 母题 → 变形 → 综合

| 步骤 | 输出 | 示例 (数学) |
|---|---|---|
| **1. 概念** | 知识点定义 + 易错点 | 函数单调性定义 |
| **2. 母题** | 该概念的代表性题目 (高考真题优先) | 2018 导数大题 |
| **3. 变形** | 同知识点不同角度/不同难度的题目 | 2019/2020 同类变形 |
| **4. 综合** | 跨知识点综合题 | 导数+解析几何 |

## 二、母题构建方法论 v1.1 (MATH_004)

**11 扩展字段** (v1.0 → v1.1 升级)：

| 字段 | 用途 |
|---|---|
| `source_type` | 来源类型 (高考真题/模拟题/原创) |
| `difficulty` | 难度 (A/B/C/D) |
| `board` | 板块 (立体几何/解析几何/...) |
| `concept_id` | 关联概念 ID |
| `chain_id` | 链 ID (跨题关联) |
| `card_id` | 卡片 ID |
| `schema_version` | schema 版本 |
| `display_target` | 渲染目标 (默认 `["学习中心"]`) |
| `tags` | 标签数组 |
| `related_cards` | 关联卡片 ID 数组 |
| `prerequisites` | 前置知识 ID 数组 |

## 三、与 PT-030 的关系

- **4 步法** = **如何训练** (方法论) — 宇兄端工具方法论
- **PT-030 真题** = **训练什么** (内容) — 雪薇端真题挖掘
- **4 步法母题可来源于 PT-030 真题** — `MATH_005_5道历史真题改造为母题原型.md` 是桥接示例

## 四、相关 handoff 文档

- `handoff/MATH_001_4步法_概念-母题-变形-综合_v1.0.md` — 4 步法 v1.0 规范
- `handoff/MATH_002_网页版MVP架构_v1.0.md` — 网页版 MVP 架构
- `handoff/MATH_004_母题构建方法论_v1.1.md` — 11 扩展字段
- `handoff/MATH_005_5道历史真题改造为母题原型.md` — 5 道改造示例
- 共同仓 4 步法数学 56 张 v1.1 卡 (commit c480706) — 宇兄端已产

## 五、雪薇端用法

### 5.1 工具链

```bash
# v1.0 → v1.1 升级
python tools/upgrade_pps_v11.py --input v10.json --output v11.json

# validator 校验
python tools/math_4step_validator.py --batch --dir <generated>

# GLM-4-flash 反向推演
python tools/glm5_check.py --input v11.json
```

### 5.2 立即可做

- **2018 上海历史 20 题 v1.1 → v1.2 升级** (高优本周) — 用 `upgrade_pps_v11.py` 加 11 字段
- **PT-030 真题卡生产** (按 RUJING_006 v1.1 规范)
- **display_target 字段** (按 v3.0 拍板, 默认 `["学习中心"]`)
