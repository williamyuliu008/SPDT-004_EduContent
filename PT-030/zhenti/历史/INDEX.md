# 历史 zhenti 索引 (PT-030)

> **闭环状态**：✅ 44 卷 1602 题
> **覆盖年份**：1990-2017 + 2024
> **schema**：zhenti v1.0 + v2.0
> **源头**：`knowledge-cards-prod/projects/gaokao-history/zhenti/`

---

## 一、44 卷 1602 题

| 维度 | 数量 |
|---|---:|
| 总卷数 | 44 (38 + 6 占位) |
| 总题数 | **1602** |
| has_answer | 22 |
| has_issue (6 占位) | 6 (`h1996/h1997/h2001_12/13/h2003/h2004`) |
| 覆盖年份 | 1990-2017 + 2024 |

> 6 占位已 commit `0d13fdc` 修复追溯。

## 二、源头路径

```
D:\Z_学习平台\knowledge-cards-prod\projects\gaokao-history\zhenti\
├── papers/
│   ├── h1990_01.json ~ h2017_44.json   (38 卷, 1990-2017)
│   └── 2024/                            (2 卷, 2024 .txt 源)
├── sources/                              # 2 个 2024 .txt
├── tools/                                # 转换/校验脚本
└── bank_summary.json                     # 索引 (44 条)
```

## 三、bank_summary.json 字段示例 (v1)

```json
{
  "key": "h1990_01",
  "year": "1990",
  "orig": "1990年上海高考历史真题及答案.doc",
  "questions": 45,
  "choice": 33,
  "has_answer": true,
  "compact_ans": 20,
  "chars": 6753
}
```

## 四、宇兄端 v1.2 70 题扩产 (RUJING_007) — 待 mirror

- 2017 + 2018 + 2019 上海历史
- 70 题 v1.2 (含 11 扩展字段)
- 入口：`PT-030/mirror/v1.2_70题历史/`
- 状态：⏳ 宇兄端机器未 push

## 五、关键 commit 链

- `c4ba424` — 44 卷入仓
- `0d13fdc` — fix 6 孤儿占位
- `ac8338d` — 三件套精写 7 专题 38 quiz

## 六、display_target 字段

按 v3.0 拍板，雪薇端产卡默认 `["学习中心"]`。
- bank_summary 顶层字段 (v1) 不含 display_target
- papers/*.json (v2 精修版) 已补全

## 七、立即可做

- **2018 上海历史 20 题 v1.1 → v1.2 升级** (高优本周) — 已写 1.1 20 题，待 upgrade_pps_v11.py
- **2017/2019/2024 上海历史扩产** (中优) — 宇兄端 v1.2 已做 70 题，雪薇端接力
- **历史方法论卡 5 张** (中优) — 按数学 6 板块 × 5 方法模式
- **PT-030 入口** → `PT-030/curriculum/历史.md`
