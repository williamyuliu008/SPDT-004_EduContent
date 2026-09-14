# 知识图谱 v2.0 设计文档 (P0-B.4)

## 立项目标
P0-B.3 完成图谱数据层（multi_subject_kg_v1.0 + math_kg_v1.2），P0-B.4 推**应用层**：path_finder 工具 + rujing App 集成，让图谱从静态文档升级为自适应学习驱动力。

## 范围

### 1. 工具层 — kg_path_finder.py (7 KB)
基于 knowledge_graphs/<graph_id>.json 提供 4 命令：

| 命令 | 功能 | 输入 | 输出 |
|:---|:---|:---|:---|
| `list` | 列出所有概念 | --graph | 节点/边统计 |
| `recommend` | 推荐下一步 | --graph --known --top | 满足 prereqs 的 Top-N 概念 |
| `path` | 找最短路径 | --graph --from --to | BFS 最短路径 |
| `journey` | 完整学习路径 | --graph --known | 拓扑排序所有未掌握概念 |

### 算法
- **recommend**: 候选 = in_library 概念中 prereqs 已掌握的；score = prereq 边权重均值
- **path**: BFS 找最短路径
- **journey**: Kahn's 拓扑排序（无前驱 → 后继），保证 prereqs 在前

### 2. 应用层 — math_4step_mvp Flask 集成

新增 3 路由：

| 路由 | 方法 | 功能 |
|:---|:---|:---|
| `/kg` | GET | 知识图谱列表（所有 kg JSON 摘要） |
| `/kg/<graph_id>` | GET | 图谱详情（节点 + 边表格 + path_finder UI） |
| `/api/path_finder` | GET | 包装 kg_path_finder.py subprocess 调用 |

新增 2 模板：
- `templates/kg_list.html` — 图谱卡片网格
- `templates/kg_view.html` — 节点表格 + 边表格 + path_finder 交互（输入 known IDs → 实时推荐）

### 3. 启动方式
```bash
cd products/math_4step_mvp
python app.py
# 访问 http://127.0.0.1:5050/kg
```

## 工具链

| 工具 | 用途 | 规模 |
|:---|:---|:---|
| `tools/kg_validator.py` (5 KB) | 校验 JSON schema + 引用完整性 | 多学科支持 |
| `tools/kg_path_finder.py` (7 KB) | 推荐学习路径 | 4 命令 |
| `knowledge_graphs/math_kg_v1.2.json` (7.5 KB) | 数学 9 概念 | ✅ |
| `knowledge_graphs/multi_subject_kg_v1.0.json` (16.5 KB) | 6 学科 30 概念 | ✅ |
| `products/math_4step_mvp/app.py` (8.5 KB → 11 KB) | Flask + kg 路由 | 9 路由 |
| `products/math_4step_mvp/templates/kg_*.html` (4.5 KB) | UI 模板 | 2 文件 |

## 测试结果

| 路由 | Status | Content Length |
|:---|:---|:---|
| `/kg` | 200 | ~700 字节 |
| `/kg/multi_subject_kg_v1.0` | 200 | ~3 KB |
| `/api/path_finder?recommend&known=concept_C1,concept_C2` | 200 | 推荐 concept_C5 |

## 下一阶段 (P0-C / P0-D)

- **P0-C 元学习扩展**: 8 → 20 张 (主动回忆/睡眠/错题本等)
- **P0-D rujing 学习中心 App 集成 v1.0**: 母题详情页加 "适用策略" + "适用概念" tab
- **P0-E 学生端 (雪薇端) 验收**: 学生用图谱推荐路径自主学习