# 地理 zhenti 索引 (PT-030)

> **闭环状态**：✅ 46 卷 2178 题
> **覆盖年份**：1990-2021 + 2024
> **schema**：zhenti v1.0
> **源头**：`knowledge-cards-prod/projects/gaokao-geography/zhenti/`

---

## 一、46 卷 2178 题

| 维度 | 数量 |
|---|---:|
| 总卷数 | 46 |
| 总题数 | **2178** |
| has_answer | 11 |
| has_issue | 0 |
| 覆盖年份 | 1990-2021 + 2024 |

## 二、源头路径

```
D:\Z_学习平台\knowledge-cards-prod\projects\gaokao-geography\zhenti\
├── papers/
│   ├── g1990_01.json ~ g2021_*.json   (45 卷, 1990-2021)
│   └── g2024_*.json                   (1 卷, 2024)
├── sources/                            # 46 .txt
├── tools/                              # 2 个 _*.py
└── bank_summary.json                   # 索引 (46 条)
```

## 三、关键 commit 链

- `e591000` — 46 卷 2178 题入仓
- `ac8338d` — 三件套精写 19 专题 88 quiz

## 四、display_target 字段

按 v3.0 拍板，雪薇端产卡默认 `["学习中心"]`。
- bank_summary 顶层字段 (v1) 不含 display_target
- papers/*.json 已补全

## 五、跨机数据流

```
雪薇端 knowledge-cards-prod/projects/gaokao-geography/
   ↓ 46 卷 2178 题 + 19 专题 quiz
PT-030/zhenti/地理/ (本目录, 索引)
   ↓
宇兄端 review + validator 跑回归
```

## 六、立即可做

- **催另一 AI 补 49 专题 v0.4 cards/** (空目录)
- **地理方法论卡 5 张** (中优) — 按数学 6 板块 × 5 方法模式
- **2025 上海地理扩产** (中优) — 现有 1990-2021+2024, 2025 待补
- **has_answer 比例提升** — 11/46 (24%) → 目标 80%+
- **PT-030 入口** → `PT-030/curriculum/地理.md`
