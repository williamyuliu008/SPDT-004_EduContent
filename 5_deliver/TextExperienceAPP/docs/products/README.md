# SPDT-001: 鸿蒙生态开发

> 鸿蒙 NEXT 精品 App 矩阵 — 5 品牌 13 APP，年产 100+ 款

## 快速导航

| 文件 | 用途 |
|---|---|
| [SPDT.yaml](SPDT.yaml) | 产品线注册 + 品牌清单 + 技术栈 + KPI |
| [MANAGEMENT.md](MANAGEMENT.md) | 管理规范（品牌生命周期/目录规范/协作规则） |
| [pdt-registry.yaml](pdt-registry.yaml) | 品牌 PDT 详细注册表 |
| [docs/](docs/) | 跨品牌文档 + 5 份品牌手册 |

## 品牌一览

| 品牌 | 颜色 | APP | 目标 | 状态 |
|:---|:---|:---|:---|:---|
| ThinkKit | #5B8C5A | 6 (coach/flashcard/zknote/mindmap/quiz/reader) | 50 | ✅ |
| Craftsman | #E87A2A | 4 (arkui/ohpm/utils/utils-v2) | 20 | ✅ |
| HarmonyCoder | #7B2D8E | 1 (旗舰) | 1 | ✅ |
| RhythmHabit | #3B82B0 | 1 (habit) | 20 | ✅ |
| GaokaoAgent | #C44536 | 1 (agent) | 10 | ✅ |

> **合计**: 13/13 编译通过 · 13/13 签名通过 · 5/5 品牌CI接入

## 技术栈

```
ArkTS strict mode → ArkUI Stage → Navigation+NavPathStack
    │
    ├── common/ (23源文件: 12组件+5工具+2存储+1主题+2算法)
    │
    ├── SDK: target 26.0.0 → compat 6.1.1(24)
    │
    └── CI: PREFLIGHT → BUILD → SIGN → DEPLOY → REPORT
```

## 代码仓

- **主代码仓**: [D:\92_products\SPDT-001_Harmony](D:\92_products\SPDT-001_Harmony)
- **管理仓**: [D:\92_products\SPDT-001_Harmony](D:\92_products\SPDT-001_Harmony)

## 当前负责人

鸿蒙特使 (agent-e926h) · 2026-07-07
