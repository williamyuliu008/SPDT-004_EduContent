# TextExperience 内容缝合管线 · SOP

> **版本**：v1.1 | **日期**：2026-07-15 | **基于**：PT-038 书法史+古代史+世界史项目实践

---

## 零、核心理念（必须时刻对照）

> **"用学科知识本身的魅力征服读者，而非用学科之外的媚俗手段迎合观众。"**

这是整个管线的价值锚。所有决策——选什么材料、怎么写叙事、加什么多媒体形式——都以这个原则为基准。

### 这个原则的三层含义

**第一层：知识的内在脉络就是最好的叙事逻辑**
历史本身就有因果逻辑、时间逻辑、对比逻辑。好的叙事设计，是让这种内在逻辑自己浮现出来，而不是在知识点外面套一个"故事壳"。
打个比方：好的悬疑片不是"讲一个道理+套一些案件"，而是"案件本身就是道理"。历史剧本也一样——不是因为加了对白才有趣，而是历史本身已经足够戏剧性。

**第二层：好奇心是最强的学习动力，好奇心需要被正确激发**
不是"这个知识点很重要"能激发好奇心，而是"这个现象和我以为的不一样"能激发好奇心。
好的内容设计 = 找到学习者已有的认知和真实知识之间的落差 → 用叙事把这个落差填上。
这个过程本身让人上瘾。

**第三层：叙事的目的是认知，不服务于流量**
不要用"梗"、"网络用语"、"过度戏剧化"来制造趣味——这些东西短期有效，长期损害内容的严肃性和可信度。
趣味性来自于知识本身的有趣：因果链条的反直觉性、历史人物的处境复杂性、不同观点的碰撞张力。

### 三层质量标准

| 层级 | 维度 | 底线要求 |
|---|---|---|
| 底层 | **知识完备性 + 准确性** | 所有时间/数据/事件必须有史料依据；关键结论双模型审计 |
| 中层 | **叙事逻辑性 + 趣味性** | 核心问题必须真实、引人；因果链条必须清晰；不强行煽情/媚俗 |
| 顶层 | **多媒体便捷性** | 同源内容多格式输出；匹配不同使用场景（听/读/做） |

---


```
输入：领域知识 + 考点标注
         │
         ▼
┌─────────────────────┐
│  Phase 0  设计层     │  meta.json / 知识链规划
│  Phase 1  数据层     │  episode Python 数据文件
│  Phase 2  剧本层     │  四幕微剧本 JSON
│  Phase 3  卡片层     │  自动派生 节点卡+心法卡+链卡
│  Phase 4  出版层     │  电子书 DOCX/MD
│  Phase 5  音频层     │  广播剧 MP3+BGM混音
│  Phase 6  归档层     │  PT-038 存档 + 注册表写入
└─────────────────────┘
         │
         ▼
输出：电子书 + 知识链卡片包 + 广播剧音频
```

**核心原则**：
- 同源知识，多格式输出，一处改动全链路同步
- Python 数据文件（`get_data()`）是唯一真相源
- JSON 剧本从 Python 数据派生，音频从剧本派生

---

## 二、项目目录结构

每个内容包（Content Pack）遵循以下结构：

```
PT-038_TextExperience/
├── meta.json                    ← 包顶层元数据（必须）
├── [pack_name]/                  ← 包名，如「配置包_cafa_calligraphy_2026」
│   ├── meta.json                ← 包配置
│   ├── knowledge/               ← 静态知识库
│   │   ├── kb_vocab.json        ← 核心词汇表（star5 标注）
│   │   └── ability_list.json    ← 能力点清单
│   ├── prompts/                 ← 提示词模板
│   │   └── cross_pack_links.json
│   └── scripts/                  ← 所有脚本 + 生成物
│       ├── [ep0X_topic.py]      ← episode 数据文件（Python get_data()）
│       ├── [generate_ebook.py]  ← 电子书生成器
│       ├── [micro_dramas.json]  ← 四幕微剧本
│       ├── *.docx / *.md        ← 电子书生成物
│       └── *.json               ← 剧本/脚本
├── [series_v1]/                  ← 卷一，结构同上
├── [series_v2]/
├── [series_v3]/
├── ebooks/                       ← 所有卷电子书汇总（正式存档）
├── audio/                        ← 所有音频文件（正式存档）
├── cards/                        ← 所有卡片包（正式存档）
└── docs/                         ← 设计文档、SOP、索引
```

