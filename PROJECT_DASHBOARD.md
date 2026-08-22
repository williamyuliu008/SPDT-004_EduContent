# SPDT-004 项目总览 v1.0

> **版本**：v1.0（W26 战略层首发）
> **目的**：一文档看全 SPDT-004 当前状态——治理 / 产物 / 协作 / 下一阶段
> **配套**：[LAYERS.md](LAYERS.md) + [WINDOWS.md](WINDOWS.md) + [PRODUCT_LINE.md](PRODUCT_LINE.md) + [docs/REVIEW_INBOX.md](docs/REVIEW_INBOX.md)
> **更新**：每阶段准出门时刷新

---

## 1. 一句话定位

**SPDT-004 = 自适应备考智能体产品线**。5 阶段流水线（1_ingest → 2_structure → 3_render → 4_adapt → 5_deliver）生产 4 大真产品（视频 / 知识卡片 / 电子书 / 音频），服务"教育/备考"用户。

**核心理念**：不靠 AI 自由创作，靠 CGM 约束型生成方法论 + 模板 + 审计，把专家经验编码为可复用的工业级生产线。

---

## 2. 当前快照（W26 启动时）

| 维度 | 状态 |
|:---|:---|
| **战略层** | v3.0 上半场准出门 PASS（4/4 GOLD，[docs/v3.0_h1_signoff.md](docs/v3.0_h1_signoff.md)）|
| **下一阶段** | v3.0 下半场：英语 49 概念扩展 |
| **4 真产品** | P-001/002/003/004 全部 GOLD ✅ |
| **治理层** | 4 份规范文档 + 3 个 git tag |
| **CI 工具** | 3 个治理工具 + 1 个质量工具 + 1 个 hook 安装器 |
| **协作** | review_inbox 机制（W24 落地）|
| **输入端** | ENVELOPE 规范 + 4 个自动化脚本（W25 落地）|
| **产物** | **188 链 1293 卡 ship 到 rujing APP** |
| **质量** | 4 真产品 P0 样本全 GOLD |
| **commits** | 11 个本轮（v2.3 之后）|
| **tags** | v1.0-final / v2.0 / v2.0-approved |

---

## 3. 治理结构（4 层文档）

```
LAYERS.md (3 层)
  L0_stable       4 个 pdt (1_ingest / 知识卡工具链 / 质量审计 / 模板)
  L1_evolutionary 9 个 pdt (TextExperience / KTE / VFX / autoclaw_kit / Skill系统 / APP / 视觉库 / CGM SOP / OMAS)
  L2_experimental 7 个 pdt (4_adapt / 跨包联动 / 古史_v4 扩产 / 墨骨山河 ep02-08 / Stage A 改造 / T4 叙事审计 / 新 Skill)

WINDOWS.md (3 窗口)
  W_low   1-2 周一次  L0 修小修
  W_mid   每天/每周   L1 内容生产（默认）
  W_high  每天多次    L2 新功能

PRODUCT_LINE.md v2.0
  真产品 4 个: P-001 视频 / P-002 知识卡片 / P-003 电子书 / P-004 音频
  中间产物 3 个: M-001 知识链 / M-002 配置数据 / M-003 视觉素材
  已废止 2 个: v1.0-P-004 微剧本 / v1.0-P-007 Skill（git tag v1.0-final 锁档）

review_inbox (跨窗口协作)
  3 模板: prompt/decision/feedback
  4 步工作流: prompt → review → decisions → archive
  模拟样本: RUJING_001_handoff (4 决策)
```

---

## 4. CI 工具链（5 个）

| 工具 | 用途 | 状态 |
|:---|:---|:---:|
| `tools/layer_lint.py` | 跨层依赖检查 | ✅ 0 错 |
| `tools/window_check.py` | 窗口与改动层匹配 | ✅ OK |
| `tools/layer_doc_sync.py` | 文档与代码一致性 | ✅ 0 错 |
| `tools/accuracy_auditor.py` | 4 真产品准确性验收 | ✅ 全 GOLD |
| `.githooks/pre-commit` | Git commit 前自动跑 3 治理工具 | ✅ 已装 |

