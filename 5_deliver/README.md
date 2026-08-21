# 5_deliver/ · L1_evolutionary · 触达交付层

> **Layer**: L1_evolutionary（默认 W_mid）
> **依据**: [LAYERS.md](../LAYERS.md) + [WINDOWS.md](../WINDOWS.md) + [SPDT.yaml](../SPDT.yaml)
> **状态**: 单 APP 运行中（rujing）

---

## 定位

流水线第 5 阶段——多端分发终端。当前聚焦 HarmonyOS APP（rujing），其他终端（Web、跨平台）暂未启动。

## 子模块

| 子模块 | 用途 | 状态 |
|:---|:---|:---:|
| `TextExperienceAPP/` | HarmonyOS APP 开发平台 | ✅ 活跃 |
| `TextExperienceAPP/apps/rujing/` | 国美书法备考 APP | ✅ 运行 |

## 协作方

- **上游（L0）**: knowledge_cards（被消费）
- **上游（L1）**: 2_structure TextExperience（消费卡库）

## 改动窗口

- 默认 **W_mid**（演化迭代窗）
- 紧急修复可在 W_low

## 关键里程碑

- 2026-07-30: 12 个其他 app 迁移至 SPDT-001_Harmony/apps/
- 2026-08-21: app_count 13 → 1（待 SPDT.yaml v3.0 同步修复）

## 引用

- 上层: [SPDT.yaml](../SPDT.yaml) 中 pdt_id=`TextExperienceAPP`
- 治理: [docs/governance/分层治理检查清单.md](../docs/governance/分层治理检查清单.md)
