# 雪薇终端后续任务清单 v1.0

> **版本**：v1.0 (2026-09-12)
> **拍板**：雪薇 9-12 拍板"知识挖掘/真题挖掘在雪薇端，功能探索在宇兄端"
> **配套**：v1.0 协作基线（commit 543c7d5）+ 雪薇机器状态（commit f955912）

---

## 一、分工原则（v1.0 拍板）

| 任务类型 | 主导方 | 说明 |
|---|---|---|
| **知识挖掘** | 雪薇端 | 6 学科真题、专题卡、三件套精写 |
| **真题挖掘** | 雪薇端 | 高考 6 学科真题（数学/历史/地理/政治/语文/外语）|
| **功能探索** | 宇兄端 | v3 UI 升级、Manim 动画、多媒体、RUJING 客户端 |
| **4 步法 v1.1 母题** | 雪薇主（PT-030 数学）| 宇兄续做函数/数列/解析几何，雪薇 review |

---

## 二、已完成（本会话 + 历次）

### 2.1 6 学科题库（闭环 4 学科）
- 数学 145 题 / 历史 1602 / 地理 2178 / 政治 1482 = **5407 题**

### 2.2 5 学科学习中心
- 数学 + 历史 + 地理 + 政治 + v3 集成
- tab-概念/影响/转折/易错/测验 + tab-方法论（数学/政治）

### 2.3 共同仓 SPDT-004_EduContent
- autoclaw_kit 21 文件（v1.0 规范 + 校验器 + 转换器）
- 4 文档（v1.0/v2.0/v3.0 + 状态 + ALL_CONTENT_INDEX）
- 3 README（PT-038 课程索引）
- 2 工具脚本（_stat_content.py + _add_display_target.py）
- **62 套历史卡 PASS 验证**

### 2.4 display_target 字段补全
- 1355 个 JSON 文件（雪薇端 → `["学习中心"]`）
- 内仓 `knowledge-cards-prod` commit `b89a0e9`
- 共同仓 `SPDT-004_EduContent` commit `03c5c04`

### 2.5 4 步法 v1.1 母题（宇兄端已推）
- 数学 51 张 + 历史 5 张 = **56 张 v1.1 PASS**
- 工具链 4 个 .py + 5 篇 handoff + Flask MVP
- 远端 commit `c480706`

---

## 三、本机后续任务清单（按优先级）

### 🔥 高优（本周）

#### A. 语文 zhenti/ 启动
- **目标**：上海语文高考真题 2018-2024
- **路径**：`projects/gaokao-chinese/zhenti/`
- **源**：D:\E_古诗文\三件套\ + 教育部考试中心
- **预计题量**：5 卷 × 30 题 = 150 题
- **方法**：参考政治 35 卷精修（1c3e05d 流程）

#### B. 外语 zhenti/ 启动
- **目标**：上海英语高考真题 2018-2024
- **路径**：`projects/gaokao-foreign/zhenti/`
- **源**：D:\F_英语\三件套\ + 教育部考试中心
- **预计题量**：5 卷 × 40 题 = 200 题
- **方法**：参考政治 35 卷精修

#### C. 6 学科 ZHENTI_INDEX 升级
- **当前**：`docs/ZHENTI_INDEX.md` v1.0 4 学科 + 6 学科框架
- **目标**：v1.1 含语文/外语进度
- **路径**：`docs/ZHENTI_INDEX.md`

### 🟡 中优（本月）

#### D. 4 步法数学 v1.1 学习中心集成
- **当前**：56 张卡在共同仓 `products/courses/数学/4step/`
- **目标**：在 `apps/learning-hub-v2/_reader/数学/` 加 tab-4step
- **配套**：4 步法数学 validator (mirror 自宇兄端)

#### E. 6 学科学习中心 v3 完整集成
- **当前**：5 学科（数学/历史/地理/政治/语文/外语）
- **目标**：每个学习中心 index.html 跑 v3 UIUX 5 律 + aesthetic_lint ≥ 80 分
- **配套**：v3 PROPOSAL.md 5 项必接能力

#### F. PT-030 数学 review（宇兄续做）
- **目标**：宇兄端 PR 30 母题（函数/数列/解析几何），雪薇 24h review
- **配套**：v1.1 规范文档 + display_target 字段

### 🟢 低优（下季度）

#### G. 历史方法论卡 5 张
- **目标**：5 张方法论（按数学 6 板块 × 5 方法模式）
- **路径**：`projects/gaokao-history/methods/`
- **方法**：参考数学 methods/ (commit eee6e49)

#### H. 地理方法论卡 5 张
- **路径**：`projects/gaokao-geography/methods/`

#### I. 古史 v1-v4 + 墨骨山河 ep09 续作 review
- **当前**：宇兄端主 PT-031（4 卷 + ep09 + 配置包已 mirror）
- **目标**：续作 ep04+ + ep10+，雪薇 review

---

## 四、待启动后台 task 计划

### task-1: 语文 zhenti 抓取
- 抓上海语文 2018-2024 真题
- 输出 papers/*.json + sources/*.txt + bank_summary.json
- 入仓 `projects/gaokao-chinese/zhenti/`
- 跟政治/地理/历史 4 学科统一结构

### task-2: 外语 zhenti 抓取
- 抓上海英语 2018-2024 真题
- 输出同上
- 入仓 `projects/gaokao-foreign/zhenti/`

### task-3: 4 步法 v1.1 学习中心渲染
- 读宇兄端 products/courses/数学/4step/ 数据
- 渲染到 `apps/learning-hub-v2/_reader/数学/`
- 加 tab-4step
- 配套 spec.yaml

### task-4: 6 学科 ZHENTI_INDEX v1.1
- 写 `docs/ZHENTI_INDEX.md` v1.1
- 加语文/外语进度
- 6 学科统一索引

### task-5: 跨仓 PR review 流程
- 配 GitHub Actions CI
- 跑 `tools/_stat_content.py` 每周
- 24h review 通知

---

## 五、本机任务执行顺序

```
本周（高优）：
  task-1 语文 zhenti 抓取（→ commit 入仓）
  task-2 外语 zhenti 抓取（→ commit 入仓）
  task-4 ZHENTI_INDEX v1.1 更新（→ commit 入仓）

本月（中优）：
  task-3 4 步法 v1.1 学习中心渲染
  task-5 跨仓 PR review 流程

下季度（低优）：
  G/H 历史/地理方法论卡
  I 古史/墨骨山河续作 review
```

---

## 六、跨机协作预期（基于 v1.0 协作基线）

### 6.1 雪薇端 → 共同仓
- task-1/2/3/4 完成后 → commit 到共同仓
- 宇兄端 24h review → 合并

### 6.2 宇兄端 → 共同仓
- 宇兄端 PT-030 函数/数列/解析几何 30 母题 PR
- 雪薇端 24h review
- 配套 v1.1 规范校验

### 6.3 雪薇端 → 学习中心
- 6 学科学习中心 + v3 集成 100%
- display_target 字段应用

---

## 七、变更记录

| 日期 | 版本 | 变更 | 拍板 |
|---|---|---|---|
| 2026-09-12 | v1.0 | 初版（4 学科闭环 + 6 学科框架 + 14 个 todo）| 雪薇（v1.0 协作基线后） |
