# strategy_crosslink v1.1 效果报告

## 立项目标
让 4 步法母题 ↔ 策略卡 互引从"100% 覆盖（平均 1 个策略/张）"提升到"2+ 关联占 70%+"

## 关键改动 (v1.0 → v1.1)
- **method_tag 智能映射 (METHOD_TAG_RULES)**: 12 个前缀（G-/G1-/G2-/T-/T1-/V-/M-/F-/S-/A-/P-/X-）→ 必推荐策略链
- **关键词细化**: 短词改长词（"向量" → "向量法" / "建系"），但保留 v1.0 基础词（"异面" "面面垂直" "线面垂直" "二面角"）避免回退
- **UTF-8 stdout 修复**: scan/report 子命令强制 `sys.stdout = io.TextIOWrapper(... encoding='utf-8', errors='replace')` 解决 Windows GBK 乱码

## 跑批效果 (跨 7 学科 20 张母题)

| 关联数 | v1.0 (06ef170) | v1.1 | 提升 |
|:---|:---|:---|:---|
| 0 关联 | 0 | 0 | 持平 |
| 1 关联 | 19 张 (95%) | 6 张 (30%) | **-13** |
| 2+ 关联 | 1 张 (5%) | **14 张 (70%)** | **+13** |
| 平均/张 | 1.05 | **1.70** | **+0.65** |

### 数学 15 张细分
- 1 关联: 2 张 (13%) — pp_001 (G1-中位线), pp_009 (T-面面垂直升级)
- 2 关联: 13 张 (86%) — G-/G2-/T1-/V- 前缀全部命中
- 平均: 1.87 关联/张

### 历史 5 张
- 历史 method_tag 实际形态待补 METHOD_TAG_RULES (现仅关键词匹配)

## 已知 gap
- **5 学科母题 (语文/英语/地理/政治/书法) 0 张入库**: P0-A 下阶段需补 41 张
- **历史 method_tag 规则待补**: hp_001-005 实测后才填 METHOD_TAG_RULES 的 C-/M-/T-/W- 段
- **地理/政治/语文/英语/书法 method_tag 前缀规则**: 待 5 学科母题入库后回填

## 工具命令
```bash
# 扫匹配 (不写回)
python tools/strategy_crosslink.py scan --root D:\4_data\knowledge_cards

# 写回 (双向回填母题 applicable_strategies + 策略 original_problem_id)
python tools/strategy_crosslink.py crosslink --root D:\4_data\knowledge_cards

# 报告
python tools/strategy_crosslink.py report --root D:\4_data\knowledge_cards
```

## 后续计划
- 5 学科母题入库 (语文 10 + 英语 10 + 地理 8 + 政治 8 + 书法 5 = 41 张)
- 母题入库后跑 v1.1 crosslink，验证跨学科 method_tag 规则
- rujing 学习中心 App 集成 `applicable_strategies` 字段（详情页加"适用策略"tab）
