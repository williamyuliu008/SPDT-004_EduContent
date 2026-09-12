# PT-030 真题处理工具包 (pt030_toolkit) v1.0

**跨机协作**: 宇兄端 ↔ 雪薇端
**作者**: 宇兄窗口 (开发助手)
**版本**: v1.0 (2026-09-12)

---

## 一、5 分钟上手 (雪薇端)

### Step 1: 拉代码

```bash
cd /path/to/your/SPDT-004_EduContent
git pull origin master
```

### Step 2: 配置路径 (3 选 1)

**A. 复制 config 模板**:
```bash
cp tools/pt030_toolkit/config.yaml.example tools/pt030_toolkit/config.yaml
# 编辑 config.yaml, 改路径为雪薇端机器的实际路径
```

**B. 环境变量覆盖** (推荐临时切换):
```bash
# Windows PowerShell
$env:PT030_RAW_DIR = "D:\Users\xuewei\data\rujing_out\真题主库\raw"
$env:PT030_SPLIT_DIR = "D:\Users\xuewei\data\rujing_out\真题主库\split"

# Linux/macOS bash
export PT030_RAW_DIR=/Users/xuewei/data/rujing_out/真题主库/raw
export PT030_SPLIT_DIR=/Users/xuewei/data/rujing_out/真题主库/split
```

**C. 什么都不改** (用默认路径 D:\\4_data\\... — 仅宇兄端机器)

### Step 3: 安装依赖

```bash
pip install pypdf python-docx pyyaml zhipuai

# .doc 老试卷 (1990-2017 上海高考) 需要 win32com + Word
# 仅 Windows + MS Word 16.0+
pip install pywin32
```

### Step 4: 验证

```bash
# Linux/macOS
export PYTHONPATH=tools:$PYTHONPATH
python -m pt030_toolkit.cli info
python -m pt030_toolkit.cli --version

# Windows PowerShell
$env:PYTHONPATH = "tools;$env:PYTHONPATH"
python -m pt030_toolkit.cli info
python -m pt030_toolkit.cli --version
```

期望输出:
```
pt030_toolkit v1.0.0
PT-030 toolkit path config:
  config file:        (未找到, 用默认值)
  RAW_DIR:            D:\4_data\rujing_out\真题主库\raw
  SPLIT_DIR:          D:\4_data\rujing_out\真题主库\split
  ...
```

---

## 二、命令速查

### C1 试卷解析 (PDF / docx / doc)

| 命令 | 用途 | 输出 |
|------|------|------|
| `parse-pdf <pdf>` | PDF 解析 | `<RAW_DIR>/<stem>_raw.json` |
| `parse-docx <docx>` | docx 解析 | `<RAW_DIR>/<stem>_raw.json` |
| `parse-doc <doc>` | .doc 老试卷 (1990-2017) | `<RAW_DIR>/<stem>_raw.json` |
| `parse-batch <dir>` | 批量解析目录下所有 | 多个 raw.json |

### C2 题目切分

| 命令 | 用途 | 输出 |
|------|------|------|
| `split <raw.json>` | v1.1 切分 (28题/选项/题型/页脚清理) | `<SPLIT_DIR>/<stem>_split_v11.json` |

### C1+C2 一体化流水线

| 命令 | 用途 | 输出 |
|------|------|------|
| `pipeline <pdf/docx/doc>` | C1→C2 自动流水线 | `<SPLIT_DIR>/<stem>_split_v11.json` |

### C3 双 LLM 协作 (新增 v1.0)

| 命令 | 用途 | 输出 |
|------|------|------|
| `llm-gen <theme>` | GLM-5 出题 (实际用 glm-4-flash) | `<真题主库>/llm_gen/<subject>_<theme>_gen.json` |
| `llm-review <json>` | glm-4-flash 推演验证 (答案/解析/变式) | `<input>_reviewed.json` |

### 工具

| 命令 | 用途 |
|------|------|
| `info` | 显示路径配置 (debug) |
| `--version` | 显示版本 |

---

## 三、典型工作流 (雪薇端)

### 流程 A: 处理新 PDF 真题

```bash
# 1. C1+C2 一体化 (推荐)
python -m pt030_toolkit.cli pipeline /path/to/2018_上海_高考_历史.pdf
# → 输出 D:\4_data\rujing_out\真题主库\split\2018_上海_高考_历史_split_v11.json

# 2. C3 双 LLM 协作 (推演 + 加答案/解析)
python -m pt030_toolkit.cli llm-review \
    D:\4_data\rujing_out\真题主库\split\2018_上海_高考_历史_split_v11.json
# → 输出 reviewed.json (含 verdict/answer/explanation/variants)

# 3. 人工 review 后, 转学习中心 zhenti 卡片
# (此步骤雪薇端主导, 4 步法 v1.1 模板填充 + display_target: ["学习中心"])
```

### 流程 B: 处理 .doc 老试卷 (1990-2017)

```bash
# 1. 批量解析目录下所有 .doc
python -m pt030_toolkit.cli parse-batch \
    "D:\9_archive\上海高考试卷\上海高考历史1990-2019、24\"
# → 44 个 raw.json 写入 RAW_DIR (约 14s)

# 2. 切分 (仅对 1990/1993/1998 等纯文本 doc 有效)
for raw in D:\4_data\rujing_out\真题主库\raw\*.json; do
    python -m pt030_toolkit.cli split "$raw"
done
```

### 流程 C: 出新母题 (4 步法 v1.1 模板)

