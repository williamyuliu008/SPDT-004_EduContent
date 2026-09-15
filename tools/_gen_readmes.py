"""M-2: 给 SPDT-004 核心子目录批量加轻量 README.md"""
from pathlib import Path

ROOT = Path(r"D:\2_products\education\SPDT-004_EduContent")

# 10 个核心子目录的元数据
DIRECTORIES = [
    {
        "dir": "tools",
        "title": "工具集",
        "owner": "宇兄端",
        "status": "活跃 (12+ 脚本)",
        "phase": "P0-CGM 全线 + PT-030 解析器",
        "purpose": "双窗口共用工具脚本 (LLM batch gen / validator / path_finder / 解析器)。",
        "contents": [
            "`strategy_*.py` 策略卡工具 (3 个)",
            "`mother_problem_*.py` 母题工具 (3 个)",
            "`meta_*.py` 元学习工具 (2 个)",
            "`kg_*.py` 知识图谱工具 (2 个)",
            "`glm*.py` GLM-4-flash 工具 (3 个)",
            "`parse_*.py` PT-030 解析器 (3 个: PDF/docx/doc)",
        ],
        "contract": "宇兄维护，雪薇可调用，需修时走 handoff/。",
        "links": "见 PROJECT.md § 4 双窗口协作",
    },
    {
        "dir": "products/math_4step_mvp",
        "title": "rujing Flask Web demo",
        "owner": "宇兄端",
        "status": "跑通 (127.0.0.1:5050)",
        "phase": "P0-D / P-CGM.5 集成完成",
        "purpose": "rujing 学习中心 Web 演示，10 路由覆盖母题/策略/概念/元学习/视频/音频。",
        "contents": [
            "`app.py` Flask 应用 (10 路由)",
            "`templates/` 5 个 HTML (index/browse/learn/verify/kg)",
            "`static/` CSS/JS",
        ],
        "contract": "宇兄维护，是 P1 雪薇端验收 demo。",
        "links": "启动: `python app.py` → http://127.0.0.1:5050",
    },
    {
        "dir": "knowledge_graphs",
        "title": "知识图谱 JSON 资产",
        "owner": "宇兄端",
        "status": "活跃 (2 kg 文件, 39 概念, 34 边)",
        "phase": "P0-B 全线 + P-CGM.5 视频挂载",
        "purpose": "学科知识图谱 JSON 资产，含 math_kg_v1.2 (9 概念) + multi_subject_kg_v1.0 (30 概念)。",
        "contents": [
            "`math_kg_v1.2.json` (9 概念, 14 边)",
            "`multi_subject_kg_v1.0.json` (30 概念, 20 边, 53 视频链接)",
        ],
        "contract": "宇兄维护，git tracked。",
        "links": "validator: `tools/kg_validator.py`",
    },
    {
        "dir": "handoff",
        "title": "双窗口协作契约",
        "owner": "宇兄 + 雪薇",
        "status": "活跃 (5+ 篇文档)",
        "phase": "P0-P1 全线",
        "purpose": "宇兄→雪薇/手机端/消费者 A 的协作文档契约。",
        "contents": [
            "`SPDT004_DUAL_WINDOW_COLLABORATION_v1.0/v1.1` 双窗口 v1.0/v1.1",
            "`P1_rujing_雪薇端验收清单_v1.0.md`",
            "`P1_PT-030_数据规范_v1.0.md`",
            "`PT-030_工具链_v1.0_完整onboarding.md`",
        ],
        "contract": "双窗口唯一接口，工具变更必走此目录。",
        "links": "见 OWNERS.md § 5 双窗口交接契约",
    },
    {
        "dir": "docs",
        "title": "设计文档",
        "owner": "宇兄端",
        "status": "活跃 (10+ 篇)",
        "phase": "P0-CGM 全部",
        "purpose": "路线设计文档 + 工具/规范文档。",
        "contents": [
            "`02-设计文档/` 设计规范 (策略卡 v1.0 / 知识图谱 v1.0/v1.2/v2.0 / 5 学科母题 / 元学习 chain_id 修复)",
            "`04-Skills/` 雪薇端 Skills 文档",
        ],
        "contract": "宇兄维护，雪薇可读。",
        "links": "见 PROJECT.md § 6 阶段路线表",
    },
    {
        "dir": "prompts",
        "title": "LLM 提示词",
        "owner": "宇兄端",
        "status": "活跃",
        "phase": "P0 全线",
        "purpose": "母题/策略/元学习 LLM 生成提示词模板。",
        "contents": ["GLM-4-flash batch gen 提示词"],
        "contract": "宇兄维护，工具调用。",
        "links": "见 tools/mother_problem_batch_gen.py 等",
    },
    {
        "dir": "quality",
        "title": "质检工具",
        "owner": "宇兄端",
        "status": "活跃",
        "phase": "P0 全线",
        "purpose": "validator / auditor / 准确度统计工具。",
        "contents": ["策略/母题/元学习 validator"],
        "contract": "宇兄维护，雪薇可调用。",
        "links": "见 tools/kg_validator.py",
    },
    {
        "dir": "templates",
        "title": "模板",
        "owner": "宇兄端",
        "status": "活跃",
        "phase": "P0 全线",
        "purpose": "HTML / PDF / DOCX 模板。",
        "contents": ["Flask 模板 + 文档模板"],
        "contract": "宇兄维护。",
        "links": "见 products/math_4step_mvp/templates/",
    },
    {
        "dir": "1_ingest",
        "title": "原始素材采集",
        "owner": "雪薇端",
        "status": "活跃 (PT-030 数据)",
        "phase": "P1 PT-030 入库",
        "purpose": "PT-030 真题 PDF/docx/doc 原始素材。",
        "contents": ["5 学科真题 (5407 题)"],
        "contract": "雪薇端主导，宇兄提供解析工具。",
        "links": "见 handoff/P1_PT-030_数据规范_v1.0.md",
    },
    {
        "dir": "3_render",
        "title": "CGM 多媒体渲染管线",
        "owner": "宇兄端",
        "status": "活跃 (P-001 历史视频管线)",
        "phase": "P-CGM.1~3.5",
        "purpose": "manim + edge-tts + ffmpeg 多媒体渲染。CGM 融合方法论的物理落地。",
        "contents": [
            "`P-001_video/` 历史视频生成器 (5 脚本)",
            "`media/batch/w28/` 10 集 v3+v4 视频 (PASS 100%)",
        ],
        "contract": "宇兄维护。视频产物在 D:\4_data\work\media\。",
        "links": "见 docs/02-设计文档/knowledge_graph_v2.0_设计.md",
    },
]


TEMPLATE = """# {title}

> **Owner**: {owner} | **Status**: {status} | **Phase**: {phase}

## 作用
{purpose}

## 主要内容
{contents_list}

## 协作契约
{contract}

## 相关
{links}
"""


def gen_readme(meta: dict) -> str:
    contents_list = "\n".join(f"- {c}" for c in meta["contents"])
    return TEMPLATE.format(
        title=meta["title"],
        owner=meta["owner"],
        status=meta["status"],
        phase=meta["phase"],
        purpose=meta["purpose"],
        contents_list=contents_list,
        contract=meta["contract"],
        links=meta["links"],
    )


for meta in DIRECTORIES:
    target = ROOT / meta["dir"] / "README.md"
    target.write_text(gen_readme(meta), encoding="utf-8")
    print(f"  WROTE: {target.relative_to(ROOT)}")

print(f"\n完成 {len(DIRECTORIES)} 个子目录 README")