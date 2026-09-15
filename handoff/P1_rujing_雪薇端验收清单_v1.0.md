# P1 雪薇端验收清单 (rujing demo) v1.0

## 目的
让雪薇端走一遍 rujing demo, 验收 P0 全线交付 (P0-A 策略库 + P0-B 知识图谱 + P0-C 元学习 + P0-D /learn 集成).

## 启动方式

```bash
cd D:\2_products\education\SPDT-004_EduContent\products\math_4step_mvp
python app.py
# 访问 http://127.0.0.1:5050
```

## 验收路由 (10 路由)

| # | 路由 | 验收项 | 期望 |
|:---|:---|:---|:---|
| 1 | `/` | 首页 | 显示 4 卡片网格 (浏览/训练/验收/kg) |
| 2 | `/browse` | 浏览模式 | 显示 3 库卡片 (concepts/parent_problems/variants) |
| 3 | `/browse?chain=math/M-V3-01-线面平行` | 链过滤 | 只显示线面平行相关卡片 |
| 4 | `/learn/pp_001` | 数学母题学习 | 4 点联动: 母题 + 变形 + 适用策略 (math_007) + 适用概念 (kg) + 元学习 (5 张) |
| 5 | `/learn/ch_001` | 语文母题学习 | 4 点联动: 母题 + 适用策略 (ch_strategy) + 适用概念 (语文 5 概念) + 元学习 |
| 6 | `/learn/hp_001` | 历史母题学习 | 4 点联动 |
| 7 | `/verify?id=concept_xxx` | 验收模式 | 填空验证 |
| 8 | `/kg` | 知识图谱列表 | 3 个图谱 (math_v1.0/1.1/1.2 + multi_subject_v1.0) |
| 9 | `/kg/multi_subject_kg_v1.0` | 6 学科图谱详情 | 30 概念 + 20 边表格 + path_finder UI |
| 10 | `/api/path_finder?recommend&known=concept_C1,concept_C2` | path_finder API | 返回推荐 concept_C5 + 5.0 score |

## 关键验收标准

### A. 数据完整性
- [ ] 6 学科图谱 30 概念 (语文 6 + 英语 5 + 历史 5 + 地理 5 + 政治 5 + 书法 5)
- [ ] 数学图谱 9 概念 (100% in_library)
- [ ] 60+ 张母题跨 7 学科
- [ ] 20 张元学习 (覆盖记忆术/认知科学/应试/心理/时间管理 5 类)

### B. 联动正确性
- [ ] /learn/<pp_id> 显示该母题关联策略卡 (applicable_strategies)
- [ ] /learn/<pp_id> 显示该母题关联概念节点 (跨 kg 查找)
- [ ] /learn/<pp_id> 推荐 ≥3 张元学习卡 (含通用 5 张兜底)

### C. path_finder 闭环
- [ ] `/api/path_finder?recommend&known=concept_C1,concept_C2` 推荐 concept_C5 (语言基础)
- [ ] `/api/path_finder?journey&known=concept_C1` 推荐 28 步学习路径
- [ ] `/api/path_finder?path&from=concept_C1&to=concept_C5` 返回最短路径

## 反馈点

| 类型 | 例子 | 处理 |
|:---|:---|:---|
| 母题内容错误 | pp_018 method_tag 错 | 雪薇端手动改 JSON |
| 知识图谱节点缺失 | 5 学科某节点无母题 | 雪薇端用 `mother_problem_batch_gen.py` 补 |
| 元学习 chain_id 不规范 | 通用模板 | 雪薇端用 `_fix_meta_chain.py` 修 |
| /learn 路由慢 (>3s) | 跨学科扫所有 kg | 宇兄端加缓存 |
| path_finder 推荐不准 | score 不合理 | 宇兄端调权重 |

## 时间预算
- 单次验收：~30 分钟 (10 路由 + 数据完整性)
- 反馈循环：~1-2 小时（写入 issues）
- 端到端闭环：~1 工作日

## 启动 checklist
1. [ ] 启动 Flask: `python app.py` (端口 5050)
2. [ ] 访问 http://127.0.0.1:5050 看首页
3. [ ] 按顺序验收 10 路由
4. [ ] 记录任何数据缺失/错误到 `review_inbox/P1_验收反馈_雪薇端_YYYY-MM-DD.md`
5. [ ] 反馈给宇兄端 (`#issues` 或 handoff 文档)

## 下一步
P1 验收完成 → P2 启动 (PT-030 真题入库 + 5 学科扩题)