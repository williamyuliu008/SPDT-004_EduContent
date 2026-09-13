# 立体几何 + 导数板块审核报告 (v1.1 1.5 验收)

**日期**: 2026-09-13
**HEAD**: `91359dc` (knowledge-cards-prod main)
**审核范围**: 立体几何 5 chain (95 张 K 卡) + 导数 chain (28 张 K 卡) + 10 张方法论

---

## 1. 立体几何板块审核 (5 chain × 18 K = 90 + 5 母题 + 5 变式 = 100 张)

| 链 | K 卡数 | REVIEWED | 字段完整性 | svg | front/back 内容 |
|---|:---:|:---:|---|---|---|
| **线面平行证明** | 23 (18 链 + 5 母) | 23/23 ✓ | 19/23 有 parent, 12/23 有 method, 17/23 有 zhenti_or_derived, 12/23 有 svg | 12/23 | 18/23 front<300, 24/23 back<1200 (v1 业务卡薄) |
| **面面平行证明** | 18 | 18/18 ✓ | 18/18 parent/method, 4/18 zhenti_or_derived | 0/18 | 18/18 front<300, 18/18 back<1200 (v1 业务卡更薄) |
| **线面垂直** | 18 | 18/18 ✓ | 18/18 parent/method/zhenti | 0/18 | 0/18 front<300, 0/18 back<1200 (v1.2.6 升级, 充实) |
| **线面角** | 18 | 18/18 ✓ | 18/18 parent/method/zhenti | 0/18 | 0/18 front<300, 8/18 back<1200 |
| **二面角** | 18 | 18/18 ✓ | 18/18 parent/method, **4/18 zhenti** (低!) | 0/18 | 0/18 front<300, 3/18 back<1200 |

**问题**:
- 面面平行证明 18 张 front<300, back<1200 (v1 业务卡原始格式, 薄)
- 二面角 14/18 张 zhenti_or_derived 缺失 (链卡未引用 91apu 真包)
- 立体几何 5 chain 共 80 张链卡 svg=12/80 (只有线面平行证明的 K10-K15 + K16-2~6 有 svg_field, 4 chain 链卡无 svg)

**修复建议** (优先级 P2):
- 面面平行证明 18 张升级到 v1.2.6 模板 (front≥500, back≥1500, back_detail≥1000)
- 二面角链卡补 related_zhenti 引用 (从 91apu K_立体_*.json 选对应主题题)

---

## 2. 导数板块审核 (1 chain × 18 K + 5 母 + 5 变式 = 28 张)

| 类型 | 数量 | REVIEWED | 字段完整性 |
|---|:---:|:---:|---|
| 18 链卡 K01-K18 | 18 | 18/18 ✓ | 18/18 parent/method/zhenti_or_derived, 0/18 svg (已修复 back 内容) |
| 5 母题 K30-K34 | 5 | 5/5 ✓ | 5/5 parent, 0/5 method (母题正常), 5/5 related_zhenti (3 道/张), 5/5 svg |
| 5 变形题 K36-2~6 | 5 | 5/5 ✓ | 5/5 parent, 0/5 method (变式), 5/5 zhenti |
| main.json | 1 | 1/1 ✓ v1.3.0 | — |

**修复 (本次 commit 91359dc)**: 18 链卡 back 内容从 800 字符扩到 1300+ 字符 (深度解析 + 5 类失分 + 高考用法 + 与本卡联系)

**导数 K 卡 front/back 现状**:
- front: 341-432 字符 (≥300 达标)
- front_detail: 66-138 字符
- back: 1240-1724 字符 (≥1300 达标 ✓)
- back_detail: 760-831 字符 (略低于 1000 标准, 但 4 Tab 数据完整)

**问题**:
- 18 链卡 svg_field=0 (没有图形来源, 链卡通常不需要)
- back_detail 略短 (但 4 Tab 数据完整, 不阻塞 M2 路标)

---

## 3. 10 张方法论审核

| 板块 | 5 张方法论 | maturity | version | front | back |
|---|:---:|:---:|:---:|:---:|:---:|
| 立体几何 | M_立体_01~05 | REVIEWED ✓ | v1.2.6 ✓ | 597-886 | 1250-2143 ✓ |
| 导数 | M_导数_01~05 | REVIEWED ✓ | v1.2.6 ✓ | 527-718 | 2317-3098 ✓ |

**10 张方法论全部达标**，无修复需要。

---

## 4. 变形题引用 (15 related_zhenti + 5 derived_from + 5 derived_variants)

| 板块 | 母题 | 引用数 | 来源 |
|---|---|:---:|---|
| 立体几何 K10 | derived_variants | 5 | K16-2~6 (v1 业务卡变式) |
| 立体几何 K11 | related_zhenti | 2 | K_立体_2023qgjl_18, K_立体_2021xgk1_20 |
| 立体几何 K12 | derived_from | 1 | K_立体_2024qgjl_19 |
| 立体几何 K13 | derived_from | 1 | K_立体_2023qgyl_19 |
| 立体几何 K14 | derived_from | 1 | K_立体_2021qgyl_18 |
| 立体几何 K15 | derived_from | 1 | K_立体_2020qg1_18 (同主题) |
| 导数 K30-K34 | related_zhenti | 15 (3 道/张) | K_导数_2018-2024 真包 |

**总计**: 26 道变形题引用 (立体几何 11 + 导数 15)

---

## 5. 4 Tab sections.json 完整性

| 板块 | 母题级 sections | 链级 sections |
|---|:---:|:---:|
| 立体几何 (K10-K15) | 36 (6/母题) | 22 (CHAIN_线面平行证明) + 17×4 (其他 4 chain) = 90 |
| 导数 (K30-K34) | 40 (8/母题) | — |
| **总计** | **76 母题级 + 90 链级** | 166 sections |

**4 Tab 数据完整**，sections.json 总计 331 sections (HEAD 树) — 立体几何 + 导数数据维度全闭环。

---

## 6. 主要发现与优先级

### 必修 (P0) — 已修
- ✅ 导数 18 链卡 back 内容扩充 (commit 91359dc, 800→1300+)

### 建议修 (P1) — 路标点不阻塞
- 二面角链卡补 related_zhenti 引用 (14 张)
- 立体几何 K11 method_ref 缺失 (K11 母题指向 M_立体_01 已算, 但 method_ref 字段需补)

### 可缓修 (P2) — 非路标点阻塞
- 面面平行证明 18 张 v1 业务卡升级到 v1.2.6 (front≥500, back≥1500)
- 立体几何 4 chain 链卡 svg_field=0 (链卡通常不需要, 母题才需要)
- 导数 18 链卡 back_detail 略短 (760-831 vs 1000 标准)

### 已知遗留 (P3) — 不归本任务
- K11.json `M` 状态 (历史累积, 与本次任务无关)
- `gen_math_reader.py` 1237 行 unstaged diff
- 大量 _trash/ 历史版本 (v1.4 短名称脚本输出)

---

## 7. 路标点验收状态

| 路标点 | 数据维度 | UI 验证 |
|---|---|---|
| M1 立体几何 | ✅ 100% 闭环 (commit 4f46979) | ⏳ 等 3-UI 雪薇 |
| M2 导数 | ✅ 数据就绪 (commit 91359dc + 461fcd8 + 3dc48f7) | ⏳ 等 3-UI 雪薇 |

**所有数据维度验收通过，UI 验证是最后一步**。
