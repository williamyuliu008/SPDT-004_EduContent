"""
PT-030 真题处理工具包 (PT-030 Toolkit)
======================================

统一入口, 跨机复用 (宇兄端 ↔ 雪薇端).

模块:
- config: 路径配置 (config.yaml + 环境变量覆盖)
- cli: 统一 CLI 入口 (python -m pt030_toolkit <command>)

不在此包内的工具 (原 tools/ 目录):
- parse_pdf_exam.py / parse_docx_exam.py / parse_doc_exam.py
- split_questions_v11.py / run_c1_c2_pipeline.py
- glm5_question_gen.py / glm4_flash_review.py (C3 双 LLM 模板)

雪薇端调用方式:
    export PYTHONPATH=/path/to/SPDT-004_EduContent/tools:$PYTHONPATH
    cd /path/to/SPDT-004_EduContent

    # CLI 统一入口
    python -m pt030_toolkit.cli parse-pdf <pdf>
    python -m pt030_toolkit.cli split <raw.json>
    python -m pt030_toolkit.cli pipeline <pdf>
    python -m pt030_toolkit.cli llm-gen <theme>
    python -m pt030_toolkit.cli llm-review <parent_problem.json>

    # 或直接调原 tools/ 脚本
    python tools/parse_pdf_exam.py <pdf>
    python tools/split_questions_v11.py <raw.json>

版本: v1.0 (2026-09-12)
作者: 宇兄窗口 (开发助手)
"""

__version__ = "1.0.0"
__author__ = "宇兄窗口 (宇兄端)"