**命名规范**：
- 目录名：中文，无空格，用下划线或连字符
- 文件名：`<项目>_<卷>_<集>_<标题>.<格式>`（如 `古史_v3_ep01_天朝崩塌.py`）
- Python 函数：`get_data()`，无参数，无全局状态

---

## 三、Phase 0 · 设计层

### 0.1 创建包元数据（meta.json）

每个包第一件事是写 `meta.json`，这是后续所有工作的锚点。

```json
{
  "pack_id": "example_pack_v1",
  "pack_name": "卷一·标题",
  "series": "系列名",
  "series_subtitle": "副标题（时代范围）",
  "volume": 1,
  "total_episodes": 6,
  "time_span": { "start": 1840, "end": 1949 },
  "episodes": [
    {
      "ep": 1,
      "title": "第1集标题",
      "subtitle": "副标题",
      "time_period": "1840-1864",
      "time_anchor": "核心事件锚点",
      "core_historical_question": "本集要回答的核心问题",
      "knowledge_chains": ["chain_id：链名称"]
    }
  ],
  "main_line": "主线脉络一句话",
  "cross_volume_links": { "note": "与前卷/后卷的衔接" }
}
```

### 0.2 知识链规划（在 meta.json 中）

**必须提前规划的知识链**：
- 每集 2-4 条 `chain_id`
- chain_id 格式：`<类型>_<朝代/时代>_<序号>`
  - `CHAIN_近代危机_01`（危机-原因）
  - `CHAIN_近代探索_01`（探索-变革）
  - `CHAIN_现代建国_01`（建国-制度）
- 每条链需标注：`原因类` / `影响类` / `变革类` / `制度类` / `概念类`

**考点权重标注**：
- `★★★★★` 高频考点（必须掌握，优先出卡）
- `★★★★` 中频考点
- `★★★` 基础考点

---

## 四、Phase 1 · 数据层

### 4.1 Python Episode 数据文件

**文件**：`scripts/<项目>_ep0X_<标题>.py`

**必须使用 `get_data()` 函数**，禁止用 JSON（JSON 多行字符串在 Python 中非法）。

```python
"""
<项目名> · 第X集
<标题>：<副标题>
时间锚点：<核心事件>
核心问题：<本集要回答的问题>
涉及知识链：<chain_id 列表>
"""

def get_data():
    return {
        "ep": 1,
        "series": "系列名",
        "series_subtitle": "系列副标题",
        "title": "集标题",
        "subtitle": "副标题",
        "time_period": "时间跨度",
        "duration": "时长",

        # ============================================================
        # 第一幕：时间线（Timeline）
        # ============================================================
        "timeline": {
            "overview": "本幕总起，2-3段",
            "events": [
                {
                    "year": "1840",
                    "title": "事件标题",
                    "description": "事件描述，50-100字",
                    "significance": "历史意义，30字以内"
                },
                # ... 4-6个事件
            ]
        },

        # ============================================================
        # 第二幕：艺术/专业问题
        # ============================================================
        "art_question": {
            "theme": "本幕主题",
            "content": "核心内容，3-4段"
        },

        # ============================================================
        # 第三幕：当代回响
        # ============================================================
        "contemporary_echo": {
            "theme": "当代关联主题",
            "content": "连接现代的意义，2-3段"
        },

        # ============================================================
        # 第四幕：春秋笔法
        # ============================================================
        "spring_autumn": {
            "theme": "评判框架主题",
            "content": "历史评价与反思，2-3段"
        },

        # ============================================================
        # 知识链数据（供卡片生成器使用）
        # ============================================================
        "knowledge_chains": [
            {
                "chain_id": "CHAIN_近代危机_01",
                "chain_title": "鸦片战争链",
                "chain_type": "原因类",
                "key_nodes": [
                    {
                        "node_id": "N_危机_01_01",
                        "node_title": "工业革命后的英国",
                        "content": "节点内容",
                        "exam_weight": "★★★★★",
                        "card_type": "节点卡"
                    }
                ],
                "cause_summary": "原因概述",
                "impact_summary": "影响概述",
                "strategy": "学习策略",
                "memorization_tips": "记忆技巧"
            }
        ]
    }
```

### 4.2 最佳实践

- **四幕结构不要写太满**：剧本杀式微剧本每幕预留 400-600 字，留给 AI 演绎空间
- **时间线事件控制在 5-8 个**：太少没厚度，太多流水账
- **每个节点必须带 `exam_weight`**：★★★★★ 的节点优先进入卡片生成
- **chain_id 在 meta.json → episode .py → 卡片生成器全链路保持一致**

---

## 五、Phase 2 · 剧本层

### 5.1 四幕微剧本格式

