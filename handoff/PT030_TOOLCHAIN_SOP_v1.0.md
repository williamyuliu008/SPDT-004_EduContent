# PT-030 工具链 SOP v1.0 (2026-09-13)

> **拍板**: 雪薇 2026-09-13 "完成后整理 SOP 便于重用"
> **作者**: 雪薇端 (mavis root, 4 窗口)
> **工具链 commit**: 84e44bf → b7ad851 (8 commits)
> **总经验**: 8 天实战 (2026-09-12 → 2026-09-13) + 3.5h 全量推演

---

## 一、目标与适用场景

### 1.1 PT-030 是什么

**P**roblem-**T**ree **030** = 上海高考真题挖掘与加工项目 (子项目于 2026-09-12 启动)

**双窗口协作**:
- **雪薇端** (本机 D:\Z_学习平台\, 学生助手 AI): 真题数据挖掘主导
- **宇兄端** (另一台机, 开发助手 AI): 工具开发 + 验证

### 1.2 工具链能力 (C1+C2+C3 三步)

```
原始 PDF/docx/doc
    ↓ [C1] parse_pdf / parse_docx / parse_doc (pypdf 6.18+python-docx 1.2+pywin32)
raw.json (text + pages + 题号检测)
    ↓ [C2] split_questions_v11 (regex + 选项 split + 题号白名单)
split_v11.json (questions[] 数组, 每题 stem/options/answer_label)
    ↓ [C3.1] glm5_question_gen (主题出题)
gen.json (LLM 出的母题)
    ↓ [C3.2] glm4_flash_review / qwen_review (单题推演 verdict/explanation/variants)
reviewed.json (加 answer/explanation/variants/key_concepts/common_mistakes)
    ↓ [C4] merge_to_kcards (PT-030 产物 → K_card v1.2.1)
本地 K 卡库 (D:\Z_学习平台\knowledge-cards-prod\)
```

### 1.3 适用场景

| 场景 | 工具 | 耗时 |
|---|---|---|
| 新高考 docx 真题批量入库 | math_pipeline.py --batch | 1 套/秒 |
| 老 .doc 扫描图片题 | parse_doc_exam.py (需 MS Word) | 1 套/2-3s |
| LLM 推演答案/解析 | batch_review_qwen.py (Qwen) | 1 套/8-15 min |
| 启发式 → Qwen 重分类 | batch_reclassify_pt030.py | 1 张/12s |
| LLM 出新母题 (按主题) | llm_gen "解三角形" --count 3 | 1 主题/30s |
| 立体几何/函数专项升级 | batch_review_qwen_liti.py / batch_review_qwen_4panels.py | 1 张/25s |

---

## 二、环境配置 (一次性)

### 2.1 Python 依赖
```bash
pip install pypdf python-docx pyyaml zhipuai pywin32 httpx sniffio
```
**实际版本** (2026-09-13):
- pypdf 6.18.1
- python-docx 1.2.0
- pyyaml 6.0.3
- zhipuai 2.1.5.20250825
- pywin32 312
- httpx (最新)
- sniffio 1.3.1 (zhipuai 缺)

### 2.2 路径配置
```yaml
# tools/pt030_toolkit/config.yaml (本机路径)
raw_dir: D:/Z_学习平台/SPDT-004_EduContent/PT-030/zhenti/数学/raw
split_dir: D:/Z_学习平台/SPDT-004_EduContent/PT-030/zhenti/数学/split
zhenti_dir: D:/Z_学习平台/knowledge-cards-prod/projects/math
handbook_dir: D:/Z_学习平台/knowledge-cards-prod
pt030_root: D:/Z_学习平台/SPDT-004_EduContent/PT-030

# GLM API key (智谱) — 留空, 走环境变量
glm5_api_key: ""
glm4_flash_api_key: ""
# Qwen3.5-Plus (推荐) — 走环境变量 QWEN_API_KEY
```

