# 知识管线和 App 接口分析报告
> **日期**：2026-08-01
> **背景**：地理山河系列接入后，发现知识管理层（Stage 1-2）与知识展现层（App rawfile）之间接口存在显著规范缺口
> **目标**：识别接口结构、版本管理问题和优化方向

---

## 一、现有接口全貌

### 接口地图

```
┌─────────────────────────────────────────────────────────────────────┐
│                      知识管理层（Stage 1-2）                          │
│                                                                     │
│  ① 原始素材                                                           │
│      ↓                                                                │
│  ② 1_ingest 管线                                                      │
│      ├─ M0: entry_judge     → 判定适用性                              │
│      ├─ M1: syllabus_parser  → content_spec.yaml                      │
│      └─ M2: calibrator      → raw_entries.json + audit_log.json      │
│                                                                     │
│  ③ 4_adapt 知识包（KB 层）                                            │
│      ├─ meta.json           ← 链定义（chain_id / chain_name / causal_logic）│
│      ├─ kb_vocab.json       ← 知识条目（206条，含 kb_id / structured_content）│
│      └─ ability_list.json   ← 能力列表                                 │
│                                                                     │
└───────────────  ★ 接口 A：KB → App rawfile JSON ★ ───────────────────┘
                        │
                        │  Python 转换（手工脚本，无版本控制）
                        │  kb_vocab.json (206条)
                        │      ↓
                        │  *_cards.json (32条)
                        │  丢弃了：kb_id、structured_content、exam_tips...
                        │
┌───────────────────────┴─────────────────────────────────────────────┐
│                      知识展现层（Stage 3 + App）                      │
│                                                                     │
│  ④ 5_deliver rawfile                                                │
│      ├─ geo_cards.json      schema=v3, package_id/title             │
│      ├─ mogustory_cards.json schema=v3, package_id/title             │
│      └─ cafa_cards.json     schema=1.0, pack_id/title (≠v3!)       │
│                                                                     │
│  ⑤ App ImportService.ets                                           │
│      └─ importCardPackage() → db.upsertCard() → Chain + Card 表     │
│                                                                     │
│  ⑥ App Database                                                     │
│      └─ Chain { chain_id, title, subject, chain_type, narrative, ...}│
│         Card { card_id, chain_id, front, back_core, back_detail, ...}│
└─────────────────────────────────────────────────────────────────────┘
```

---

## 二、现有 Schema 对比

| 字段 | geo_cards.json (v3) | mogustory_cards.json (v3) | cafa_cards.json (v1.0) | App Card 接口 |
|:---|:---|:---|:---|:---|
| 顶层 package_id | ✅ | ✅ | ❌ 用 `pack_id` | — |
| 顶层 package_title | ✅ | ✅ | ❌ 用 `pack_title` | — |
| 顶层 schema_version | ✅ `"v3"` | ✅ `"v3"` | ✅ `"1.0"` | — |
| 顶层 total_cards | ✅ | ✅ | ✅ | — |
| 顶层 total_chains | ✅ | ✅ | ✅ | — |
| card_id | ✅ | ✅ | ✅ | ✅ |
| chain_id | ✅ | ✅ | ✅ | ✅ |
| chain_title | ✅ | ✅ | ✅ | ✅ |
| card_type | ✅ `"node"`/`"strategy"` | ✅ | ❌ 用 `NODE`/`STRATEGY` | ✅ |
| chain_role | ✅ | ✅ | ❌ 无 | ✅ |
| front | ✅ | ✅ | ✅ | ✅ |
| back_core | ✅ | ✅ | ✅ | ✅ |
| back_detail | ✅ | ✅ | ✅ | ✅ |
| tags | ✅ | ✅ | ✅ | ✅ |
| subject | ❌ | ❌ | ✅ | ✅ (运行时推断) |
| difficulty | ❌ | ❌ | ✅ | ❌ |
| exam_type | ❌ | ❌ | ✅ | ❌ |
| scoring_points | ❌ | ❌ | ✅ | ❌ |
| maturity | ❌ | ❌ | ✅ | ✅ (运行时硬编码 RAW) |

---

## 三、核心问题识别

### 问题 1：Schema 版本号形同虚设（严重）

`geo_cards.json` 和 `mogustory_cards.json` 都声称 `schema_version: "v3"`，但字段完全不同：

- v3 没有 `pack_id`（用 `package_id`）
- v3 没有 `subject`（由 ImportService 推断）
- v3 没有 `difficulty` / `exam_type` / `scoring_points`

更严重的是 `cafa_cards.json` 用 `schema_version: "1.0"`，字段又不同。

**根因**：`schema_version` 从未被 App 层校验——ImportService 直接按字段名取值，没有任何版本兼容性处理。

### 问题 2：知识溯源链断裂（严重）