**文件**：`scripts/micro_dramas.json`（每包一个汇总文件）+ `scripts/<ep>_micro_drama.json`（每集独立）

```json
{
  "series": "系列名",
  "episodes": [
    {
      "ep": 1,
      "title": "集标题",
      "act_1": {
        "type": "narrative",
        "content": "时间线叙事旁白"
      },
      "act_2": {
        "type": "scripted",
        "scenes": [
          {
            "scene_id": "S01",
            "role": "角色A",
            "content": "对白/独白"
          }
        ]
      },
      "act_3": { "type": "narrative", "content": "当代回响" },
      "act_4": { "type": "narrative", "content": "春秋笔法评注" }
    }
  ]
}
```

### 5.2 剧本生成流程

```
meta.json（知识链规划）
       ↓
episode .py（get_data()）
       ↓
micro_dramas.json（四幕剧本）
       ↓
e-book generator（电子书）
audio narration extractor（音频旁白提取）
card generator（卡片派生）
```

### 5.3 音频旁白提取脚本

```python
# scripts/extract_narration.py（参考古史_v3的extract_narration.py）
# 职责：从 micro_dramas.json 提取所有旁白文本
# 输出：<ep>_narration.txt（纯文本，供 TTS 调用）
```

---

## 六、Phase 3 · 卡片层

### 6.1 卡片自动生成器

**文件**：`scripts/<项目>_卡片_自动生成器.py`

**从 episode .py 的 `knowledge_chains` 自动派生**，无需手动编写每张卡。

```python
def load_all_episodes():
    """加载所有 episode Python 数据"""
    ...

def derive_node_cards(episode):
    """从 key_nodes 派生节点卡"""
    ...

def derive_strategy_cards(chain):
    """按 chain_type 批量生成心法卡"""
    # 原因类 → 为什么会发生？
    # 影响类 → 产生了什么后果？
    # 变革类 → 变革的关键转折点？
    # 制度类 → 制度设计逻辑？
    ...

def derive_chain_card(chain):
    """生成链卡（chain overview）"""
    ...

def generate_all():
    # 输出：JSON + Anki CSV
    ...
```

### 6.2 三型卡片规范

| 卡片类型 | 来源 | 数量/链 | 核心功能 |
|---|---|---|---|
| 节点卡 | key_nodes | 4-6张/链 | 原子事实，名词解释型 |
| 心法卡 | chain_type 策略模板 | 2-4张/链 | 操作型知识，原因/影响分析 |
| 链卡 | chain metadata | 1张/链 | 全链概览，跨节点关系 |

**card_id 格式**：
- 节点卡：`H_<时代>_<链号>_<节点号>`（如 `H_近代_01_01`）
- 心法卡：`S_<时代>_<链号>_<序号>`（如 `S_近代_01_01`）
- 链卡：`L_<时代>_<链号>`（如 `L_近代_01`）

---

## 七、Phase 4 · 出版层

### 7.1 电子书生成器

**文件**：`scripts/generate_<项目>_ebook.py`

```python
def generate_ebook(episodes):
    # 1. 加载所有 episode Python 数据
    # 2. 按四幕结构组装 MD 文本
    # 3. 生成 appendices（知识链索引 + 考点清单）
    # 4. 输出：
    #    - <项目>_电子书.md
    #    - <项目>_电子书.docx（用 python-docx 转换）
```

### 7.2 输出路径规则

**正式生成物必须放在两层位置**：

| 文件类型 | 第一位置（包内） | 第二位置（PT-038汇总） |
|---|---|---|
| episode .py | `scripts/` | — |
| micro_dramas.json | `scripts/` | — |
| 电子书 | `scripts/` | `PT-038/ebooks/` |
| 卡片包 | `scripts/` | `PT-038/cards/` |
| 音频 | `audio/` | `PT-038/audio/` |

**注意**：第一位置的 `scripts/` 内电子书是开发版；PT-038 根目录的 `ebooks/` 是正式存档版。

---

## 八、Phase 5 · 音频层

### 8.1 音频规格

| 参数 | 值 | 说明 |
|---|---|---|
| 音色 | `male-qn-badao` | 霸道青年，适合戏剧性强的叙事 |
| BGM权重 | `0.15` | amix 权重 `1.2 0.15`（旁白:音乐） |
| 语速 | `0.92` | 正常偏慢，便于跟听 |
| 格式 | MP3 192kbps | `ffmpeg -ar 44100 -ac 2 -b:a 192k` |

### 8.2 混音命令

