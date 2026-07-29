# SPDT-001 工作规划 v2.0

> 2026-07-17 | 鸿蒙特使 | 基于四份关键输入的综合规划

## 输入基础

| # | 文档 | 维度 | 关键贡献 |
|:---|:---|:---|:---|
| 1 | DevEco_CLI开发规范 | 开发效率 | devecocli全自动流水线，29→150 APP扩展能力 |
| 2 | 小龙虾设计评估 | 产品竞争力 | 三面板UI、四色视觉、DRD模板、Panic Button |
| 3 | 智能体APP设计指南 | 产品架构 | 5类Agent、4层架构、5大通用模块、统一数据协议 |
| 4 | OMAS本地能力赋能 | 平台资源 | Design SOP、CMC、SDC、MODLIB的匹配与调用 |

## 四条工作线

### 线A: 效率基建（本周）
- [ ] devecocli daily cron 更新为 DevEco 6.1 路径
- [ ] 创建 scripts/smoke-test.ps1（部署→冷启动→截图）
- [ ] 创建 docs/鸿蒙商店上架SOP.md
- [ ] 品牌手册更新（13→29 APP，加入智能体定位）

### 线B: 产品旗舰（本周）
- [ ] HarmonyCoder: 代码问答+审查引擎基础版
- [ ] ThinkKit-coach: 个性化学习Agent
- [ ] GaokaoAgent: 问答助手Agent
- [ ] Design SOP 生成三款Agent集群设计
- [ ] 三面板UI组件模板 → templates/base

### 线C: 批量扩展（下周）
- [ ] ThinkKit 教育系列 30 款骨架
- [ ] Craftsman 工具系列收尾 20 款
- [ ] 50 APP PREFLIGHT -ScanAll

### 线D: 运营上线（两周）
- [ ] 5-10 款旗舰提交鸿蒙应用商店
- [ ] CMC 批量生成商店描述
- [ ] 监控看板建立
- [ ] 用户数据反馈→下一轮MAC调研

## 关键里程碑

| 时间 | 里程碑 |
|:---|:---|
| 07-17 | CLI CI恢复 + 目录整理 |
| 07-18 | 3款旗舰 Agent 上线 + 品牌手册更新 |
| 07-21 | 上架SOP完成 |
| 07-23 | 50 APP PREFLIGHT |
| 07-28 | 5-10款旗舰提交商店审核 |