```
kb_vocab.json:
  "kb_id": "KB_GEO_HH_002",
  "concept": "黄河含沙量",
  "structured_content": {
    "年均含沙量": "35kg/m³（陕县站）",
    "对比长江": "0.54kg/m³",
    "年输沙量": "约16亿吨"
  }

↓ (手工转换，丢失了关联)

geo_cards.json:
  "card_id": "GEO_NAT_001",
  "front": "黄河的泥沙从哪里来？...",
  "back_core": "黄河中游流经黄土高原..."
  （无 kb_id 引用，无 structured_content）
```

**后果**：
- 无法回答"这张卡来自哪个 KB 条目"
- 无法追踪"哪个 KB 条目被改动了，需要重新生成哪些卡"
- 无法做增量更新（只能全量重新生成）

### 问题 3：App 层 hardcoded 学科映射（中等）

`ImportService.ets` 的 `inferSubject()` 和 `getXxxDisplayTitle()` 是硬编码在代码里的。**每新增一个科目就要改 ImportService.ets**：

```typescript
// 每加一个科目就要在这里加判断
if (chain_id.startsWith('GEO_山河_') ||
    chain_id.startsWith('GEO_人地_') ||
    chain_id.startsWith('GEO_区域_')) {
  return Subject.GEOGRAPHY;
}
```

### 问题 4：无接口版本管理（中等）

- `kb_vocab.json` 有 `version: "1.0.0"`，但没有语义化版本规则
- `*_cards.json` 没有 `kb_version` 或 `source_ref` 字段
- App 端没有对输入 Schema 做版本校验

### 问题 5：kb_vocab.json 包含量远超 App 需求

206 个 KB 条目 → 只选了 32 个卡片。其他 174 个知识条目对 App 完全不可见。这意味着：
- KB 的真正价值（详细 structured_content、exam_tips、scoring_points）没有被利用
- App 展示的只是冰山一角

---

## 四、接口优化方案

### 4.1 统一 Schema 版本（v4 提案）

废弃 `schema_version` 的随意命名，改为**语义化接口版本**：

```json
{
  "interface_version": "4.0.0",
  "kb_source": {
    "pack_id": "geo_shanhe_2026",
    "kb_version": "1.0.0",
    "generated_at": "2026-08-01T00:00:00+08:00",
    "generator": "build_cards_from_meta.py"
  },
  "package_id": "GEO_SHANHE_SERIES",
  "package_title": "地理山河系列",
  "node_cards": [
    {
      "card_id": "GEO_NAT_001",
      "chain_id": "GEO_山河_黄河",
      "chain_title": "黄河·九曲入海",
      "card_type": "node",
      "chain_role": "pivot",
      "front": "黄河的泥沙从哪里来？...",
      "back_core": "黄河中游流经黄土高原...",
      "back_detail": "...",
      "tags": ["黄河", "水土流失"],
      "kb_lineage": [
        { "kb_id": "KB_GEO_HH_001", "weight": 0.6 },
        { "kb_id": "KB_GEO_HH_002", "weight": 0.4 }
      ]
    }
  ],
  "total_cards": 32,
  "total_chains": 16
}
```

**关键变化**：
1. `interface_version`：接口协议版本（App 解析器必须支持）
2. `kb_source`：溯源信息（追踪来源 KB 包和版本）
3. `kb_lineage`：卡片与 KB 条目的多对多关联（含权重）

### 4.2 App 端版本协商（ImportService 升级）

```typescript
interface PackageManifest {
  interface_version: string   // e.g. "4.0.0"
  kb_source: {
    pack_id: string
    kb_version: string
  }
  // ... rest of fields
}

// ImportService 读取时先检测版本
function parsePackage(raw: string): PackageManifest {
  const obj = JSON.parse(raw)
  const ver = obj.interface_version ?? inferLegacyVersion(obj)
  
  // 版本协商：支持降级
  if (!semver.satisfies('4.0.0', `^${ver}`)) {
    HiLog.warn('Unsupported interface version: ' + ver)
    // 尝试转换...
  }
  return obj
}

// 硬编码映射改为配置驱动
// 从 chain_id 前缀表读取，存储在 App 配置中，支持热更新
const SUBJECT_PREFIX_MAP: Record<string, Subject> = {
  '墨骨山河': Subject.CALLIGRAPHY,
  'CHAIN_CAFA_Ep': Subject.CALLIGRAPHY,
  'GEO_山河_': Subject.GEOGRAPHY,
  'GEO_人地_': Subject.GEOGRAPHY,
  'GEO_区域_': Subject.GEOGRAPHY,
  // 新科目：只需在配置文件中添加，无需改代码
}
```

### 4.3 KB→Cards 转换管道（自动化）

当前是手工 Python 脚本，应升级为版本化的转换管道：

