# 知识图谱 v1.0 设计文档 (P0-B)

## 立项目标
为自适应学习提供"前驱/后继"基础 — 让学生按"已掌握 → 未掌握"路径推荐下一题，而非随机/题海。

## 范围
v1.0 范围：**数学 9 核心概念**（5 实体 + 4 虚拟）。

设计原则：
- **实体概念**: 已有 1+ 母题入库，立即可学习
- **虚拟概念**: 列出但标 `status: virtual`，等待母题补全后升级为 in_library
- **覆盖率**: 实体概念 5/5 (100%) 母题覆盖

## 数据模型
存储路径: `knowledge_graphs/<graph_id>.json`

### 节点 (Node)
```json
{
  "id": "concept_01",              // 内部唯一 ID
  "name": "线面平行",                // 人类可读名
  "chain_id": "math/M-V3-01-线面平行", // 与 4 步法母题 chain_id 对齐
  "difficulty": "中",                // 易/中/难
  "domain": "立体几何/位置关系",      // 学科子域
  "mother_problems": ["pp_001", "pp_006", "pp_007"],  // 关联母题
  "strategy_chains": ["math_strategy_vector", "math_strategy_graphing"],  // 关联策略链
  "coverage": "100%",                 // 母题覆盖度
  "status": "in_library",            // in_library | virtual
  "prerequisites": ["concept_07"],   // 前驱节点
  "successors": ["concept_02"],       // 后继节点
  "related": ["concept_03"]           // 相关节点（非依赖）
}
```

### 边 (Edge)
```json
{
  "from": "concept_07", "to": "concept_01", 
  "type": "prerequisite",     // prerequisite | related
  "weight": 1.0               // 0.0-1.0 边权重
}
```

### 学习路径 (Learning Path)
预定义完整学习路径，供自适应学习推荐使用：
```json
{
  "立体几何完整路径": ["concept_07", "concept_01", "concept_02", "concept_03", "concept_04", "concept_05"],
  "高考压轴路径": ["concept_07", "concept_02", "concept_03", "concept_05"]
}
```

## v1.0 数学 9 概念

| ID | 名称 | 难度 | 状态 | 母题 | 策略链 |
|:---|:---|:---|:---|:---|:---|
| concept_07 | 向量与建系 | 中 | virtual | 0 | vector |
| concept_01 | 线面平行 | 中 | in_library | pp_001/006/007 | vector+graphing |
| concept_02 | 线面垂直 | 中 | in_library | pp_002/008/009 | vector |
| concept_03 | 空间角 | 中 | in_library | pp_003/010/013 | vector+graphing |
| concept_04 | 空间距离 | 难 | in_library | pp_004/005/011 | vector+equation |
| concept_05 | 立体几何综合 | 难 | in_library | pp_012/014/015 | vector+graphing+equation |
| concept_06 | 函数与方程 | 中 | virtual | 0 | function_equation+graphing |
| concept_08 | 解析几何 | 难 | virtual | 0 | graphing+equation+parameter |
| concept_09 | 导数 | 难 | virtual | 0 | guihua+graphing |

## 边 (14 条)

### 前驱边 (10 条)
- concept_07 → concept_01/02/03/04 (向量是立体几何前驱)
- concept_01 → concept_02/05 (平行 → 垂直 → 综合)
- concept_02 → concept_03/05 (垂直 → 角度 → 综合)
- concept_03 → concept_05 (角度 → 综合)
- concept_04 → concept_05 (距离 → 综合)
- concept_06 → concept_09 (函数 → 导数)

### 相关边 (3 条, 非依赖)
- concept_01 ↔ concept_03/04 (平行与角度/距离相关)
- concept_07 → concept_08 (向量是解析几何工具)

## 验证
工具: `tools/kg_validator.py`

校验项 (6 类):
1. 必备字段: schema_version / graph_id / subject / nodes / edges
2. 节点 ID 唯一
3. 边引用节点存在
4. 母题引用存在 (按学科目录扫 pp_/hp_/ch_/en_/geo_/pol_/cal_)
5. 策略链引用存在 (接受 chain_id 或 card_id)
6. 前驱/后继引用节点存在

```bash
python tools/kg_validator.py knowledge_graphs/math_kg_v1.0.json
# [PASS] all checks ok
```

## 下一阶段 (P0-B 扩展)
- **P0-B.2**: 补 4 虚拟概念母题 (函数与方程 / 解析几何 / 导数 / 向量基础) — 9 张母题入库
- **P0-B.3**: 扩到 6 学科知识图谱 (语/英/史/地/政/书), 各 5-8 概念
- **P0-B.4**: rujing 学习中心 App 集成 knowledge_graph.json — 自适应学习路径推荐 UI

## 工具链
| 工具 | 用途 | 状态 |
|:---|:---|:---|
| `tools/kg_validator.py` (4 KB) | 校验 JSON schema + 引用完整性 | ✅ v1.0 |
| `knowledge_graphs/math_kg_v1.0.json` (6.8 KB) | 数学 9 概念图谱 | ✅ v1.0 |
| (待开发) `tools/kg_path_finder.py` | 给定起点概念 → 推荐学习路径 | P0-B.5 |
