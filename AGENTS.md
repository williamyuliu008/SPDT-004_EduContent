# AGENTS.md — SPDT-004_EduContent

## Data Path
- raw:    `D:\4_data\raw\education\` + `D:\4_data\raw\media\`
- work:   `D:\4_data\work\education\edu_content\` + `D:\4_data\work\media\`
- output: `D:\4_data\output\deliverables\edu_content\` + `D:\4_data\output\content\`

数据迁移记录:
- `3_render/`    → `D:\4_data\work\media\renders\`
- `shared/`      → `D:\4_data\raw\media\assets\`
- `5_deliver/`   → `D:\4_data\output\deliverables\edu_content\`
- `products/`    → `D:\4_data\output\deliverables\edu_content\products\`

数据治理规范: [D:\4_data\DATA_GOVERNANCE_SPEC.md](D:\4_data\DATA_GOVERNANCE_SPEC.md)

---

## 关键决策 (本项目稳定结论)

### 学生画像 (本项目核心约束)
- **地理位置**: 上海
- **方向**: 文科 / 艺术类
- **高考考试范围**: 语数外 + 史地政 + 书法 (国美校招)
- **明确排除**: 物理、化学、生物 (3 科完全不涉及)
- **学段**: 高中 (上海卷优先, 全国卷参考)
- **影响**:
  - 解题策略库: 只覆盖 6 主科 (语数英史地政) + 1 艺术科 (书法)
  - 母题/真题: 排除物理化学生物
  - 学习路径: 上海高考时间表 + 国美校招时间表
  - 跨学科: 文综 (史地政) 关联, 语数英 vs 艺术生平衡

### 双窗口分工
- **宇兄端 (开发助手)**: 工具/算法/RUJING/7 PDT/Manim/验证
- **雪薇端 (学生助手)**: 知识/真题挖掘/6 学科学习中心
- 共同仓: github.com/williamyuliu008/SPDT-004_EduContent
- 分支: master (双端共用, pull + push 无 rebase)
- 真题挖掘和处理 (PT-030): 雪薇端主导, 宇兄端做工具 + 验证 + 高难度组件

### 当前 P0 路线 (本轮 2026-09-13 拍板)
- **P0-A 主线**: 解题策略库 v1.0 (6 学科方法论, ~42-56 张) — 宇兄端做
- **P0-C 辅线**: 元学习/考试策略 v1.0 (~20-30 张) — 宇兄端做
- **不做** (转交/暂缓): 真题挖掘/处理 (雪薇端) / 物理化学生物 (排除) / 错题本/学情分析 (需用户行为数据)

