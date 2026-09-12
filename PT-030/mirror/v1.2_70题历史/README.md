# Mirror 入口 — v1.2 70 题历史 (RUJING_007) — 待宇兄端 push

> **状态**：⏳ 宇兄端机器未 push
> **预期数据**：2017+2018+2019 上海历史 70 题 v1.2
> **拍板来源**：共同仓 `handoff/RUJING_007_真题卡v1.2扩产报告_70题.md` + `RUJING_007_真题卡扩产报告_2018-2019_2026-09-10.md`
> **雪薇端入口**：本目录 `PT-030/mirror/v1.2_70题历史/`

---

## 一、待 mirror 数据预期

按 RUJING_007：

| 维度 | 数量 |
|---|---:|
| 2017 上海历史 | 20 题 (v1.2) |
| 2018 上海历史 | 30 题 (v1.2) |
| 2019 上海历史 | 20 题 (v1.2) |
| **合计** | **70 题** |

每题 v1.2 = 11 扩展字段 (source_type / difficulty / board / concept_id / chain_id / card_id / schema_version / display_target / tags / related_cards / prerequisites)

## 二、mirror 流程

```
宇兄端机器 (autoclaw)
   ↓ 1. 产 70 题 v1.2 JSON
   ↓ 2. 跑 validator (tools/math_4step_validator.py)
   ↓ 3. commit + push 共同仓
共同仓 handoff/RUJING_007_* (已推)
   ↓ 雪薇端 git pull
雪薇端 (本机 mavis)
   ↓ 4. mirror 70 题 JSON → PT-030/mirror/v1.2_70题历史/2017/2018/2019/
   ↓ 5. 补全 display_target ["学习中心"]
   ↓ 6. commit + push 共同仓
宇兄端 review → 合入
```

## 三、目录预期结构 (待宇兄端 push)

```
PT-030/mirror/v1.2_70题历史/
├── README.md                          ← 本文件
├── 2017/
│   ├── INDEX.md                       ← 2017 20 题索引
│   └── 2017_上海_历史_真题卡_v1.2_20题.json
├── 2018/
│   ├── INDEX.md                       ← 2018 30 题索引
│   └── 2018_上海_历史_真题卡_v1.2_30题.json
└── 2019/
    ├── INDEX.md                       ← 2019 20 题索引
    └── 2019_上海_历史_真题卡_v1.2_20题.json
```

## 四、跨机协作

- 宇兄端负责 70 题 v1.2 生产 (本机 autoclaw, 另一台机器)
- 雪薇端负责 mirror + display_target 补全 (本机 mavis)
- 24h 内 PR review
- 学科前缀：`h` (历史), 2017/2018/2019 三卷

## 五、立即可做

- **等待宇兄端 push** (本机无法访问宇兄端 autoclaw 机器)
- **宇兄端 push 后, 雪薇端拉 + mirror + commit** (本目录入口)
- **PT-030 入口** → `PT-030/curriculum/历史.md` + `PT-030/zhenti/历史/INDEX.md`
