# 元学习 chain_id 修复记录 (P0-C.5)

## 立项目标
P0-C 生成 12 张元学习时 (meta_009-020), LLM 在 6 张 chain_id 偷懒写为 `meta_learning_general`. 修复为具体名, 让 path_finder / 跨链引用可用.

## 修复清单 (6 张)

| 文件 | 旧 chain_id | 新 chain_id |
|:---|:---|:---|
| meta_009.json (主动回忆) | meta_learning_general | meta_learning_active_recall |
| meta_012.json (错题本) | meta_learning_general | meta_learning_error_book |
| meta_013.json (刻意练习) | meta_learning_general | meta_learning_deliberate_practice |
| meta_016.json (元认知监控) | meta_learning_general | meta_learning_metacognition |
| meta_018.json (学习迁移) | meta_learning_general | meta_learning_transfer |
| meta_020.json (成长型思维) | meta_learning_general | meta_learning_growth_mindset |

## 工具
- `tools/_fix_meta_chain.py` (1.2 KB) — 批量修 JSON 字段
- 跨平台 UTF-8 安全 (Python pathlib + json)

## 修复后状态

| 指标 | 修前 | 修后 |
|:---|:---|:---|
| 总卡数 | 20 | 20 |
| 唯一 chain_id | 14 (含 7 张 general 重复) | **20 (每张独立)** |
| general 占位 | 7 张 | 0 张 |

## 数据位置
**注意**: 元学习 JSON 文件 (`D:\4_data\knowledge_cards\元学习\meta_*.json`) 不在 SPDT-004 git 仓库内 (内容/管线分离). 此修复在磁盘生效, 但 git 只记录工具脚本 + 本说明.

## 下一步
- P0-D: rujing /learn/<pp_id> 页加 "适用策略" + "适用概念" tab
- en_010 七选五段落匹配 (低优先)