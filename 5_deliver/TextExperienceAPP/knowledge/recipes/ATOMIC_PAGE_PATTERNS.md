# 原子页面模式 v1.0

> 所有鸿蒙 App 页面可分解为 ≤6 种原子模式
> 来源：5 个 App 开发验证

---

## 6 种原子模式

### List（列表页）
- **结构**: HNavBar + HSearchBar(可选) + List(ForEach+HCard) + HEmptyState + HFAB
- **适用**: 笔记列表、习惯列表、卡组列表、工具入口
- **验证 App**: thinkkit-zknote, rhythm-habit, thinkkit-flashcard, craftsman-utils

### Detail（详情页）
- **结构**: HNavBar(返回) + 内容区(图文/统计) + 操作按钮
- **适用**: 笔记详情、习惯统计、知识点详情
- **验证 App**: rhythm-habit (打卡统计)

### Form（表单页）
- **结构**: HNavBar + HFormItem(多个) + HButton(提交) + 校验
- **适用**: 新建笔记、编辑习惯、创建卡组
- **验证 App**: thinkkit-zknote (编辑模式)

### Dashboard（面板页）
- **结构**: HNavBar + KPI 卡片网格 + 图表区 + 列表区
- **适用**: 学习面板、数据概览、统计视图
- **验证 App**: gaokao-agent (Dashboard)

### Tool（工具页）
- **结构**: HNavBar(返回) + 输入区 + 处理按钮 + 输出区
- **适用**: JSON格式化、正则测试、单位换算
- **验证 App**: craftsman-utils (4 个工具页)

### Wizard（向导页）
- **结构**: HNavBar + 步骤进度条 + 分步内容 + 上一步/下一步
- **适用**: 注册流程、诊断测评、设置向导
- **验证 App**: gaokao-agent (冷启动诊断)

---

## 匹配规则

| 需求描述含... | → 原子模式 |
|-------------|----------|
| 列表/搜索/筛选/空状态 | List |
| 查看/详情/统计 | Detail |
| 新建/编辑/填写/输入 | Form |
| 概览/KPI/趋势/图表 | Dashboard |
| 输入→处理→输出/转换/计算 | Tool |
| 步骤/向导/测评/多页表单 | Wizard |

---

## 组合规则

复杂页面 = 原子模式组合：
- gaokao-agent 刷题页 = Tool (输入→判定) + Detail (AI反馈)
- gaokao-agent 诊断页 = Wizard (15步) → Dashboard (结果展示)
- craftsman-utils = List (工具网格) → Tool×4 (各工具页)