```bash
# ffmpeg 混音（amix 方式，BGM 更自然，不会在旁白停顿时突显）
ffmpeg -i narration.mp3 -i bgm.mp3 \
  -filter_complex "amix=inputs=2:duration=shortest:weights=1.2 0.15" \
  -ar 44100 -ac 2 -b:a 192k output.mp3

# 备选：crossfade 方式（旁白间隙处渐入渐出，更平滑）
ffmpeg -i narration.mp3 -i bgm.mp3 \
  -filter_complex "acrossfade=d=1:c1=tri:c2=tri" \
  -ar 44100 -ac 2 -b:a 192k output.mp3
```

### 8.3 音频文件命名

```
<Ep序号>_<标题>_<版本>.mp3
Ep01_天朝崩塌_完整版_霸道青年.mp3    ← 完整版（时间线+当代回响）
Ep01_天朝崩塌_精简版.mp3             ← 精简版（6-8分钟）
对比_霸道青年音色_卷首语.mp3          ← 音色对比样例
```

---

## 九、Phase 6 · 归档层

### 9.1 PT-038 注册表写入

完成每个包后，在 `pdt-registry.yaml` 中写入/更新注册信息：

```yaml
content_packages:
  - pdt_sub_id: PT-038-X         # 新包编号
    name: <pack_id>
    name_zh: <中文名>
    subject: <科目/领域>
    episodes: <集数>
    knowledge_chains: <链数>      # 如有
    cards: <卡片数>                # 如有
    status: active
```

### 9.2 目录创建顺序

```bash
# 首次建立新 PDT 项目时
New-Item -ItemType Directory -Path "D:\92_products\SPDT-004_EduContent\PT-038_TextExperience\ebooks"
New-Item -ItemType Directory -Path "D:\92_products\SPDT-004_EduContent\PT-038_TextExperience\audio"
New-Item -ItemType Directory -Path "D:\92_products\SPDT-004_EduContent\PT-038_TextExperience\cards"
New-Item -ItemType Directory -Path "D:\92_products\SPDT-004_EduContent\PT-038_TextExperience\docs"
```

⚠️ **常见错误**：`New-Item -ItemType File` 会错误创建占位文件。确认用 `PSIsContainer` 检查目录是否真正创建成功。

---

## 十、最佳实践清单

### ✅ 必做

1. **先写 meta.json，再写代码**：知识链规划是所有后续工作的锚点
2. **Python get_data() 代替 JSON**：避免字符串转义地狱
3. **卡片从 episode 数据自动派生**：不要手动写卡，手动写必出错漏
4. **生成物放在两个位置**：包内 scripts/（开发版）+ PT-038 根目录（正式版）
5. **chain_id 全链路一致**：meta.json → episode .py → 卡片生成器 → 50链索引
6. **BGM 权重 0.15**：实测 0.4 太吵，0.1 太弱，0.15 是黄金值
7. **霸道青年音色 `male-qn-badao`**：比精英青年音色更有戏剧张力，适合历史叙事

### ❌ 禁做

1. **不用 JSON 存多行字符串**（Python 中非法）
2. **不在 scripts/ 留调试文件**（`debug_*.py`、`inspect_*.py` 完成后删除）
3. **不直接在 PT-038 根目录操作**（在包内开发，成熟后同步到根目录）
4. **不用 bash 语法**（Windows 环境统一用 PowerShell）
5. **不删除生成物到垃圾桶以外的地方**：用 `mavis-trash`，不用 `rm` / `Remove-Item`

---

## 十一、常见问题处理

| 问题 | 原因 | 解决方案 |
|---|---|---|
| Copy-Item 报错"找不到路径" | 目标目录是占位假文件（非真实目录） | 用 `Get-Item` 检查 `PSIsContainer`，假文件用 `mavis-trash` 删除后重建 |
| ffmpeg 挂起不返回 | 命令需要 TTY/交互式输入 | 检查是否需要 `--no-wait` / device-code 模式；用 `2>&1 \| Select-Object -Last N` 限制输出 |
| 音频文件大小异常（几KB） | TTS 生成失败但空文件被创建 | 检查 API 限速/Quota；添加文件大小校验 `< 50KB 则重新生成` |
| 卡片数量不对 | key_nodes 数量与预期不符 | 在生成器中添加 `assert card_count > 0` 断言 |
| meta.json 和 episode .py 的 chain_id 不一致 | 多次修改导致漂移 | 用 `grep -r "CHAIN_" scripts/` 扫描全量 chain_id，对比 meta.json |

---

## 十二、新领域接入清单

当接入一个新领域（如法考/思政/非遗）时，快速检查清单：

