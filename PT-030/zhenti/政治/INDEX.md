# 政治 zhenti 索引 (PT-030)

> **闭环状态**：✅ 35 卷 1482 题
> **覆盖年份**：1990-2018
> **schema**：zhenti v1.0 + v2.0 (题型分类 + 答案配对)
> **源头**：`knowledge-cards-prod/projects/gaokao-politics/zhenti/`

---

## 一、35 卷 1482 题

| 维度 | 数量 |
|---|---:|
| 总卷数 | 35 (33 + 2 源空) |
| 总题数 | **1482** |
| has_answer | 19 |
| has_issue (2 源空) | 2 (`p2001_12/p2002_14`) |
| 覆盖年份 | 1990-2018 |

## 二、源头路径

```
D:\Z_学习平台\knowledge-cards-prod\projects\gaokao-politics\zhenti\
├── papers/
│   └── p1990_01.json ~ p2017_35.json   (35 卷, 1990-2017)
├── sources/                              # 35 .txt
├── tools/                                # 2 个 _*.py
└── bank_summary.json                     # 索引 (35 条)
```

## 三、v2 精修字段 (新增)

`questions_v2` 数组 + `stats` 题型统计：

```json
{
  "key": "p2017_35",
  "year": "2017",
  "questions": 23,
  "questions_v2": [
    {
      "number": "1",
      "type": "single_choice",          // single_choice/multi_choice/judge/matching/fill_blank/material_analysis/essay
      "stem": "题干...",
      "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
      "answer": "B",
      "has_answer": true,
      "explain": "解析...",
      "raw": "原始文本..."
    }
  ],
  "stats": {
    "single_choice": 18,
    "material_analysis": 3,
    "essay": 2
  }
}
```

## 四、关键 commit 链

- `180aceb` — 1990-2018 35 卷 949 题入仓 (v1)
- `1c3e05d` — 政治真题 v2 精修 35 卷 (题型分类 + 答案配对)
- `b4caf8c` — 政治方法论卡 5 张入仓 (唯物论/辩证法/政治/经济/开放论述)
- `9910f62` — 政治三件套精写 23 专题 99 quiz

## 五、display_target 字段

按 v3.0 拍板，雪薇端产卡默认 `["学习中心"]`。
- bank_summary 顶层字段 (v1) 不含 display_target
- papers/*.json v2 精修版已补全

## 六、立即可做

- **2 源空占位追溯** (p2001_12/p2002_14) — 找外部 AI 抓原 .doc 重解析
- **政治方法论卡扩展** (中优) — 已有 5 张 (唯物论/辩证法/政治/经济/开放论述)
- **2019-2024 上海政治扩产** (中优) — 35 卷基础上扩
- **has_answer 比例提升** — 19/35 (54%) → 目标 80%+
- **PT-030 入口** → `PT-030/curriculum/政治.md`
