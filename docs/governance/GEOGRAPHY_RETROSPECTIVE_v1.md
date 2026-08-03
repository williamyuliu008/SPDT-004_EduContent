# 地理科目内容开发复盘报告
> **日期**：2026-08-01
> **项目**：地理山河系列（GEO_SHANHE_SERIES）→ 入境 App 导入
> **执行流**：Phase 1（M0/M1/M2）→ App 集成 → v13 部署
> **版本**：v1.0

---

## 一、执行过程回顾

### 1.1 管线执行（M0/M1/M2）

| 阶段 | 执行结果 | 关键数据 |
|:---|:---|:---|
| **M0 入口判别** | ✅ 适用 | C1=0.6 / C2=0.7 / C3=0.8 / C4=0.9（空间数据项偏低） |
| **M1 元数据生成** | ✅ 完成 | 16 条链，206 个知识点，3 个子模块 |
| **M2 质量校准** | ⚠️ Mock 模式 | 23 条代表性条目，23/23 通过（无真实 API 验证） |
| **KB JSON 生成** | ✅ 完成 | `kb_vocab.json`，206 条，JSON 内部引号修复 |

### 1.2 App 集成过程

| 步骤 | 结果 | 说明 |
|:---|:---|:---|
| `geo_cards.json` 初版生成 | ✅ | 32 张卡（16 链 × 2），16KB |
| ImportService.ets 修改 | ✅ | 新增 `inferSubject()` 和 `getGeographyDisplayTitle()` |
| ImportPage.ets 修改 | ✅ | 新增"一键导入地理山河"按钮 |
| Index.ets / ChainListPage.ets | ✅ | 地理入口激活 + 链排序修复 |
| v10 部署 | ✅ | 首次地理集成 |
| **geo_cards.json 损坏** | ❌ | v11/v12 持续存在编码问题 |
| **v13 重建** | ✅ | 从 meta.json 彻底重建，部署成功 |

---

## 二、问题根因分析

### 2.1 编码损坏（阻断性问题）

**症状**：
- JSON 解析失败：`Invalid control character at line 13 column 139 (char 467)`
- App 导入时报"读取失败"
- 部分中文字符显示为乱码（如 `鍦扮悊灞辨渤绯诲垪`）

**根因**：PowerShell 与 Python 混用导致编码污染：
1. Python 生成的 UTF-8 JSON 被 PowerShell 管道处理
2. PowerShell 默认行为将 `\r\n` 写入文件，但 `\r` 字符也意外残留在字符串值内（破坏了 JSON 语义）
3. Python `json.loads()` 对控制字符 `\r`（0x0D）的严格校验导致解析失败

**触发路径**（推测）：
```
Python json.dumps() 
  → PowerShell 管道（stdout）
  → PowerShell 重定向写入
  → 文件包含意外的 \r 在字符串内容中
  → App 读取失败
```

**教训**：**JSON 文件的读写必须在 Python 内部完成，不得跨 PowerShell 管道**。

### 2.2 M2 Mock 模式的隐蔽风险

M2 阶段没有真实 API（`DEEPSEEK_API_KEY` 未设置），全程 23/23 条目直接通过，信任等级全是 C（无 E/D）。

**潜在风险**：
- 数值类知识条目（如黄河年均输沙量 35 亿吨、长江全长 6397km）未经验证
- 地理数据对精确数值极为敏感——误判一个数量级即完全错误
- Mock 模式下的"C 级信任 = 直接接受"掩盖了潜在的数值错误

### 2.3 App 集成流程缺失（最大 SOP 缺口）

CGMPipeline SOP v1.1 中：
- Stage 3 "Step 8：发布 metadata.json" 仅描述视频包发布
- **没有任何关于 rawfile JSON 卡片包（`_cards.json`）的生成规范**
- 地理山河的 32 张卡是"手工生成 + 手动修复"，没有 SOP 约束

---

## 三、SOP 缺口清单

