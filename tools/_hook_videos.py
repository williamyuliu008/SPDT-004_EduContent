"""P-CGM.5: 给 multi_subject_kg_v1.0 历史 5 概念挂视频链接"""
import json
from pathlib import Path

kg_path = Path(r"D:\2_products\education\SPDT-004_EduContent\knowledge_graphs\multi_subject_kg_v1.0.json")
g = json.loads(kg_path.read_text(encoding="utf-8"))

VIDEO_MAP = {
    "concept_H1": [  # 史料实证
        {"title": "史料实证 · 史前史", "filename": "hp_001_史料实证判断_史前史.mp4", "mother_problem": "hp_001"},
        {"title": "史料解读 · 演讲结构", "filename": "hp_004_史料解读_演讲结构.mp4", "mother_problem": "hp_004"},
    ],
    "concept_H2": [  # 时间轴定位
        {"title": "时间轴定位 · 公元前后", "filename": "hp_002_时间轴定位_公元前后.mp4", "mother_problem": "hp_002"},
        {"title": "经济全球化 · 阶段时间轴", "filename": "hp_005_经济全球化_阶段时间轴.mp4", "mother_problem": "hp_005"},
    ],
    "concept_H3": [  # 工业革命与现代化
        {"title": "工业革命 · 19世纪末德国", "filename": "hp_003_工业革命与现代化_19世纪末德国.mp4", "mother_problem": "hp_003"},
        {"title": "苏联解体 · 1991", "filename": "hp_006_苏联解体_1991.mp4", "mother_problem": "hp_006"},
        {"title": "9·11 与反恐战争", "filename": "hp_007_9_11_反恐战争.mp4", "mother_problem": "hp_007"},
    ],
    "concept_H4": [  # 史料解读
        {"title": "史料解读 · 演讲结构", "filename": "hp_004_史料解读_演讲结构.mp4", "mother_problem": "hp_004"},
        {"title": "全球金融危机 · 2008", "filename": "hp_008_全球金融危机_2008.mp4", "mother_problem": "hp_008"},
    ],
    "concept_H5": [  # 经济全球化
        {"title": "经济全球化 · 阶段时间轴", "filename": "hp_005_经济全球化_阶段时间轴.mp4", "mother_problem": "hp_005"},
        {"title": "全球金融危机 · 2008", "filename": "hp_008_全球金融危机_2008.mp4", "mother_problem": "hp_008"},
        {"title": "新冠疫情 · 2020", "filename": "hp_012_新冠疫情_2020.mp4", "mother_problem": "hp_012"},
        {"title": "AI 革命 · 2023", "filename": "hp_014_AI革命_2023.mp4", "mother_problem": "hp_014"},
    ],
}

for n in g["nodes"]:
    if n["id"] in VIDEO_MAP:
        n["video_links"] = VIDEO_MAP[n["id"]]

kg_path.write_text(json.dumps(g, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"挂载视频完成. 概念数: {sum(1 for n in g['nodes'] if n.get('video_links'))}")
for n in g["nodes"]:
    if n.get("video_links"):
        print(f"  {n['id']} ({n['name']}): {len(n['video_links'])} 个视频")