import sqlite3, json
from datetime import datetime, timezone

DB_PATH = r"D:\92_products\SPDT-001_Harmony\_03_knowledge\mmc_archive.db"
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# Brands
brands = [
    ("ThinkKit", "#5B8C5A", "学术学习与知识管理生态", 5),
    ("Craftsman", "#F18F01", "极客开发者效率工具", 2),
    ("HarmonyCoder", "#7B2D8E", "AI驱动编程助手", 1),
    ("GaokaoAgent", "#2563eb", "高考AI辅导教育", 1),
    ("Rhythm", "#4A90D9", "生活健康习惯养成", 1),
]
for b in brands:
    c.execute("INSERT INTO brands (brand_name, primary_color, positioning, app_count, created_at) VALUES (?,?,?,?,?)", b + (now,))

# Apps
apps = [
    {"app_name":"thinkkit-coach","brand":"ThinkKit","short_desc":"Agent驱动的高考数学个性化学习系统","features":"dashboard,plan,knowledge_panorama,flashcard_gen,templates","pages":4,"has_canvas":0,"has_http":0,"has_router":0,"primary_color":"#5B8C5A"},
    {"app_name":"thinkkit-flashcard","brand":"ThinkKit","short_desc":"简约双向闪卡记忆工具","features":"flashcard_review,sm2_algorithm,card_groups","pages":1,"has_canvas":0,"has_http":0,"has_router":0,"primary_color":"#5B8C5A"},
    {"app_name":"thinkkit-mindmap","brand":"ThinkKit","short_desc":"灵活高效的思维导图工具","features":"mindmap_tree,zoom_pan,color_marking,export_outline","pages":1,"has_canvas":1,"has_http":0,"has_router":0,"primary_color":"#6B5CE7"},
    {"app_name":"thinkkit-reader","brand":"ThinkKit","short_desc":"深度阅读与摘录批注","features":"book_import,reader,annotations,themes,storage","pages":3,"has_canvas":0,"has_http":0,"has_router":1,"primary_color":"#5B8C5A"},
    {"app_name":"thinkkit-zknote","brand":"ThinkKit","short_desc":"极简大纲笔记·本地优先","features":"outline_notes,hierarchy,collapse,inline_edit","pages":1,"has_canvas":0,"has_http":0,"has_router":0,"primary_color":"#5B8C5A"},
    {"app_name":"craftsman-arkui","brand":"Craftsman","short_desc":"ArkUI组件开发模板与参考工程","features":"stage_model_template,common_ready,build_config","pages":1,"has_canvas":0,"has_http":0,"has_router":0,"primary_color":"#F18F01"},
    {"app_name":"craftsman-ohpm","brand":"Craftsman","short_desc":"鸿蒙三方库发现与推荐工程","features":"ohpm_index,tag_filter,library_cards","pages":1,"has_canvas":0,"has_http":0,"has_router":0,"primary_color":"#F18F01"},
    {"app_name":"harmonycoder","brand":"HarmonyCoder","short_desc":"说需求即出代码 — AI编程伙伴","features":"code_gen,demo_scenarios,deveco_export,ohpm_recommend,project_guide","pages":5,"has_canvas":0,"has_http":0,"has_router":1,"primary_color":"#7B2D8E"},
    {"app_name":"gaokao-agent","brand":"GaokaoAgent","short_desc":"六科统一的高考AI辅导Agent","features":"diagnostic,tutoring,knowledge_map,dashboard,subject_switch","pages":5,"has_canvas":1,"has_http":1,"has_router":0,"primary_color":"#2563eb"},
    {"app_name":"rhythm-habit","brand":"Rhythm","short_desc":"极简习惯追踪与打卡","features":"habit_tracking,daily_checkin,streak,weekly_progress","pages":1,"has_canvas":0,"has_http":0,"has_router":0,"primary_color":"#4A90D9"},
]

for app in apps:
    c.execute(
        "INSERT INTO events (event_type, app_name, brand, version, created_at, metadata_json, source_dir, tags) VALUES (?,?,?,?,?,?,?,?)",
        ("harmony_app_created", app["app_name"], app["brand"], "V1.0", now,
         json.dumps(app, ensure_ascii=False),
         f"D:\\92_products\\SPDT-001_Harmony\\apps\\{app['app_name']}\\",
         app["features"])
    )

# Dependency graph
edges = [
    ("ThinkKit","ThinkKit","EVOLVES","ThinkKit品牌内APP共享common内核和品牌色"),
    ("Craftsman","Craftsman","EVOLVES","Craftsman品牌内工具APP共享Stage模型模板"),
    ("ThinkKit.zknote","ThinkKit.flashcard","UPGRADES","大纲速记→闪卡复习（从笔记到记忆）"),
    ("ThinkKit.coach","ThinkKit.flashcard","UPGRADES","学习教练内置闪卡生成，驱动闪卡升级"),
    ("ThinkKit.reader","ThinkKit.zknote","UPGRADES","阅读批注→大纲笔记（从阅读到笔记）"),
    ("craftsman-arkui","craftsman-ohpm","UPGRADES","组件模板→OHPM库推荐"),
    ("harmonycoder","craftsman-arkui","UPGRADES","AI代码生成→组件模板"),
    ("gaokao-agent","thinkkit-coach","UPGRADES","高考助手→学习教练（从六科到数学深度）"),
    ("common_kernel_v2","ThinkKit","FOUNDATION","Common Kernel v2是所有ThinkKit APP的底座"),
    ("common_kernel_v2","Craftsman","FOUNDATION","Common Kernel v2是所有Craftsman APP的底座"),
    ("common_kernel_v2","HarmonyCoder","FOUNDATION","Common Kernel v2支持HarmonyCoder"),
    ("common_kernel_v2","GaokaoAgent","FOUNDATION","Common Kernel v2为高考助手提供全组件覆盖"),
    ("common_kernel_v2","Rhythm","FOUNDATION","Common Kernel v2为律动习惯提供组件"),
]
for src, tgt, rel, desc in edges:
    c.execute("INSERT INTO depgraph (source, target, relation, description, created_at) VALUES (?,?,?,?,?)", (src, tgt, rel, desc, now))

conn.commit()

# Verify
c.execute("SELECT COUNT(*) FROM events"); print(f"Events: {c.fetchone()[0]}")
c.execute("SELECT COUNT(*) FROM depgraph"); print(f"DepGraph: {c.fetchone()[0]}")
c.execute("SELECT COUNT(*) FROM brands"); print(f"Brands: {c.fetchone()[0]}")
c.execute("SELECT app_name,brand FROM events ORDER BY brand,app_name")
print("\n--- Archived Apps ---")
for row in c.fetchall(): print(f"  [{row[1]}] {row[0]}")
conn.close()
print(f"\nDB: {DB_PATH}")
