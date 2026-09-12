# 数学学科 — PT-030 工具链应用方案 v1.0

> **拍板**：雪薇端 (mavis 学生助手) — 2026-09-12 21:00 北京时间
> **配套**：`PT-030/curriculum/数学.md` (学科规划) + `tools/math_pipeline.py` (雪薇端 helper)
> **状态**：端到端验证通过 (2024 上海数学原卷 docx → 22 题, 4 选项, 0 答案)

---

## 一、工具链能力总结 (PT-030 v1.0)

| 命令 | 用途 | 雪薇端现状 |
|---|---|---|
| `parse-pdf` | C1 PDF 解析 (pypdf 6.18.1) | ✅ 已就绪 |
| `parse-docx` | C1 docx 解析 (python-docx 1.2.0) | ✅ 已就绪 |
| `parse-doc` | C1 老 .doc 解析 (pywin32 312, 需 MS Word) | ✅ 已就绪 (需 Word) |
| `parse-batch` | 批量解析目录下所有格式 | ✅ 已就绪 |
| `split` (v1.1) | C2 题目切分 | ⚠️ main bug (见 §五), 用 math_pipeline 绕开 |
| `pipeline` | C1+C2 一体化 | ⚠️ 同 split bug |
| `llm-gen` | C3.1 GLM-5 出题 (实际 glm-4-flash) | ✅ 已就绪, 需 ZHIPU_API_KEY |
| `llm-review` | C3.2 glm-4-flash 推演 | ✅ 已就绪, 需 ZHIPU_API_KEY |
| `info / version` | 路径/版本查询 | ✅ 已就绪 |

**依赖安装** (onboarding §3.2, 已在本机完成):
```bash
pip install pypdf python-docx pyyaml zhipuai pywin32
# 已装: pypdf 6.18.1, python-docx 1.2.0, pyyaml 6.0.3, zhipuai 2.1.5.20250825, pywin32 312
```

---

## 二、数学学科现状盘点 (2026-09-12)

### 2.1 已沉淀资产 (3 层)

| 层级 | 数量 | 位置 | 状态 |
|---|---:|---|---|
| **145 张单题 K 卡** (91apu + 本地上海) | 145 | `D:\Z_学习平台\knowledge-cards-prod\projects\math\cards\` | ✅ 闭环 |
| **30 张方法论卡** (6 板块 × 5 方法) | 30 | `D:\Z_学习平台\knowledge-cards-prod\projects\math\methods\` | ✅ 闭环 |
| **原卷切分 JSON** (2016/2017/2018/2020/2021/2023) | 90+ | `…/math\cards\本地上海\解析版\` + `…\原卷\` | ✅ 手工切 |
| **4 步法 v1.1 K 卡** (宇兄端产, 56 张) | 56 | 共同仓 commit c480706 | ✅ |

### 2.2 数学高考原料 (E 盘, 2026-09-12 探查)

```
E:\我的数据\上海高考试卷\上海高考数学1990-2025\
├── 春考卷（2017-2025）\       — 9 套 × 2 版 (原卷+解析) = 18 docx/doc
└── 秋考卷（1990-2025）\       — 26 套 × 2 版 ≈ 60 docx/doc

E:\我的数据\上海高考数学真题\   — 21 份散装 (1990-2023, 与上面有重叠)

