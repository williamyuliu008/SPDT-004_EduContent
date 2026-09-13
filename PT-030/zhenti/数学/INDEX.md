# 数学 zhenti 索引 (PT-030)

> **状态**: ✅ 工具链 v1.0 上线 + 真题 574 题入库 (2026-09-12 21:30)
> **覆盖年份**: 2016-2025 新高考 docx (26 套) + 1990-2015 老 .doc (66 套, 0 题)
> **schema**: PT-030 split_v11.json v1.1
> **源头**: `D:\Z_学习平台\SPDT-004_EduContent\PT-030\zhenti\数学\`

---

## 一、PT-030 工具链解析成果 (2026-09-12)

| 类别 | 文件 | 识别题数 | 备注 |
|---|---:|---:|---|
| **新高考 docx (2016-2025)** | 26 | **574** | 22 题/套, 8.4% 选项检测 |
| **老 .doc (1990-2015)** | 66 | 0 | 含扫描图片, 待 OCR |
| **春考解析版 (1 套推演)** | 1 | 21/22 | glm-4-flash 推演 |
| **llm-gen (4 主题)** | 4 | 12 道 | 解三角形/概率/数列/立体几何 |

**总计 26 套新高考 = 574 题入库**, 平均 22 题/套

---

## 二、6 板块真题 K 卡 (历史资产, 不冲突)

| 板块 | 张数 | 质量评级 | 抓取工具 |
|---|---:|---|---|
| 立体几何 | 27 | A | `_scrape_91apu_liti.py` (v1.2.9) |
| 解析几何 | 30 | **A** | `_scrape_91apu_5board.py` (v1.3.0) |
| 导数 | 30 | **A** | 同上 |
| 数列 | 24 | B+ | 同上 (2018-2020 课标卷归类需复核) |
| 概率统计 | 22 | A- | 同上 (课标卷 18 题 + 21 题) |
| 解三角形 | 12 | B | 同上 (新高考开始 q17 才是单纯解三角形) |
| **合计** | **145** | — | — |

---

## 三、本仓目录 (PT-030 zhenti/数学/)

```
PT-030/zhenti/数学/
├── INDEX.md                              ← 本文件
├── EXEC_REPORT_2026-09-12.md             ← 工具链执行报告
├── PLAN_PT030_TOOLKIT_v1.0.md            ← 工具链应用方案
├── raw/                                  ← C1 解析 (92 .json, .gitignore 隔离)
├── split/                                ← C2 切分 (91 .json + 1 reviewed)
└── llm_gen/                              ← C3.1 出题 (5 .json)
```

---

## 四、display_target 字段 (v3.0 拍板)

雪薇端产卡默认 `["学习中心"]`, 已在 1355 个 JSON 中补全 (commit b89a0e9).

PT-030 工具链生成的 raw/split JSON **未加** display_target (工具链产物非学习中心渲染对象), 需后续人工筛选用作 K 卡时再加.

---

## 五、跨机数据流

```
E:\我的数据\上海高考试卷\上海高考数学1990-2025\   ← 数学高考原料
   ↓ parse_pdf / parse_docx / parse_doc
PT-030/zhenti/数学/raw/                         ← 92 raw.json
   ↓ split_questions_v11
PT-030/zhenti/数学/split/                       ← 91 split_v11.json
   ↓ glm4_flash_review (按需)
PT-030/zhenti/数学/split/*_reviewed.json         ← 21 题推演 (95% 成功率)

llm_gen (按主题)                                 ← 4 主题 12 道新母题
   ↓
PT-030/zhenti/数学/llm_gen/<主题>_gen.json

宇兄端: 24h 内 review + validator 回归
```

---

## 六、立即可做 (按工具链接入)

- [x] 工具链 v1.0 上线 (math_pipeline.py helper 入仓)
- [x] 26 套新高考 docx 批量解析 (574 题入库)
- [x] 4 主题薄弱板块 llm-gen (12 道新母题)
- [x] 1 套 llm-review 验证 (21 题推演)
- [ ] 24 套剩余 split 跑 llm-review (~24 × 30s = 12 min, 总计 528 题推演)
- [ ] 90+ 张已切分原卷 JSON 跑 llm-review
- [ ] 145 张 K 卡 v1.1 升级 (11 扩展字段)
- [ ] 1990-2015 老 doc OCR 化 (待宇兄端 PDF 解析器 v1.1 同步)

---

## 七、相关文档

- `PT-030/curriculum/数学.md` — 学科规划
- `PT-030/methodology/4step_v1.1.md` — 4 步法
- `PT-030/methodology/display_target_v3.0.md` — v3.0 拍板
- `tools/math_pipeline.py` — 雪薇端 helper
- `tools/pt030_toolkit/README.md` — 工具链 README
- `handoff/PT-030_雪薇端启动报告_v1.0.md` — 雪薇端 v1.0 启动报告
