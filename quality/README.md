# quality/ · L0_stable · 质量审计基础设施

> **Layer**: L0_stable（受 W_low 保护）
> **依据**: [LAYERS.md](../LAYERS.md) + [WINDOWS.md](../WINDOWS.md) + [SPDT.yaml](../SPDT.yaml)
> **状态**: 已稳定 / 工具链齐全

---

## 定位

质量门禁基础设施。包括：
- 黄金测试用例（正确 vs 缺陷对比）
- 编译器门禁（render / static）
- 验证脚本（mutation / gate_validation）
- 方法论文档
- 集成测试

## 子模块

| 子模块 | 用途 | 状态 |
|:---|:---|:---:|
| `content_quality_gate/_01_golden_tests/` | 黄金测试用例（correct + defects） | ✅ 稳定 |
| `content_quality_gate/_02_compiler/` | 编译器门禁（render / static） | ✅ 稳定 |
| `content_quality_gate/_03_validation/` | 验证脚本（mutation / gate） | ✅ 稳定 |
| `content_quality_gate/_04_methodology/` | 方法论文档 | ✅ 稳定 |
| `content_quality_gate/_05_integrations/` | 集成测试 | ✅ 稳定 |
| `content_quality_gate/_00_governance/` | 治理规范 | ✅ 稳定 |

## 与 L1/L2 的关系

- **消费方（L1）**: CGM SOP / Skill 系统 / 知识卡片系统
- **被消费方**: 无（L0 是底层）

## 改动窗口

- 仅 **W_low**（稳定维护窗，1-2 周一次）
- 任何改动需走 RFC（哪怕 1 行）

## 引用

- 上层: [SPDT.yaml](../SPDT.yaml) 中 pdt_id=`CardQualityAuditor`
- 文档: [docs/04-Skills/SPDT-004_知识卡片_测试标准设计.md](../docs/04-Skills/SPDT-004_知识卡片_测试标准设计.md)
- 治理: [docs/governance/分层治理检查清单.md](../docs/governance/分层治理检查清单.md)