```
□ 1. 创建 <new_pack>/meta.json（知识链规划 + 考点权重）
□ 2. 编写 episode .py（get_data() 格式）
□ 3. 运行 micro_dramas.json 生成
□ 4. 运行卡片自动生成器（检查 card_count）
□ 5. 运行电子书生成器（检查 MD/DOCX 输出）
□ 6. 生成音频旁白文本 + TTS + BGM混音
□ 7. 同步到 PT-038/ebooks/、audio/、cards/
□ 8. 更新 pdt-registry.yaml
□ 9. 清理调试文件
```

---

## 十三、CGM 内容质量管理规则（审计标准）

> **目标**：在规模生产的同时，确保内容质量不滑坡。每集内容上线前，必须通过以下三层审计。

### 审计A：历史准确性（底线，必须通过）

```
□ 时间线事件的年份、事件名称、历史意义与主流史学共识一致
□ 关键数据（伤亡人数、条约条款、领土变更）有明确史料支撑
□ 涉及争议性历史结论（如当代回响）必须标注"学界存在不同观点"
□ 所有★★★以上考点节点必须有明确的史料来源路径
□ 禁止：无中生有、移花接木、以今律古（用现代价值观强加于历史人物）
```

**审计方式**：双模型交叉验证（用第二个模型重新生成同一段，对比关键事实是否一致）

### 审计B：知识链质量（核心价值，差异化标准）

```
□ 每条 chain 只有一个核心因果逻辑——能用一句话说清楚这条链的主题
□ chain_type 判断准确：
    - 原因类：为什么发生？根本原因 + 直接原因 + 触发条件
    - 影响类：产生了什么？短期影响 + 长期影响 + 连锁反应
    - 变革类：关键转折点是什么？变革前状态 → 触发机制 → 变革后状态
□ 心法卡 front（问题）必须是主动检索式：
    - ✅ "为何X事件导致了Y结果？"
    - ❌ "X事件是什么？"
□ 节点卡 back（答案）必须包含对比或反例：
    - ✅ "科举制的进步性在于……（但同期欧洲仍采用……）"
    - ❌ "科举制是选拔官员的制度。"
□ ★★★★★考点节点必须出现在至少一种卡片类型中
```

### 审计C：叙事体验（感受层面，主观+客观结合）

```
□ 第二幕"核心问题"是否为真实学术争议：
    - ✅ "为何洋务运动技术引进失败了，而明治维新制度变革成功了？"
    - ❌ "洋务运动失败了，请回答失败原因。"
□ 当代回响是否具体可验证（非强行升华）：
    - ✅ "一战后德国《凡尔赛和约》的赔款条款，在1923年导致了恶性通货膨胀，"
         "这一机制与今天某些国家的债务危机有相似的结构性逻辑。"
    - ❌ "从一战我们学到，要珍惜和平。"
□ 春秋笔法是否呈现多元史学观点：
    - 每集至少呈现两个不同的史学评价视角（如传统观点 vs 修正史观）
□ 叙事中不使用媚俗手段：
    - ❌ 网络用语（"太燃了"、"绝绝子"等）
    - ❌ 无根据的戏剧化细节（"他猛地一拍桌子"等主观臆断）
    - ❌ 刻意煽情的描写（历史本身的重量已经足够）
□ 音频旁白转写文本在场景转换处有情感锚点提示（如"[停顿]"、"[低沉]"）
```

### 审计触发条件

| 条件 | 必须通过 |
|---|---|
| 新科目第一集 | 全部三层审计 |
| 已有科目新集 | 审计A + 审计B（简化版：快速扫描） |
| 大规模修改（改动核心史实） | 全部三层 |
| 小修小改（文字润色） | 审计A 自查 |

---


| 文件 | 位置 | 用途 |
|---|---|---|
| `meta.json` | 各包根目录 | 包顶层元数据，知识链规划的源头 |
| `古史_v3_ep0X_*.py` | 古史_v3/scripts/ | 卷三 episode 数据文件（含知识链） |
| `古史_v3_卡片_自动生成器.py` | 古史_v3/scripts/ | 129张卡片自动派生 |
| `generate_v3_ebook.py` | 古史_v3/scripts/ | 卷三电子书生成器 |
| `extract_narration.py` | 古史_v3/scripts/ | 从剧本提取旁白文本 |
| `古史_v3_50链索引.md` | 古史_v3/scripts/ | 全50链与集数的映射表 |
| `pdt-registry.yaml` | `D:\92_products\SPDT-004_EduContent/` | PT-038 注册表 |