**实测**：
- P-002 知识卡片：93/93 v6.0 政治样本 GOLD
- P-003 电子书：1/1 H-M1 第一章 GOLD
- P-004 音频：1/1 古史 v3 ep01 GOLD
- P-001 视频：0 样本（推迟 W27+）

---

## 5. 输入端自动化（W25 落地）

```
1_ingest/
  ENVELOPE_SPEC.md            4 层接口机制 + 9 字段 JSON Schema
  schemas/envelope.schema.json
  processor.py                M0/M1/M2 集成调度
  watcher.py                  轮询 D:/4_data/ingest_queue/ 自动处理
  ingest_cli.py               CLI 入口 (new/process/list/status)
  install_watcher.py          一键安装 (Windows schtasks / Linux systemd)
```

**E2E 实测**：test-w25-e2e-001 投递 → watcher 自动处理 → 产出 ingested.json + audit_log.json → 投递 2_structure 队列 ✅

---

## 6. 关键文件索引（21 个）

| 路径 | 大小 | 类型 |
|:---|:---:|:---|
| LAYERS.md | 6.8K | 治理 |
| WINDOWS.md | 5.7K | 治理 |
| PRODUCT_LINE.md | 17.0K | 产品线 |
| AGENTS.md | 0.6K | 项目元信息 |
| SPDT.yaml | 20.8K | 产品线注册（v3.0）|
| docs/REVIEW_INBOX.md | 5.7K | 协作机制 |
| docs/governance/分层治理检查清单.md | 8.0K | 治理检查 |
| 1_ingest/ENVELOPE_SPEC.md | 8.7K | 输入端规范 |
| 1_ingest/schemas/envelope.schema.json | 3.3K | JSON Schema |
| templates/default_config.yaml | 7.8K | 4 真产品参数集 |
| templates/audio_spec.yaml | 5.4K | P-004 模板 |
| products/PT-039_CalligraphyVision/草书辨析卡/template.yaml | 7.1K | M-003 模板 |
| tools/layer_lint.py | 10.3K | CI |
| tools/window_check.py | 11.6K | CI |
| tools/layer_doc_sync.py | 10.8K | CI |
| tools/accuracy_auditor.py | 13.2K | 质量 |
| tools/install_hooks.py | 4.8K | 安装器 |
| 1_ingest/processor.py | 7.9K | 自动化 |
| 1_ingest/watcher.py | 3.9K | 自动化 |
| 1_ingest/ingest_cli.py | 6.8K | CLI |
| 1_ingest/install_watcher.py | 4.4K | 安装 |
| handoff/rujing.md | 8.8K | RUJING 交接 |

---

## 7. 11 个本轮 commit + 3 个 tag

| commit | 描述 |
|:---|:---|
| 92fa7f6 | W21 分层 + 工具链 |
| 9ce08e2 | W22 顺手修残留 + CI 窗口规则 |
| 45f903a | PRODUCT_LINE v1.0 |
| 10e92f4 | PRODUCT_LINE v2.0 精简 |
| 6055f75 | v1.0 归档 + git tag v1.0-final |
| 7fcb767 | W22 输入端接口 + 4 工具（A→D→C→B）|
| 90b0f6b | accuracy_auditor 修 bug + 4 真产品分级 |
| 8272bbe | RUJING 项目交接文档 v1.0 |
| d818b32 | W24 治理持续运转 + review_inbox 机制 |
| d2779b4 | W25 输入端 watcher/CLI 自动化 |

**git tag**：
- `v1.0-final` — v1.0 9 大产品状态锁档
- `v2.0` — v2.0 规范草签
- `v2.0-approved` — v2.0 准出门拍板（W23 完成后）