```bash
# 1. GLM-5 出题 (实际 glm-4-flash)
python -m pt030_toolkit.cli llm-gen "函数与极限" --count 5 --subject 数学
# → 5 道母题草稿

# 2. 推演验证
python -m pt030_toolkit.cli llm-review /path/to/数学_函数与极限_gen.json
# → 加 verdict/answer/explanation/variants

# 3. 人工筛选 + 4 步法 v1.1 字段填 (宇兄端已有 pp_001-015 模板)
```

---

## 四、依赖矩阵

| 工具 | 必需依赖 | 平台 |
|------|---------|------|
| parse_pdf_exam | pypdf >= 3.0 | 全平台 |
| parse_docx_exam | python-docx | 全平台 |
| parse_doc_exam | pywin32 + Word 16.0+ | **仅 Windows** |
| split_questions_v11 | (无, 纯 Python) | 全平台 |
| glm5_question_gen | zhipuai >= 2.0 | 全平台 (API 在线) |
| glm4_flash_review | zhipuai >= 2.0 | 全平台 (API 在线) |
| pt030_toolkit (本包) | pyyaml | 全平台 |

**Windows 用户**: `pip install pypdf python-docx pyyaml zhipuai pywin32`
**macOS/Linux 用户**: `pip install pypdf python-docx pyyaml zhipuai` (不能跑 .doc 解析)

---

## 五、API Key 配置

GLM API key 从以下来源读取 (优先级):

1. 命令行 `--api-key xxx`
2. 环境变量 `ZHIPU_API_KEY`
3. config.yaml `glm5_api_key` / `glm4_flash_api_key`

**注意**: 智谱 AI 的 GLM-5 经常被 reasoning 占满 max_tokens (实测 4000 token 全部 reasoning, content 0 chars)
本工具包**实际用 glm-4-flash** (已验证 pp_001 推演 ✓ PASS), GLM-5 仅作 brainstorming 候选

---

## 六、路径优先级

```
环境变量 PT030_RAW_DIR  >  config.yaml raw_dir  >  代码默认值
```

例如雪薇端希望 raw 输出到 `/Users/xuewei/data/raw`:
```bash
export PT030_RAW_DIR=/Users/xuewei/data/raw
# 此时所有解析工具输出到 /Users/xuewei/data/raw
```

---

## 七、不在打包范围 (4 步法独立体系)

4 步法母题/卡片 (数学 56 张 + 历史 5 张) 走独立体系, 不在 pt030_toolkit 范围:

- `tools/math_4step_validator.py` - 4 步法验证器
- `tools/upgrade_pps_v11.py` - 母题升 v1.1 工具
- `tools/draw_pp_figures.py` - 母题 SVG 配图
- `tools/glm5_check.py` - pp_001 推演 (验证)
- `products/math_4step_mvp/` - Flask 网页版

4 步法直接用 `python tools/xxx.py`, 不通过 pt030_toolkit CLI。

---

## 八、跨机数据流 (5 步自动化)

```
宇兄端 (开发)  工具 + 验证
   |
   v
[C1]  工具: parse_pdf / parse_docx / parse_doc
   |
   v
raw.json  (git push 共同仓)
   |
   v
[C2]  工具: split_questions_v11
   |
   v
split_v11.json  (git push 共同仓)
   |
   v
雪薇端 (学生)  主导: 知识挖掘 + 真题库
   |
   v
[C3.1] 工具: llm-gen  (GLM-5 出题)
   |
   v
gen.json  (雪薇端本地)
   |
   v
[C3.2] 工具: llm-review  (glm-4-flash 推演)
   |
   v
reviewed.json  (雪薇端本地)
   |
   v
人工 review + 4 步法 v1.1 字段填 + display_target
   |
   v
PT-030/zhenti/<学科>/ 母题卡片  (git push 共同仓)
```

---

## 九、故障排查

| 问题 | 解决 |
|------|------|
| `ModuleNotFoundError: pt030_toolkit` | 漏设 PYTHONPATH, 参见 Step 4 |
| `yaml not found` | `pip install pyyaml` |
| `No module named win32com` | .doc 解析仅 Windows + Word, 其他平台忽略 |
| `API key missing` | 设 ZHIPU_API_KEY 环境变量 |
| `GLM-5 content 0 chars` | 已知 bug, 自动 fallback glm-4-flash |
| `PDF 选项检测 0 个` | v1.0 已知限制, v1.1 改进中 (C2 v1.1 已修 Q1 边界) |
| `路径不存在` | RAW_DIR/SPLIT_DIR 等会自动 mkdir, 但父目录需可写 |

---

## 十、版本演进

| 版本 | 日期 | 关键改进 |
|------|------|---------|
| v1.0 | 2026-09-12 | 5 核心解析器 + C3 双 LLM 模板 + CLI 入口 + 路径配置 |

**未来规划**:
- v1.1: C1 选项检测改进 (修复 v1.0 0 选项 bug)
- v1.2: C2 答案区智能提取 (PDF 末尾"试题答案"区按题号匹配)
- v2.0: 雪薇端 6 学科 zhenti 库接入 (PT-030/zhenti/<学科>/)
- v3.0: 双 LLM 协作升级 (GLM-5 brainstorming + glm-4-flash 正式 + 人工 review 流水线)

---

## 联系 / 反馈

- 共同仓: https://github.com/williamyuliu008/SPDT-004_EduContent
- 双窗口协作规范: `handoff/SPDT004_DUAL_WINDOW_COLLABORATION_v1.0_给雪薇窗口.md`
- 工具链交付说明: `handoff/PT-030_工具链_v1.0_交雪薇端.md`
