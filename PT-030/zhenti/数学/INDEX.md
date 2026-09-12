# 数学 zhenti 索引 (PT-030)

> **闭环状态**：✅ 145 张单题 K 卡
> **覆盖年份**：2018-2024 (91apu) + 2008-2023 (上海本地)
> **schema**：K_card v1.2.1 / v1.3.0
> **源头**：`knowledge-cards-prod/projects/math/`

---

## 一、6 板块 145 张 K 卡

| 板块 | 张数 | 质量评级 | 抓取工具 |
|---|---:|---|---|
| 立体几何 | 27 | A | `_scrape_91apu_liti.py` (v1.2.9) |
| 解析几何 | 30 | **A** | `_scrape_91apu_5board.py` (v1.3.0) |
| 导数 | 30 | **A** | 同上 |
| 数列 | 24 | B+ | 同上 (2018-2020 课标卷归类需复核) |
| 概率统计 | 22 | A- | 同上 (课标卷 18 题 + 21 题) |
| 解三角形 | 12 | B | 同上 (新高考开始 q17 才是单纯解三角形) |
| **合计** | **145** | — | — |

## 二、数学方法论卡 (30 张 v2.0.0)

`projects/math/methods/` (commit v2.0.0)

按 6 板块 × 5 方法模式：
- 概念 → 母题 → 变形 → 综合 → 易错点

## 三、源头路径

```
D:\Z_学习平台\knowledge-cards-prod\projects\math\
├── cards/                          # 145 张 K 卡
├── methods/                        # 30 张方法论卡
└── ALL_ZHENTI_INDEX.md             # 详细索引
```

## 四、display_target 字段

按 v3.0 拍板，雪薇端产卡默认 `["学习中心"]`。
- 145 张 K 卡 + 30 张方法论 = 175 个 JSON 已补全 display_target (commit b89a0e9)

## 五、跨机数据流

```
雪薇端 knowledge-cards-prod/projects/math/
   ↓ 145 张 K 卡 + 30 张方法论
PT-030/zhenti/数学/ (本目录, 索引)
   ↓
宇兄端 review + validator 跑回归
```

## 六、立即可做

- **2017/2019/2024 上海数学扩产** (中优) — 30+ 套老试卷
- **1990-2007 上海老卷补全** — 本地上海/ 已有部分
- **单题 K 卡 → 卷级 bank_summary 升级** — 与历史/地理/政治对齐
- **PT-030 入口** → `PT-030/curriculum/数学.md`