### 2.3 环境变量
```powershell
$env:PYTHONPATH = "D:\Z_学习平台\SPDT-004_EduContent\tools;$env:PYTHONPATH"
$env:PYTHONIOENCODING = "utf-8"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:QWEN_API_KEY = "sk-..."      # 优先 (稳定 17-25s/题, 19% fail)
$env:ZHIPU_API_KEY = "dfe14..."   # 备选 (zhipuai SDK hang 风险)
```

### 2.4 关键修复点 (踩过的坑)
- **zhipuai SDK 内部 httpx 不接受 timeout** → 用 `review_qwen.py` 直调 Qwen API
- **split_questions_v11.py main 不收 argv[2]** → 用 `math_pipeline.py` 调函数绕开
- **PowerShell 5.1 默认 GBK** → 必须设 PYTHONIOENCODING=utf-8 + Console.OutputEncoding
- **中文文件名 glob 失败** → 用 Get-ChildItem -Recurse
- **JSON 写文件要 utf-8 编码** → `write_text(..., encoding='utf-8')`

---

## 三、工具清单 (D:\Z_学习平台\SPDT-004_EduContent\tools\)

| 工具 | 功能 | 输入 | 输出 |
|---|---|---|---|
| **math_pipeline.py** | C1+C2 端到端 (PDF/docx/doc → split) | 1 个文件 or 目录 | raw.json + split_v11.json |
| **parse_pdf_exam.py** | C1 PDF 解析 (pypdf) | .pdf | raw.json |
| **parse_docx_exam.py** | C1 docx 解析 (python-docx) | .docx | raw.json |
| **parse_doc_exam.py** | C1 .doc 解析 (pywin32 + Word COM, **仅 Windows**) | .doc | raw.json |
| **split_questions_v11.py** | C2 切分 (v1.1) | raw.json | split_v11.json |
| **run_c1_c2_pipeline.py** | C1+C2 一体化 (旧) | 文件 | split |
| **glm5_question_gen.py** | C3.1 GLM-5 出题 | 主题 | gen.json |
| **glm4_flash_review.py** | C3.2 GLM-4-flash 推演 (旧, zhipuai SDK hang) | split | reviewed.json |
| **review_qwen.py** | C3.2 Qwen3.5-Plus 推演 (推荐, 直调 API) | question dict | reviewed dict |
| **batch_review_qwen_liti.py** | 立体几何专项 | 立体几何 K 卡 | 升级 + 报告 |
| **batch_review_qwen_4panels.py** | 4 板块 (解析几何/导数/概率/解三角) | 4 板块 K 卡 | 升级 + 报告 |
| **batch_reclassify_pt030.py** | PT-030 重分类 | 560 张 K 卡 | 重打 module 标签 |
| **merge_to_kcards.py** | C4 PT-030 产物 → K_card v1.2.1 | PT-030 输出 | 本地 K 卡库 |
| **audit_liti_function.py** | 立体几何+函数/导数综合审核 | K 卡库 | 问题报告 |
| **audit_fix_back.py** | 审核修复 (back 字段 + 母题变式) | 4 板块 K 卡 | 修复 |

---

## 四、典型工作流 (3 场景)

### 场景 A: 新真题批量入库 (端到端)

```powershell
# 1. 启动环境
$env:PYTHONPATH = "D:\Z_学习平台\SPDT-004_EduContent\tools;$env:PYTHONPATH"
$env:PYTHONIOENCODING = "utf-8"
$env:QWEN_API_KEY = "sk-..."
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
cd D:\Z_学习平台\SPDT-004_EduContent

# 2. C1+C2 批量解析
python tools/math_pipeline.py --batch "E:\我的数据\上海高考试卷\上海高考数学1990-2025\秋考卷（1990-2025）"
# → 26 套 raw.json + 26 套 split_v11.json (约 30s)

# 3. Qwen 推演 (后台批量, 30-40 min)
python tools/batch_review_qwen_4panels.py
# → 200+ 张 K 卡 verdict/explanation/variants 升级

# 4. 重分类 (后台批量, 20 min)
python tools/batch_reclassify_pt030.py
# → 560 张 K 卡 module 标签修正 (启发式 → Qwen)

# 5. K 卡入库 (1s)
python tools/merge_to_kcards.py
# → 548 张 K_card v1.2.1 入库
```