```python
# build_cards_from_kb.py — KB → App Cards 转换器
# 位置：1_ingest/ 或 4_adapt/ 中，作为正式产出工具

class CardBuilder:
    def __init__(self, kb_path: Path, output_path: Path):
        self.kb = json.load(open(kb_path))
        self.meta = json.load(open(kb_path.parent / 'meta.json'))
        self.output_path = output_path
        
    def build(self, options: BuildOptions) -> PackageManifest:
        """
        1. 读取 meta.json 中的 chains
        2. 每个 chain 选取 KB 条目（按 weight 排序选 top-K）
        3. 从 KB 条目提取 front/back_core/back_detail
        4. 写入 kb_lineage 追溯信息
        5. 输出带 interface_version 和 kb_source 的 PackageManifest
        """
        pass
    
    def validate(self, manifest: PackageManifest) -> list[str]:
        """输出前质量检查"""
        errors = []
        # interface_version 存在
        # 所有 card 有 kb_lineage
        # chain_id 与 meta.json 一致
        # ... 
        return errors
```

---

## 五、版本管理方案

### 5.1 语义化版本规则（针对接口协议）

| 字段 | 变更规则 |
|:---|:---|
| **MAJOR**（4→5） | App 端不兼容变更：删字段、改字段类型、删卡片类型 |
| **MINOR**（4.1→4.2） | 向后兼容变更：新增可选字段、新增卡片类型 |
| **PATCH**（4.0.0→4.0.1） | 修正性变更：字段语义澄清（不影响解析器） |

### 5.2 KB 包版本规则

| 字段 | 变更规则 |
|:---|:---|
| **MAJOR** | 链结构变化（链增删、chain_id 改名） |
| **MINOR** | 知识条目重大修正（数值变化、定义修正） |
| **PATCH** | 标签/措辞调整，不影响内容实质 |

### 5.3 App rawfile 接口与 KB 版本的关系

```
KB 包 v1.2.0
    ├─ meta.json v1.2.0
    ├─ kb_vocab.json v1.2.0
    └─ *_cards.json (由 v1.2.0 生成)
            interface_version: "4.0.0"
            kb_version: "1.2.0"
```

**规则**：
- 只要 KB 的 MAJOR 版本不变，Cards 的 interface_version 不变
- Cards 的 interface_version 由 KB 转换工具统一写入
- App ImportService 只需声明自己支持的 interface_version 范围

---

## 六、实施建议

### 立即可做（不破坏现有流程）

1. **统一顶层字段命名**：`package_id`/`package_title` vs `pack_id`/`pack_title` → 统一为 `package_id`/`package_title`，App 层兼容两者
2. **App 层增加 `kb_source` 字段读取**（可选，不影响现有导入）
3. **在 SOP 中明确定义"接口 Schema 版本"和"KB 包版本"的区别**

### 下一迭代（需要 App 改动）

4. **升级 ImportService**：支持 `interface_version` 字段读取和版本协商
5. **迁移科目映射到配置**：从 hardcoded 代码 → JSON 配置文件
6. **转换工具规范化**：将手工脚本 → 正式版本化管理工具

### 长期演进

7. **kb_lineage 字段**：建立 KB↔Cards 的可追溯链路
8. **增量更新机制**：基于 kb_version 比对，只重新生成变化的链对应的卡

---

## 七、Open Questions

| 问题 | 影响 | 建议 |
|:---|:---|:---|
| App 是否需要感知 KB 的完整 structured_content？ | 如果需要，Interface 要传递更多字段 | 短期 No，保持现状；长期考虑"深度卡" vs "展示卡"分离 |
| KB 中的 206 条 vs App 中的 32 张卡，剩余 174 条如何利用？ | 知识浪费；AI 问答需要更多上下文 | 可在 AI 问答时按需从 KB 查，不一定要全量进 Cards |
| 是否需要支持多 KB 版本共存（历史版本卡 vs 最新卡）？ | 追溯和版本管理需求 | 短期 No，App 只保留最新版本 |

---

## 八、推荐：立即采取的行动

| 优先级 | 行动 | 预计工时 | 责任人 |
|:---|:---|:---|:---|
| **P0** | 在 SOP 中明确接口 Schema 版本命名规范（废弃 v1/v2/v3 乱用） | 0.5h | 内容专家 |
| **P0** | 统一 cafa_cards.json 字段命名（`pack_id` → `package_id`）并重部署 | 0.5h | PT-004 |
| **P1** | ImportService 增加 `interface_version` 字段读取（向后兼容 v3） | 2h | PT-RUJ |
| **P1** | 科目前缀映射从 hardcoded → JSON 配置文件 | 2h | PT-RUJ |
| **P2** | 标准化 KB→Cards 转换工具（含 kb_lineage） | 4h | PT-037 |
| **P2** | SOP 中补充 interface_version 和 KB 版本管理的规范章节 | 1h | 内容专家 |