总计: ~80 份 .docx/.doc, 覆盖 1990-2025 (春+秋) 36 年
```

**之前缺口**: D 盘没找到数学高考 PDF/doc, 现在 E 盘 80 份完全充足!

### 2.3 PT-030 共同仓现状 (数学部分)

| 文件 | 状态 |
|---|---|
| `PT-030/zhenti/数学/INDEX.md` | ✅ 已写 (雪薇端 9-12 cde77b6 commit) |
| `PT-030/curriculum/数学.md` | ✅ 已写 (同上) |
| `PT-030/methodology/4step_v1.1.md` | ✅ 已写 (宇兄端 MATH_001+004 镜像) |
| `PT-030/zhenti/数学/raw/` | ✅ 已建 (本方案落地) |
| `PT-030/zhenti/数学/split/` | ✅ 已建 (本方案落地) |

---

## 三、PT-030 工具链对数学的应用 (按优先级)

### P0 立即 (今天完成) ✅

| 任务 | 状态 | 命令 |
|---|---|---|
| git pull 拉工具链 v1.0 | ✅ | `git pull origin master` |
| 写 config.yaml (路径 + API key) | ✅ | `tools/pt030_toolkit/config.yaml` |
| 装依赖 (pypdf/docx/yaml/zhipuai/pywin32) | ✅ | `pip install ...` |
| 验证 CLI info | ✅ | `python -m pt030_toolkit.cli info` |
| 写 math_pipeline.py helper (绕开 split main bug) | ✅ | `tools/math_pipeline.py` |
| 端到端干跑 2024 上海数学原卷 docx | ✅ | 22 题, 4 选项, 0 答案 |

### P1 本周 (数学真题库扩产)

#### 任务 1.1: 批量解析 2017-2025 春考卷 (9 套原卷)
```bash
# 春考 9 套 (2017-2025 原卷版, docx 优先)
python tools/math_pipeline.py --batch "E:\我的数据\上海高考试卷\上海高考数学1990-2025\春考卷（2017-2025）" --filter 原卷
# 预期: 9 套 raw.json + 9 套 split_v11.json, 每套 20-22 题
# 落点: PT-030/zhenti/数学/{raw,split}/
```

#### 任务 1.2: 批量解析 2016-2025 秋考卷 (10 套原卷)
```bash
# 秋考 2016-2025 原卷版, docx 优先
python tools/math_pipeline.py --batch "E:\我的数据\上海高考试卷\上海高考数学1990-2025\秋考卷（1990-2025）" --filter 原卷
# 预期: 10 套 × 20-22 题 = 200+ 题
```

#### 任务 1.3: 跑 llm-review 给 22 题加答案/解析
```bash
# 对每套 split_v11.json 跑 glm-4-flash 推演
# 注意: 需先 set $env:ZHIPU_API_KEY="..." (已写在 config.yaml, 也可环境变量)
python tools/math_pipeline.py --review-only "D:\Z_学习平台\SPDT-004_EduContent\PT-030\zhenti\数学\split\2024年上海高考数学真题（原卷版）_split_v11.json"
# 预期: 加 verdict/answer/explanation/variants 字段
# 落点: 同 split/ 目录, _reviewed.json 后缀
```

#### 任务 1.4: 1990-2015 老试卷 (.doc) 批量解析
```bash
# 老试卷 .doc 1990-2015, 共 ~50 份
# 需 MS Word 安装 (parse_doc 依赖 win32com + Word.Application)
python tools/math_pipeline.py --batch "E:\我的数据\上海高考试卷\上海高考数学1990-2025\秋考卷（1990-2025）" --filter 老doc
# 预期: 1990-2015 50 套 .doc → 50 raw.json + 50 split_v11.json
# 已知限制: 2005+ 老试卷可能含扫描图片, 题号识别 0-10 题
```

### P2 本月 (LLM 出新母题 + 关联)

#### 任务 2.1: 补全薄弱板块母题
数学 6 板块密度: 立体几何 27 + 解析几何 30 + 导数 30 + 数列 24 + 概率 22 + 解三角形 12
薄弱板块: **解三角形 (12) + 概率 (22)**

```bash
# 为主题"解三角形"生成 5 道母题候选
python -m pt030_toolkit.cli llm-gen "解三角形" --count 5 --subject 数学
# 落点: PT-030/zhenti/数学/llm_gen/解三角形_gen.json

# 人工筛选 1-2 道, 跑推演
python -m pt030_toolkit.cli llm-review PT-030/zhenti/数学/llm_gen/解三角形_gen.json
# 落点: 同目录, _reviewed.json
```

#### 任务 2.2: 给 145 张 K 卡加 v1.1 11 字段
```bash
# 现有 tools/upgrade_pps_v11.py 已有
python tools/upgrade_pps_v11.py --batch --input D:\Z_学习平台\knowledge-cards-prod\projects\math\cards\
# 落点: 同目录, _v11.json 后缀
# 范围: 雪薇端可加 v1.1 11 扩展字段, 不动 v1.0 5 核心字段 (禁区)
```

#### 任务 2.3: 90+ 张原卷/解析版 JSON 跑 llm-review
```bash
# 对 D:\Z_学习平台\knowledge-cards-prod\projects\math\cards\本地上海\原卷\* 跑 review
# 价值: 补全 verdict/answer/explanation/variants 字段
```

### P3 长期 (与 3 学科对齐)

#### 任务 3.1: 单题 K 卡 → 卷级 bank_summary 升级
- 现状: 数学 145 张单题 K 卡, 历史/地理/政治是卷级 bank_summary
- 价值: 统一 6 学科格式
- 工具: PT-030 没现成, 雪薇端自写 (用 _scrape_91apu_* 脚本模式)

#### 任务 3.2: 与 4 步法 56 张 v1.1 卡 + 30 张方法论卡关联 chain_id
- 现状: 145 + 30 + 56 = 231 张 K 卡, 没有统一 chain_id
- 价值: 串成知识链 (概念→母题→变形→综合)
- 工具: 雪薇端写 chain_id 关联脚本

---

## 四、math_pipeline.py 雪薇端 helper 用法

### 4.1 安装/配置 (一次性)
```bash
# 1. 拉仓
cd D:\Z_学习平台\SPDT-004_EduContent
git pull origin master