| # | 缺口 | 影响 | 建议 |
|:---|:---|:---|:---|
| **G1** | SOP §2.5 地理科目 App 映射标注"TBD"，从未补充 | 新科目 App 集成人均需自行摸索 | 补充地理科目的 chain_id 前缀规范（`GEO_山河_` / `GEO_人地_` / `GEO_区域_`）和 16 条链标题 map |
| **G2** | SOP 无 rawfile JSON 卡片包的生成规范 | 每次新科目都从头摸索，无检查点 | 新增 §4.3 App 导入卡片包规范（含 geo_cards.json 格式模板） |
| **G3** | SOP 无 JSON 文件编码安全规范 | 跨工具读写导致 BOM/控制字符问题 | 补充：**JSON 文件全程 Python 读写，不得经 PowerShell 管道；部署前强制运行 `JSON.parse()` + BOM 检查** |
| **G4** | M2 Mock 模式未在 audit_log 中标注 | 质量报告失真，后续无法追溯"哪些条目是真实校准" | audit_log 增加 `calibration_mode: "mock" / "live"` 字段；Mock 模式结果须在报告中醒目提示 |
| **G5** | 地理 M0 的 C1/C2 偏低（C1=0.6/C2=0.7）未触发特殊处理 | 空间数据类知识条目在 App 中的视觉呈现未做差异化适配 | M0 报告对 C1<0.8 的科目，应标注"需 M2 视觉增强建议" |
| **G6** | 无 App 集成前的预验证清单 | 依赖人工点击测试才发现问题，浪费构建次数 | 新增 **App 集成前检查清单**：JSON 有效性 → BOM 检查 → 字段完整性 → App 构建 → 设备验证 |

---

## 四、做得好的经验（提炼）

### E1：元数据结构先行

`meta.json` 的 3 层结构（modules → chains → knowledge_points）让后续所有工作都有据可查。即使 geo_cards.json 彻底损坏，从 meta.json 重建只用了 200+ 行 Python 代码，10 分钟。

> **提炼**：每个科目包必须有 `meta.json` 作为单一数据源（Single Source of Truth）。

### E2：ImportService 的可扩展性设计

`inferSubject()` 和 `getGeographyDisplayTitle()` 的函数式设计，新增科目只需添加几个 `startsWith()` 判断和数组映射，无需改动核心逻辑。

> **提炼**：App Import 层应遵循**扩展优先于修改**原则，新科目接入成本 ≤ 新增 2 个函数。

### E3：ChainListPage 的通用排序

用 `parseInt(title)` 提取数字前缀排序，同时覆盖了书法（墨骨山河 + CAFA）和地理（1_~16_），无需为每个科目单独写排序逻辑。

> **提炼**：序号前缀（`N_`）是跨科目链排序的最小公约数方案。

### E4：Build 与 Deploy 分离

`build-cli.ps1` 和手动 `hdc install` 分离，使得 geo_cards.json 修复后只需增量构建（1ms 的 `UP-TO-DATE`），无需完整重编译。

---

## 五、SOP 优化建议（具体修改）

### 5.1 CGMPipeline SOP v1.1 → v1.2 改动建议

#### §2.5 App 学科映射（补充地理）

```markdown
| `地理` | 地理 | `GEO_山河_*` / `GEO_人地_*` / `GEO_区域_*` |
```

新增脚注：
> **地理科目标题映射**（16 条链，≤10 字）：
> ```
> GEO_山河_黄河 → 1_黄河·九曲     GEO_山河_长江 → 2_长江·三峡
> GEO_山河_淮河 → 3_淮河         GEO_山河_珠江 → 4_珠江三角洲
> GEO_山河_松花江 → 5_松花江     GEO_山河_塔里木 → 6_塔里木
> GEO_山河_青藏 → 7_青藏高原     GEO_山河_天山 → 8_天山
> GEO_人地_人口迁移 → 9_人口迁移
> GEO_人地_产业转移 → 10_产业转移
> GEO_人地_农业地域 → 11_农业地域
> GEO_人地_可持续发展 → 12_可持续发展
> GEO_区域_北方地区 → 13_北方地区
> GEO_区域_南方地区 → 14_南方地区
> GEO_区域_西北地区 → 15_西北地区
> GEO_区域_青藏地区 → 16_青藏地区
> ```
> App ImportService.ets 维护此映射表，chain_title 字段以 `meta.json` 中的 `chain_name` 为准（App 显示标题由映射表注入）。

#### 新增 §4.3 App 导入卡片包规范

```markdown
### 4.3 App 导入卡片包规范（Stage 2 产出）

> **适用场景**：科目内容包需要导入入境 App（非视频类内容包）
> **产出**：`{pack_id}_cards.json` → App `rawfile/` 目录
> **格式**：见下方 Schema

**Schema**（geo_cards v3）：
```json
{
  "package_id": "GEO_SHANHE_SERIES",
  "package_title": "地理山河系列",
  "schema_version": "v3",
  "node_cards": [ /* 见下方 Card Schema */ ],
  "total_cards": 32,
  "total_chains": 16
}
```

**Card Schema**：
```json
{
  "card_id": "GEO_NAT_001",       // 唯一 ID
  "chain_id": "GEO_山河_黄河",     // 与 meta.json 一致
  "chain_title": "黄河·九曲入海",  // meta.json 中的 chain_name
  "card_type": "node | strategy",  // node=节点卡, strategy=策略卡
  "chain_role": "pivot | result",  // pivot=支点, result=结果
  "front": "黄河的泥沙从哪里来...",  // 正面问题（≤50字）
  "back_core": "黄河中游流经...",     // 核心答案（≤200字）
  "back_detail": "...",             // 详细说明（可选）
  "tags": ["黄河", "水土流失"]       // 标签（≤4个）
}
```

**生成流程**：
```
① meta.json（单一数据源）
    ↓（Python 脚本：build_cards_from_meta.py）
