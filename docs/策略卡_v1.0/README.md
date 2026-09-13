# 解题策略卡 v1.0 (Strategy Card v1.0)

**项目**: SPDT-004 教育内容 / 知识挖掘
**版本**: v1.0 (2026-09-13)
**作者**: 宇兄窗口 (开发助手)
**完整规范**: `handoff/SPDT004_STRATEGY_CARD_v1.0_规范.md`
**验证器**: `tools/strategy_card_validator.py`

---

## 一、是什么

**解题策略卡** = 学科方法论卡片 (跨学科的"母题级方法论")
- 颗粒度: 方法论级 (1 策略覆盖 N 道题), 上层于 4 步法母题
- 学科覆盖: 6 主科 (语数英史地政) + 1 艺术科 (书法) = 7 学科
- 数量: 计划 42-56 张策略 + 20-30 张元学习 = 70+ 张

## 二、目录

```
docs/策略卡_v1.0/
├── README.md                  ← 本文件
├── 示例/
│   ├── strategy_math_001.json       数形结合
│   ├── strategy_chinese_001.json    古诗意象-意境-情感
│   ├── strategy_english_001.json    阅读理解 4 步法
│   ├── strategy_history_001.json    因果分析 4 角度
│   ├── strategy_geo_001.json        等值线判读 5 步
│   ├── strategy_politics_001.json   主体分析法
│   ├── strategy_calligraphy_001.json 五体辨识
│   ├── meta_001.json                艾宾浩斯间隔重复
│   ├── meta_002.json                番茄钟
│   └── meta_003.json                高考时间分配
```

## 三、16 字段结构

### 5 核心字段 (两窗口禁区)
- `card_id` 唯一 ID
- `chain_id` 策略族
- `schema_version` "v1.0"
- `SOP` 标准操作 (5 步内)
- `验收标准` 自检标准

### 11 扩展字段 (宇兄端可加)
- `source_type` "教学法" / "学科方法论" / "元学习" / ...
- `source_ref` 出处
- `original_problem_id` 关联母题
- `problem_statement` 典型例题
- `given_conditions` 适用条件
- `figure_description` / `figure_ref` / `figure_type` 配图
- `intuition` 直觉理解
- `thinking_path` 思维路径
- `key_insight` 核心洞察

### display_target v3.0 (必填)
- 通用: `["RUJING", "学习中心"]`

## 四、用法

### 4.1 验证单张/多张卡

```bash
# 单张
python tools/strategy_card_validator.py /path/to/strategy_math_001.json

# 批量
python tools/strategy_card_validator.py --dir D:/4_data/knowledge_cards/策略
python tools/strategy_card_validator.py --dir D:/4_data/knowledge_cards/元学习
```

期望输出: `[PASS] xxx.json: 0 条 (E=0, W=0)` 零错误零警告

### 4.2 雪薇端批量生产

```bash
# 1. 拉规范
git pull origin master

# 2. 复制示例到本地
cp -r docs/策略卡_v1.0/示例 D:/4_data/knowledge_cards/策略/新批次/

# 3. 基于示例 + LLM 协助, 写新卡 (如 strategy_math_002)
# 模板: strategy_<subject>_<3位编号>.json

# 4. 验证
python tools/strategy_card_validator.py --dir D:/4_data/knowledge_cards/策略
```

## 五、跟 4 步法 v1.0 母题的关系

```
策略卡 (方法论层)          ← 1 张覆盖 5-10 道题
  ↓ 引用
4 步法母题 (单题层)        ← 1 张 = 1 道题
  ↓ 引用
真题 (高考原题)            ← 由 C1/C2 工具链解析
```

互引字段:
- 策略卡 → 母题: `original_problem_id` (例: "pp_001, pp_006")
- 母题 → 策略: 头部加 `适用策略: math_strategy_graphing` (待 v1.1 实施)

## 六、本项目学生范围 (重要!)

- **学生**: 上海 文科/艺术生
- **高考范围**: 语数外 + 史地政 + 书法 (国美校招)
- **明确排除**: 物理、化学、生物 (3 科不做)
- 策略卡 7 学科 = 6 主科 + 1 艺术科

## 七、版本演进

| 版本 | 计划 | 关键变化 |
|------|------|---------|
| v1.0 (本轮) | 启动 + 7 学科示范 | 16 字段结构, 7+1 学科覆盖 |
| v1.1 | 雪薇端批量生产 | 根据 review 反馈调字段 |
| v2.0 | 知识图谱打通 | 加 `prerequisite_chain_ids` (前驱策略) |
| v3.0 | 跨学科融合 | 加 `cross_subject_links` (文综三科关联) |

## 八、相关链接

- 规范: `handoff/SPDT004_STRATEGY_CARD_v1.0_规范.md`
- 验证器: `tools/strategy_card_validator.py`
- 4 步法规范: `handoff/MATH_001_4step_v1.0_规范.md` (类比参考)
- 4 步法数学母题: `D:/4_data/knowledge_cards/数学/4step/`
- PT-030 工具链: `handoff/PT-030_工具链_v1.0_完整onboarding.md`
- 双窗口协作: `handoff/SPDT004_DUAL_WINDOW_COLLABORATION_v1.0_给雪薇窗口.md`
