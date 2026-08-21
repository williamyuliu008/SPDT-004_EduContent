# v1.0 已废止产品归档

> **写入日期**：2026-08-21
> **依据**：[PRODUCT_LINE.md v2.0](../../../PRODUCT_LINE.md) §1.3 + §5
> **配套**：`git tag v1.0-final`（2026-08-21）
> **状态**：软归档（保留可溯源，不物理删除）

---

## 1. 归档目的

v1.0 产品线目录中列出的 9 大产品，经 willi 2026-08-21 评估后：
- 2 个**整体拿掉**（v1.0-P-004 微剧本 + v1.0-P-007 Skill）
- 3 个**降级为中间产物**（v1.0-P-005 知识链 / v1.0-P-006 配置包 / v1.0-P-008 视觉素材）

为**保留历史可溯源 + 防止误用 + 治理透明**，归档 v1.0 已废止产品的元信息。

> **重要**：本目录只放**索引 + 说明**。原文件**保留在原位置**（git 历史可查），不做物理删除。

---

## 2. 已废止产品清单

### 2.1 v1.0-P-004 微剧本（整体拿掉）

**v1.0 定位**：人物 + 事件 + 场景 → 沉浸式微剧本（4 幕结构）

**拿掉理由**（willi 决策）：
- 没有"最终用户消费形态"——本质是 P-001 视频的输入剧本
- 8 集规划只生产 2 集（ep01 颜真卿 + ep09 商鞅变法），资源浪费
- 涉及"艺术性/感染力"，偏离"教育/备考"功能性定位

**v2.0 处理**：合并到 P-001 视频的"剧本子模块"

**原位置文件**（保留可查）：

| 文件 | 路径 | 状态 |
|:---|:---|:---|
| 墨骨山河_ep01 颜真卿 | `2_structure/TextExperience/配置包_cafa_calligraphy_2026/scripts/墨骨山河_ep01_*.json` | 已入库（P-001 输入） |
| 墨骨山河_ep09 商鞅变法 | `2_structure/TextExperience/墨骨山河_ep09/scripts/墨骨山河_ep09_商鞅变法.json` | 已入库（P-001 输入） |
| ep02-08 规划 | `2_structure/TextExperience/配置包_cafa_calligraphy_2026/scripts/墨骨山河_ep0X_*.json` | 规划未生产 |

### 2.2 v1.0-P-007 Skill 方案（整体拿掉）

**v1.0 定位**：11 个 Skill + 3 条 Chain + 6 个 Style Pack + skill_selector.py，写作者辅助工具

**拿掉理由**（willi 决策）：
- 服务"写作者"超出"教育/备考"用户群
- 11 Skill + 3 Chain + 6 StylePack + Selector + Bridge 维护成本高
- 涉及"创作/写作"艺术性，偏离"教育/备考"功能性定位

**v2.0 处理**：整体拿掉，文档归档

**原位置文件**（保留可查）：

| 文件 | 路径 | 状态 |
|:---|:---|:---|
| SKILL_*.md（11 个 Skill 文档） | `docs/04-Skills/SKILL_*.md` | 📦 归档（不删除） |
| SKILL_REGISTRY.json | `docs/04-Skills/SKILL_REGISTRY.json` | 📦 归档（不删除） |
| SKILL_MATRIX_hist_writing.md | `docs/04-Skills/SKILL_MATRIX_hist_writing.md` | 📦 归档（不删除） |
| skill_selector.py | `docs/04-Skills/skill_selector.py` | 📦 归档（不删除） |
| skill_bridge.py | `docs/04-Skills/skill_bridge.py` | 📦 归档（不删除） |
| SKILL_MANAGEMENT.md | `docs/04-Skills/SKILL_MANAGEMENT.md` | 📦 归档（不删除） |
| SKILL_SELECTOR_README.md | `docs/04-Skills/SKILL_SELECTOR_README.md` | 📦 归档（不删除） |
| feedback_logs_combined.md | `docs/04-Skills/feedback_logs_combined.md` | 📦 归档（不删除） |
| 各 Skill 的 test_runs/ | `docs/04-Skills/hist-*/test_runs/` | 📦 归档（不删除） |

> 注：`docs/04-Skills/` 目录在 v2.0 仍保留（作 git 历史），不再维护。如未来需要复活，可基于 git tag `v1.0-final` 重建。

---

## 3. 降级为中间产物（3 个，v2.0 不算"产品"）

### 3.1 v1.0-P-005 知识链 → v2.0 M-001 知识链

- v2.0 定位变化：从"独立产品"降为"P-001 视频 + P-003 电子书的共享骨架"
- 原位置：`2_structure/TextExperience/古史_v*/`（保留可查）
- v2.0 状态：中间产物，活跃

### 3.2 v1.0-P-006 配置包 → v2.0 M-002 配置数据

- v2.0 定位变化：从"独立产品"降为"P-002 知识卡片在 APP 端的学科分组"
- 原位置：`4_adapt/AdaptivePrepPlatform/_03_subject_packs/`（保留可查）
- v2.0 状态：中间产物，活跃

### 3.3 v1.0-P-008 视觉素材 → v2.0 M-003 视觉素材

- v2.0 定位变化：从"独立产品"降为"M-002 cafa 的子模块（草书辨析）"
- 原位置：`products/PT-039_CalligraphyVision/草书辨析卡/`（保留可查）
- v2.0 状态：中间产物，活跃

---

## 4. 引用关系（v1.0 → v2.0）

```
v1.0-P-004 微剧本 ──[合并]──→ v2.0 P-001 视频的"剧本子模块"
v1.0-P-007 Skill 方案 ──[拿掉]──→ 不复活（git tag v1.0-final 保留历史）

v1.0-P-005 知识链 ──[降级]──→ v2.0 M-001 中间产物
v1.0-P-006 配置包 ──[降级]──→ v2.0 M-002 中间产物
v1.0-P-008 视觉素材 ──[降级]──→ v2.0 M-003 中间产物

v1.0-P-001 视频 → v2.0 P-001 视频
v1.0-P-002 电子书 → v2.0 P-003 电子书（重排）
v1.0-P-003 知识卡片 → v2.0 P-002 知识卡片（重排）
v1.0-P-009 音频 → v2.0 P-004 音频
```

---

## 5. 复活规则（避免历史反复）

如需复活已废止产品：
- **v1.0-P-004 微剧本** → 改为"扩展 P-001 视频的剧本子模块"，不复独立产品
- **v1.0-P-007 Skill 方案** → 评估"教育/备考"用户群是否真正需要；如需要，**v3.0 重新分类**为"创作者工具"独立章节，**不与真产品混编**

复活流程：
1. 走 RFC（变更影响大）
2. willi 拍板
3. 新建 v3.0 重新分类
4. git tag `v2.0-final` 标记当前状态

---

## 6. 文件索引

```
docs/archive/v1.0_product_line/README.md        ← 本文件
PRODUCT_LINE.md v2.0                            ← 当前产品线目录
git tag v1.0-final                              ← v1.0 历史快照
git tag v2.0 (待 willi 拍板)                    ← v2.0 当前快照
```

---

## 7. 版本历史

| 版本 | 日期 | 核心变更 |
|:---|:---|:---|
| v1.0 | 2026-08-21 | 首发归档：v1.0-P-004 微剧本 + v1.0-P-007 Skill 拿掉，3 个降级，引用关系明确 |