② {pack_id}_cards.json（clean UTF-8）
    ↓
③ JSON 有效性验证（python -c "import json; json.load(open('xxx','r',encoding='utf-8'))"）
    ↓
④ BOM/控制字符检查（无 BOM，无 \r 在字符串内容内）
    ↓
⑤ 复制到 App rawfile/ 目录
    ↓
⑥ HVigor 增量构建 + hdc 部署
    ↓
⑦ App 导入验证（手动）
```

**编码安全铁律**：
> ⚠️ **JSON 文件全程 Python 读写，任何步骤不得经 PowerShell 管道！**
> - 用 `python -c "..."` 验证，不要 `Get-Content | python`
> - 写入用 `open(path, 'w', encoding='utf-8')`，**不用** PowerShell `Set-Content`
> - 部署前必须运行 BOM 检测脚本

#### 新增 §6.7 App 集成前检查清单

```markdown
## 六、App 集成前检查清单（每次部署前必跑）

- [ ] **JSON 有效性**：`python -c "import json; json.load(open('path','r',encoding='utf-8'))"`
- [ ] **BOM 检测**：`python -c "f=open('path','rb'); print(f.read(3)==b'\\xef\\xbb\\xbf')"`
- [ ] **控制字符**：`python -c "import re; raw=open('path','r',encoding='utf-8').read(); bad=[c for c in raw if ord(c)<32 and c not in '\\n\\t']; print(len(bad))"` → 期望 0
- [ ] **chain_id 一致性**：rawfile JSON 中的 chain_id 与 meta.json 完全一致
- [ ] **title 映射检查**：ImportService.ets 中的 `getXxxDisplayTitle()` map 与 meta.json chain_id 一一对应
- [ ] **HVigor 增量构建**：确认无错误
- [ ] **设备安装验证**：`hdc install` → `hdc shell aa start` 成功
- [ ] **App 导入测试**：点击"一键导入" → 检查 HiLog 无 ERROR
```

### 5.2 PT-037 SPEC.md 改动建议

在 §3.3 M2 质量校准部分补充：

```markdown
**Mock 模式风险提示**：

当 DEEPSEEK_API_KEY 未设置时，校准器运行 Mock 模式：
- 所有条目默认 C 级信任，直接接受
- 数值类条目（流量/面积/年份）未经验证
- 地理/理科类科目数值精度要求高，**强烈建议使用真实 API**

Mock 模式 audit_log 必须包含：
```json
{
  "calibration_mode": "mock",
  "warning": "数值类条目未经验证，请人工复核关键数据"
}
```
```

---

## 六、后续改进优先级

| 优先级 | 改进项 | 影响 |
|:---|:---|:---|
| **P0** | App 集成前 JSON 自动化检查脚本（防止再次编码损坏） | 阻断性问题修复 |
| **P0** | SOP §2.5 补充地理 App 映射 | 新科目可自助接入 |
| **P1** | SOP 新增 §4.3 卡片包生成规范 | 消除手工摸索 |
| **P1** | M2 audit_log 增加 `calibration_mode` 字段 | 质量报告可追溯 |
| **P2** | 地理 M2 真实 API 校准（关键数值条目） | 提升知识准确性 |
| **P2** | SOP 新增 §6.7 App 集成前检查清单 | 减少构建-部署迭代 |

---

## 七、总结

地理山河系列是 SOP v1.1 之后的第一个新科目接入。从 M0 到 App 展示全流程打通，验证了管线框架的基本可行性，但也暴露了 **App 集成层是 SOP 的盲区**——Stage 2 的输出规范止步于"发布 metadata.json"，完全没有覆盖 rawfile JSON 卡片包这一最常见的 App 内容格式。

核心经验一句话：**管线的前半段（SOP 覆盖区）规范清晰，后半段（App 接入区）基本靠经验。** v1.2 的重点应是"向后延伸 SOP 覆盖区"。