### 场景 B: 主题出新母题 (C3.1)

```bash
# 出 3 道解三角形母题
python -m pt030_toolkit.cli llm-gen "解三角形" --count 3 --subject 数学
# → 写入 raw/../llm_gen/数学_解三角形_gen.json

# 或直接脚本 (更灵活)
python tools/glm5_question_gen.py "解三角形" --subject 数学 --count 3 --output gen.json
```

### 场景 C: 单题 Qwen 推演 (调试用)

```python
import sys
sys.path.insert(0, r'D:\Z_学习平台\SPDT-004_EduContent\tools')
from review_qwen import review_one_question, get_api_key
import os
api_key = os.environ.get('QWEN_API_KEY')

q = {
    'q_no': 1,
    'stem': '在△ABC中, 已知∠A=60°, ∠B=45°, 边AC=5, 求边BC的长度。',
    'options': [],
}
result = review_one_question(q, '数学解三角形', api_key, timeout=30)
print(result)
```

---

## 五、跨窗口协作 (按 v1.1 总计划)

### 5.1 双窗口分工
| 窗口 | 任务 | 工具 |
|---|---|---|
| **雪薇 4 窗口 (root Mavis)** | 真题挖掘 + LLM 推演 + 报告 + 通知 1 窗口 | 本 SOP 全套工具 |
| **雪薇 1 窗口 (agent1)** | 母题扩展 + 变形题挖掘 + 5 链挂接 | knowledge-cards-prod 直接编辑 |
| **雪薇 3 窗口 (UI 雪薇)** | 学习中心 UI 微调 | 浏览器实测 |
| **宇兄端** | 工具开发 + 验证 + 高难度算法 | 共同仓 PR review |

### 5.2 触发式协作
- 4 窗口每完成 1 个动作 → 立刻 commit (不等其他)
- 4 窗口写完 1 板块 → 写 handoff 通知 1 窗口
- 1 窗口建完母题 → 写 handoff 通知 4 窗口
- 3 窗口 UI 验证 → 雪薇决定何时 commit

### 5.3 关键 handoff 文档
- `handoff/PT-030_雪薇端启动报告_v1.0.md` — 雪薇端 v1.0 启动
- `handoff/root_to_agent1_2026-09-13_function_panel.md` — 函数板块派单
- `handoff/SPDT004_DUAL_WINDOW_COLLABORATION_v1.1_PT-030分工修正.md` — 双窗口分工
- `PT-030/zhenti/数学/EXEC_REPORT_2026-09-12.md` — 工具链执行报告
- `PT-030/zhenti/数学/QWEN_LITI_UPGRADE_REPORT_2026-09-13.md` — 立体几何升级
- `PT-030/zhenti/数学/FUNCTION_PANEL_4PANELS_REPORT_2026-09-13.md` — 函数板块升级
- `PT-030/zhenti/数学/AUDIT_REPORT_2026-09-13.json` — 综合审核

---

## 六、已知限制 & 异常处理

### 6.1 工具链已知问题

| 问题 | 触发条件 | 解决方案 |
|---|---|---|
| zhipuai SDK hang 死 | 单题调用 > 30s | 改用 `review_qwen.py` 直调 Qwen |
| GLM API 限流 | 1 分钟 > 60 次调用 | 切 Qwen + 减并发 |
| split_questions_v11 main 不收 argv[2] | `cli split` 或 `cli pipeline` 不写文件 | 用 `math_pipeline.py` 调函数 |
| 老 .doc 扫描图片 0 题 | 1990-2015 .doc 含图片 | 需 OCR (Tesseract) + 手工标注 |
| v1.0 PDF 选项检测 0 个 | C1 PDF 解析 | C2 v1.1 部分修复, 完整版 v1.1 待宇兄端 |
| v1.0 答案区 0 题 | C1 PDF 末尾"答案区" | v1.2 待宇兄端 |

### 6.2 数据流异常