---

## 8. 当前产物

### 8.1 4 真产品 P0 样本

| 产品 | 样本 | 评分 |
|:---|:---|:---:|
| P-001 视频 | 0（推迟 W27+）| — |
| P-002 知识卡片 | 93（v6.0 政治）| GOLD 100% |
| P-003 电子书 | 1（H-M1 第一章）| GOLD |
| P-004 音频 | 1（古史 v3 ep01）| GOLD |

### 8.2 rujing APP 内容（实测）

- **总链数**：188 链
- **总卡数**：1293 卡
- **学科分布**：历史 62 链 441 卡 / 政治 61 链 427 卡 / 地理 49 链 345 卡 / 其他 16 链 80 卡
- **推送成功率**：100%（173/173）

---

## 9. W21-W26 阶段总览

| 阶段 | 主题 | 状态 |
|:---|:---|:---:|
| W21 | 分层 + 窗口 + CI 工具链 | ✅ |
| W22 | 输入端接口 + 产品线精简 + v1.0 归档 | ✅ |
| W23 | v2.0 准出门 + P1A 推送（188 链 1293 卡）| ✅ |
| W24 | 治理持续运转 + 跨窗口 review_inbox | ✅ |
| W25 | 输入端 watcher/CLI 自动化 | ✅ |
| **W26** | **战略层 + 项目总览** | **⏳** |
| W27+ | v3.0 战略（待拍板）| 📋 |

---

## 10. v3.0 拍板（已完成 A+B — 详见 [docs/v3.0_approved.md](docs/v3.0_approved.md)）

| 方向 | 拍板 | 周期 | 关键产出 |
|:---|:---:|:---|:---|
| **A · 4 真产品闭环** | ✅ | W27-W30 | P-001 视频管线 + 4/4 真产品联合验收 |
| **B · 跨学科扩展（英语）** | ✅ | W31-W34 | 49 概念 GOLD + 1→N 复制 SOP |
| **C · 持续运营深化** | ⏸️ v3.1 | — | 推迟（当前 cron 已在跑）|
| **D · review_inbox 工具化** | ⏸️ v3.1 | — | 推迟（需求未充分验证）|

**A 止损策略**：W28 结束前跑不通 → 降级演示级（PPT+配音），保住节奏。

---

## 11. 已知坑（不该再踩）

| # | 坑 | 解决 |
|:---:|:---|:---|
| 1 | `_batch_convert_push.py` 漏历史 62 套 | 已修（90b0f6b）|
| 2 | `accuracy_auditor` source_citation 检查错位 | 已修（90b0f6b）|
| 3 | `processor.py` 双层 TextIOWrapper 包装 | 已修（d2779b4）|
| 4 | rujing APP 端口（DevEco 关闭 / 手机锁屏 / IP 变）| handoff/rujing.md 6 个坑有说明 |
| 5 | 2_structure/TextExperience 是未注册 submodule | 历史问题，不影响工作流 |

---

## 12. 文件索引

```
PROJECT_DASHBOARD.md           ← 本文件 (W26)
LAYERS.md                       分层定义
WINDOWS.md                      窗口节奏
PRODUCT_LINE.md                 产品线 v2.0
SPDT.yaml                       产品线注册 v3.0
docs/REVIEW_INBOX.md            跨窗口协作机制
docs/governance/分层治理检查清单.md
1_ingest/ENVELOPE_SPEC.md       输入端规范
templates/default_config.yaml   4 真产品参数集
tools/                          5 个 CI/质量工具
handoff/rujing.md               RUJING 交接
review_inbox/                   跨窗口协作目录
docs/archive/v1.0_product_line/ v1.0 归档
```

---

## 13. 版本历史

| 版本 | 变更 |
|:---|:---|
| v1.0 | 首发：12 节（定位/快照/治理/CI/输入端/文件/commit/产物/阶段/v3.0 候选/坑/索引）|