# 2. 装依赖
pip install pypdf python-docx pyyaml zhipuai pywin32

# 3. 配 config.yaml (本仓已有, 雪薇端路径已写好)
# tools/pt030_toolkit/config.yaml
```

### 4.2 常用命令 (一行搞定)
```bash
# 设置 PYTHONPATH (PowerShell 一次性)
$env:PYTHONPATH = "D:\Z_学习平台\SPDT-004_EduContent\tools;$env:PYTHONPATH"
$env:PYTHONIOENCODING = "utf-8"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# 单文件: 解析 + 切分
python tools/math_pipeline.py "E:\我的数据\上海高考试卷\...2024原卷.docx"

# 批量: 解析目录下所有 docx/doc/pdf
python tools/math_pipeline.py --batch "E:\我的数据\上海高考试卷\上海高考数学1990-2025\春考卷（2017-2025）"

# 只跑 C1 (parse), 不切分
python tools/math_pipeline.py --parse-only <file>

# 只跑 C2 (用已有 raw.json)
python tools/math_pipeline.py --split-only <raw.json>

# 跑 C3 (LLM 推演, 对 split_v11.json 加答案/解析)
python tools/math_pipeline.py --review-only <split.json>
```

### 4.3 落点规则
- raw: `D:\Z_学习平台\SPDT-004_EduContent\PT-030\zhenti\数学\raw\<stem>_raw.json`
- split: `D:\Z_学习平台\SPDT-004_EduContent\PT-030\zhenti\数学\split\<stem>_split_v11.json`
- review: 同 split/ 目录, `<stem>_split_v11_reviewed.json`
- llm-gen: `PT-030/zhenti/数学/llm_gen/<theme>_gen.json`

---

## 五、已发现的工具链 bug (建议宇兄端修复)

| Bug | 文件:行 | 影响 | 建议 |
|---|---|---|---|
| `main()` 不接收 argv[2] 输出路径 | `tools/split_questions_v11.py:390-417` | `cli split` / `cli pipeline` 都写不出 split 文件 | 修 main: `out = Path(sys.argv[2]) if len(sys.argv) > 2 else None` |
| docstring `\9` 警告 | `tools/parse_docx_exam.py:4` | SyntaxWarning, 不影响功能 | docstring 加 `r"""..."""` |
| docstring `\<` 警告 | `tools/split_questions_v11.py:17` | SyntaxWarning, 不影响功能 | docstring 加 `r"""..."""` |

**临时方案**: 用 `math_pipeline.py` 调 `split_raw_file_v11()` 函数, 绕过 main bug。

---

## 六、跨窗口协作 (按 v1.1 分工)

| 任务 | 雪薇端 (本机) | 宇兄端 |
|---|---|---|
| 真题挖掘 (parse + split) | ✅ 已就绪, math_pipeline 一行搞定 | — |
| 答案/解析 (llm-review) | ✅ 已就绪, 用本机 ZHIPU_API_KEY | — |
| 母题出题 (llm-gen) | ✅ 已就绪 | — |
| display_target 字段 (v3.0) | ✅ 已补全 1355 个 JSON | — |
| validator 校验 | — | ⏳ 24h 内 review |
| 高难度算法 (PDF 选项检测 v1.1) | — | ⏳ roadmap v1.1 |
| 答案区智能提取 (v1.2) | — | ⏳ roadmap v1.2 |

**雪薇端交付物 (本方案)**: 跑通 2024 上海数学原卷 docx 端到端, 22 题 split_v11.json 入仓, math_pipeline helper 入仓.

---

## 七、3 句话总结

**1. PT-030 工具链对数学完全可用** — E 盘 80 份原料充足, 依赖装齐, CLI 端到端验证通过 (2024 22题 4选项)
**2. 5 大应用场景**: 批量解析真题 / LLM 推演答案 / 主题出母题 / K 卡 v1.1 升级 / 4 步法 chain 关联
**3. 1 个 helper + 1 套规划**: `tools/math_pipeline.py` 绕开宇兄端 split main bug, 本文档入 PT-030 共同仓

---

**作者**: 雪薇端 (mavis 学生助手)
**时间戳**: 2026-09-12 21:00 北京时间
**配套**:
- `tools/pt030_toolkit/config.yaml` (路径 + API key)
- `tools/math_pipeline.py` (雪薇端 helper)
- `PT-030/curriculum/数学.md` (学科规划)
- `PT-030/zhenti/数学/INDEX.md` (题库索引)
- `PT-030/methodology/4step_v1.1.md` (方法论)