| 异常 | 现象 | 处理 |
|---|---|---|
| Qwen 响应超 30s | `_error: timeout 30s` | retry 1-2 次, 仍 fail 则标 DRAFT |
| Qwen 返回无效 JSON | `_error: no JSON` | 截短 stem 后 retry |
| 重分类后模块错分 | 5 板块比例 < 80% | 人工 review + 二次 reclassify |
| 母题 derived_variants < 2 | 缺变式 | 跑 Qwen 推演 +2 变式 |

### 6.3 数据校验 (审核清单)

每次入库后跑 `tools/audit_liti_function.py`:
- 字段完整性 (id/maturity/front/back/options)
- Qwen 升级标记
- 母题变式 >= 2
- chain_id 格式
- ID 唯一性
- 错分类检测

发现 back 空 / 母题没 Qwen → 跑 `tools/audit_fix_back.py`

---

## 七、性能基准 (实测)

| 操作 | 耗时 | 备注 |
|---|---|---|
| 解析 1 套 docx | 1-2s | math_pipeline.py |
| 解析 1 套 .doc (Word COM) | 2-3s | 需 MS Word |
| Qwen 推演 1 题 | 17-25s | dashscope.aliyuncs.com |
| Qwen 出 1 母题 | 17-30s | glm-4-flash fallback |
| 重分类 1 张 | 8-15s | 短 prompt 200 token |
| 4 板块 200 张 K 卡 | 30-40 min | 后台并发 |
| PT-030 重分类 560 张 | 20-30 min | 串行 |
| K 卡合并 548 张 | < 1s | 本地写文件 |

---

## 八、Quick Start (新成员 5 分钟上手)

```powershell
# 1. 拉代码
cd D:\Z_学习平台\SPDT-004_EduContent
git pull origin master

# 2. 装依赖 (一次)
pip install pypdf python-docx pyyaml zhipuai pywin32 httpx sniffio

# 3. 配环境 (永久)
[System.Environment]::SetEnvironmentVariable("PYTHONPATH", "D:\Z_学习平台\SPDT-004_EduContent\tools", "User")
[System.Environment]::SetEnvironmentVariable("QWEN_API_KEY", "sk-...", "User")
[System.Environment]::SetEnvironmentVariable("ZHIPU_API_KEY", "dfe14...", "User")
# 重启 PowerShell 生效

# 4. 验证
$env:PYTHONPATH = "D:\Z_学习平台\SPDT-004_EduContent\tools;$env:PYTHONPATH"
$env:PYTHONIOENCODING = "utf-8"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
python -m pt030_toolkit.cli info
# 期望: 显示 RAW_DIR/SPLIT_DIR 等路径

# 5. 跑 1 套端到端
python tools/math_pipeline.py "E:\你的真题.docx"

# 6. 看结果
ls D:\Z_学习平台\SPDT-004_EduContent\PT-030\zhenti\数学\split\
```

---

## 九、扩展 (后续可加)

| 任务 | 价值 | 估时 |
|---|---|---|
| 老 .doc OCR 化 (1990-2015) | 补全 66 套扫描图片题 | Tesseract 装+跑 30 min |
| 145 张 K 卡 v1.1 升级 (11 字段) | 与 4 步法 v1.1 框架对齐 | 1 窗口工作 |
| 4 板块方法论 Qwen 升级 (剩 80%) | 跨 5 板块统一深度 | 1-2 h |
| PT-030 跑完原卷版 26 套 review | 补全 4 板块原卷答案 | 1-2 h |
| M2 函数板块母题 (K20-K34) | 1 窗口 agent1 | 1-2 h |
| M3 数列板块 | 1 窗口 | 30-60 min |
| M4 5 板块全闭环 | 雪薇实测 | 由你 |

---

**作者**: 雪薇端 (mavis root, 4 窗口)
**时间戳**: 2026-09-13 22:00
**commit**: b7ad851
**总实战**: 8 天 + 3.5h 全量推演
**总推演**: 222 张 K 卡升级 + 548 张重分类 + 12 道 LLM 新母题
