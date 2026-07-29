# CGM 内容生产管线 · 标准操作规程 v1.1
> **版本**：v1.1 | **日期**：2026-07-19 | **状态**：在用
> **本次更新**：新增第六章（内容包版本生命周期与发布审批规程），新增第七章（质量门禁自动化脚本清单）
> **定位**：内容团队唯一操作入口，新成员阅读本文即可开始生产。

---

## 一、管线全景

```
┌─────────────────────────────────────────────────────────────────┐
│                      CGM · 三阶段管线                              │
│                                                                 │
│  Stage 1          Stage 2              Stage 3               │
│  知识库构建   ──▶  知识管理与叙事   ──▶  文本及音视频生成         │
│                                                                 │
│  PT-037 KB        PT-038 TextExp       PT-VFX VideoFactory     │
│                                                                 │
│  结构化文档        微剧本 JSON              MP4 节目              │
│  标签体系         知识链 JSON              metadata.json        │
│  能力列表         三型卡片                 (IF-B 协议)           │
│                                                                 │
│  ★ 全局参数贯穿三阶段（章节/学科/系列/标签规范）                  │
└─────────────────────────────────────────────────────────────────┘
```

### 1.1 三阶段职责边界

| 阶段 | 核心任务 | 输入 | 输出 | 责任方 |
|------|----------|------|------|--------|
| **Stage 1** 知识库构建 | 原始知识结构化 | 教材/考纲/文献 | KB JSON（词汇/标签/能力） | 内容专家 |
| **Stage 2** 知识管理与叙事 | 链叙事 + 场景分类 | KB JSON | micro_drama JSON + chain_meta JSON + 三型卡片 | 编剧 + 内容专家 |
| **Stage 3** 文本及音视频节目 | 音视频节目生成 | Stage 2 输出 | MP4 + IF-B metadata | 制作工程师 |

---

## 二、全局参数集（Global Params）

> 所有三阶段共享，修改需同步更新本节。所有内容包在发布前必须确认以下参数。

### 2.1 标识符规范

| 参数 | 格式 | 示例 | 说明 |
|------|------|------|------|
| `SERIES_ID` | `大写英文+数字` | `墨骨山河`、`AI实务` | 系列唯一标识，跨包不变 |
| `EPISODE_ID` | `{SERIES_ID}_ep{NN}` | `墨骨山河_ep01` | 集编号，从01开始 |
| `SUBJECT` | `中文科目名` | `书法`、`古诗文`、`历史` | App 学科入口对应 |
| `CHAIN_ID` | `{类型}_{专题}_{编号}` | `CHAIN_实词_Top20_01`、`GAOKAO_EP01` | 知识链唯一ID |
| `CARD_ID` | `{前缀}_{NNN}` | `GAOKAO_P001`、`EP01_N003` | 卡片唯一ID |
| `PKG_VERSION` | `vMAJOR.MINOR.PATCH` | `v1.0.0` | 内容包版本（见第六章） |

### 2.2 五蕴标签规范（Five Skandha）

内容侧（Stage 2）给每个 scene 打标签，Stage 3 制作时必须遵循：

| 蕴 | 标签 | 定义 | 触发条件 |
|----|------|------|----------|
| 色蕴 | `color_base` | 视觉锚点词，≤4个 | 每个 scene 必填 |
| 受蕴 | `sensation` | 情绪类型 | 枚举：curiosity/resonance/solemnity/awe/tension/none |
| 想蕴 | `discrimination` | 认知分别点 | 1个核心区别判断 |
| 行蕴 | `action_prompt` | 输出任务类型 | 枚举：口述/复述/判断/选择/论述 |
| 识蕴 | `recognition_marker` | 检验关键词 | 闭合确认用语 |

### 2.3 认知负载标准（Cognitive Load）

| 指标 | 合格 | 警告 | 不合格（OVERFLOW） |
|------|------|------|--------------------|
| 视觉点数（`visual_points`） | ≤ 4 | 5-6 | > 6 |
| 音频分段（`audio_chunks`） | ≤ 3 | 4-5 | > 5 |
| TTS 时长 | 8-25秒/场景 | 25-40秒 | > 40秒或 < 5秒 |

### 2.4 标签体系（Tags）

Stage 1 产出的标签必须遵循两级结构：

```
#{难度}_{层级}    #难度_初阶 / #难度_中阶 / #难度_高阶
#{类型}           #实词 / #虚词 / #句式 / #书法 / #历史
#{专题}           #秦/书同文 / #安史之乱 / #译篆
#{考频}           #全国卷_高频 / #上海卷_高频
```

**命名规则**：
- 用中文或英文，不用拼音缩写
- 同义词统一（如"文言语法"统一为"句式"）
- 新标签需在 `标签总表.md` 登记，否则 Stage 2 不得引用

### 2.5 App 学科映射

内容包 → App 学科入口的强制映射关系：

| SUBJECT（全大写） | App 入口 | 法定前缀 |
|-----------------|----------|----------|
| `书法` | 书法 | `墨骨山河_` |
| `古诗文` | 古诗文 | `GAOKAO_`、`CHAIN_` |
| `历史` | 历史 | `CHAIN_`（不含GAOKAO/墨骨山河前缀） |
| `地理` | 地理 | （待定义） |
| `政治` | 政治 | （待定义） |

> **强制规则**：内容包导入时，若 chain_id 不含上述任何前缀，默认归入 `HISTORY`。
> 若内容专家有意将链放入其他学科，必须在 chain_meta JSON 中显式声明 `subject` 字段。

---

## 三、Stage 1 · 知识库构建

> **输入**：教材原文 / 考纲 / 参考文献  
> **输出**：KB JSON（词汇库、标签总表、能力列表）  
> **责任**：内容专家  
> **产出位置**：`{course}/kb/` 目录

### 3.1 核心文件

```
kb/
├── kb_vocab.json          # 词汇库（实词/虚词/术语）
├── kb_tags.json           # 标签体系索引
├── kb_abilities.json      # 能力列表（认知层级）
└── kb_meta.json          # 元数据（科目/难度/考频）
```

### 3.2 SOP

**Step 1：确定科目和难度边界**

在 `kb_meta.json` 中明确：
```json
{
  "subject": "古诗文",
  "target_exam": "高考语文",
  "difficulty_range": ["初阶", "中阶"],
  "total_entries_planned": 120
}
```

**Step 2：按义项群提取词汇（非字母序）**

词汇按**语义联想**分组，而非字母序。参考分组：
- 实词：死亡类 / 逃跑类 / 官职变动类 / 言说类 / 时间类
- 虚词：之 / 以 / 其 / 于 / 而（按频率排序）

**Step 3：标签标注**

每个词汇/条目必须标注：
- 难度：`#难度_初阶` / `#难度_中阶` / `#难度_高阶`
- 类型：`#实词` / `#虚词` / `#书法` 等
- 考频：`#全国卷_高频`（凭历史真题统计）

**Step 4：质量自检**

| 检查项 | 合格标准 |
|--------|----------|
| 每个条目有 ≥1 个标签 | 无孤立条目 |
| 标签在 `标签总表.md` 中存在 | 无未登记标签 |
| 词汇释义有课内例句或真题例句 | 避免空洞释义 |
| 同一专题词汇无重复 | 去重检查 |

### 3.3 质量门禁

```
┌─ 门禁 1.1：标签覆盖率 ───────────────────────────────┐
│  检查：kb_vocab.json 中所有条目均有标签                │
│  命令：python tools/check_tag_coverage.py kb/         │
│  阈值：覆盖率 ≥ 95%                                    │
│  结果：< 95% → 打回内容专家补充                       │
└──────────────────────────────────────────────────────┘
┌─ 门禁 1.2：标签一致性 ───────────────────────────────┐
│  检查：所有标签在标签总表中登记                        │
│  命令：python tools/check_tag_registry.py kb/         │
│  结果：发现未登记标签 → 拒绝进入 Stage 2              │
└──────────────────────────────────────────────────────┘
```

---

## 四、Stage 2 · 知识管理与叙事

> **输入**：Stage 1 产出的 KB JSON  
> **输出**：`micro_drama JSON` + `chain_meta JSON` + 三型卡片包 JSON  
> **责任**：编剧 + 内容专家  
> **产出位置**：内容包目录（例：`墨骨山河_配置包/`）

### 4.1 三型卡片规范

| 类型 | 用途 | 核心字段 |
|------|------|----------|
| **节点卡** (`node`) | 知识点正面内容 | `front`（问题/词条）、`back_core`（核心答案） |
| **心法卡** (`strategy`) | 方法/规律总结 | `front`（方法名）、`back_core`（核心逻辑） |
| **链卡** (`chain`) | 认知路径串联 | `front`（链标题）、`back_core`（起点+终点+关卡） |

### 4.2 链叙事（Narrative）编写规范

每条知识链必须有完整叙事文本，包含：

1. **【时代背景】** 时间+空间锚点（1-2句）
2. **【人物/事件】** 核心角色和行动（3-5句）
3. **【知识落点】** 与课标/考点的直接关联（1-2句）

**叙事不要求优美文学性，要求：知识点准确 + 逻辑链清晰 + 可用于 AI 问答上下文**

### 4.3 scene_type 路由规则

| 知识节点类型 | → scene_type | 布局 |
|-------------|--------------|------|
| 时间线/年代 | `timeline` | 时间轴事件流 |
| 因果关系 | `causal_chain` | 原因→结果链 |
| 对比/不同 | `contrast` | 错误 vs 正确 |
| 书法审美/书论 | `concept` | 概念图/板式 |
| 步骤/方法 | `steps` | 分步图 |
| 字形演变 | `word_evolution` | 演变过程图 |
| 引文/名言 | `quote_highlight` | 名言高亮 |
| 仕途+文学双轨 | `dual_track` | 双轨对照 |

### 4.4 五蕴标注 SOP

**每 scene 必须完成以下标注**：

```
色蕴（color_base）：
  → 从 scene 标题/核心内容提取 ≤ 4 个视觉关键词

受蕴（sensation）：
  → 判断情感类型并填入对应枚举值

行蕴（action_prompt）：
  → 明确用户在此 scene 后应完成的任务类型

识蕴（recognition_marker）：
  → 填写一个可检验的闭合关键词/短语
```

### 4.5 质量门禁

```
┌─ 门禁 2.1：知识节点覆盖率 ───────────────────────────┐
│  检查：micro_drama JSON 中 beats 与 KB 节点一一对应   │
│  标准：每个 KB 节点被 ≥ 1 个 beat 覆盖               │
│  结果：覆盖率 < 80% → 补充 beats                      │
└──────────────────────────────────────────────────────┘
┌─ 门禁 2.2：五蕴标注完整性 ─────────────────────────┐
│  检查：所有 scene 的 five_skandha 四个字段非空        │
│  命令：python tools/check_five_skandha.py drama.json │
│  结果：任意字段为空 → 拒绝进入 Stage 3               │
└──────────────────────────────────────────────────────┘
┌─ 门禁 2.3：叙事文本字数 ───────────────────────────┐
│  检查：narrative 字段 ≥ 200 字                       │
│  结果：< 200字 → 打回补充                           │
└──────────────────────────────────────────────────────┘
┌─ 门禁 2.4：subject 字段声明 ───────────────────────┐
│  检查：chain_meta JSON 中所有链显式声明 subject        │
│  结果：发现隐式链（无 subject 字段）→ 拒绝导入 App   │
└──────────────────────────────────────────────────────┘
```

---

## 五、Stage 3 · 文本及音视频节目生成

> **输入**：Stage 2 产出的 micro_drama JSON + chain_meta JSON  
> **输出**：`MP4 视频文件` + `metadata.json`（IF-B 协议）  
> **工具**：PT038_converter / scene_renderer_pillow.py / compose_video.py  
> **责任**：制作工程师  
> **产出位置**：内容包 `rawfile/` 目录（App 内置）或外部导入目录

### 5.1 完整流程

```
Step 1：converter 转换
  micro_drama JSON ──▶ scene JSON × N + manifest.json

Step 2：TTS 音频生成
  scene JSON × N ──▶ audio × N（WAV/MP3）

Step 3：音频时长校验
  ffprobe ──▶ 实际时长 vs 预期时长
  ⚠️ 门禁 3.2：时长偏差 > 15% → 重新编辑旁白

Step 4：scene_renderer 渲染
  scene JSON + audio ──▶ 帧图片序列

Step 5：视频合成
  帧序列 + 音频 ──▶ MP4

Step 6：语义对齐检查 ★ 当前最大短板
  旁白文本 ──▶ 视觉画面 逐 scene 对齐验证
  ⚠️ 门禁 3.3：alignment_confirmed ≠ true → 拒绝发布

Step 7：移动端适配检查
  ⚠️ 门禁 3.4：720p + 1.5Mbps H.264

Step 8：发布 metadata.json
  metadata.json ──▶ rawfile/ 或外部导入目录
```

### 5.2 IF-B 协议（metadata.json Schema）

```json
{
  "schema_version": "1.0.0",
  "package_id": "{SERIES_ID}_v{VER}",
  "series_title": "{中文系列名}",
  "total_episodes": {N},
  "produced_by": "PT-VFX",
  "produced_at": "{ISO8601}",
  "episodes": [
    {
      "ep": 1,
      "title": "{集标题}",
      "subtitle": "{副标题}",
      "video_file": "{文件名.mp4}",
      "duration_seconds": 149.8,
      "resolution": "1080p",
      "bitrate_kbps": 2000,
      "chains": ["{CHAIN_ID}"],
      "scene_timeline": [
        {
          "idx": 0,
          "time": 0.0,
          "scene_name": "{场景描述}",
          "scene_type": "concept",
          "chain_ref": "{CHAIN_ID}",
          "five_skandha": {
            "color_base": ["{关键词1}", "{关键词2}"],
            "action_prompt": "口述/复述",
            "recognition_marker": "{检验关键词}"
          }
        }
      ]
    }
  ]
}
```

### 5.3 TTS 规范

| 参数 | 标准值 | 备注 |
|------|--------|------|
| 语速 | 1.0x（标准） | 书法/古诗文：0.9x（庄重感） |
| 音调 | 0（标准） | 古诗文可用 +2（文雅） |
| 采样率 | 24kHz | 满足 FFmpeg 合成要求 |
| 格式 | MP3 192kbps | HARMONY OS Video 组件兼容性 |
| 每句停顿 | 0.3-0.5秒 | 场景切换处 |

### 5.4 移动端适配规范

| 参数 | 最低标准 | 推荐标准 |
|------|----------|----------|
| 分辨率 | 720p（1280×720） | 1080p（1920×1080） |
| 码率 | 1.5 Mbps | 2.0 Mbps |
| 帧率 | 24fps | 30fps |
| 编码 | H.264 Baseline | H.264 High |
| 音频码率 | 128kbps | 192kbps |
| 文件格式 | MP4 | MP4 |

**验证命令**：
```bash
ffprobe -v error -select_streams v:0 -show_entries stream=codec_name,width,height,bit_rate \
  -of json {video_file}.mp4
```

### 5.5 质量门禁

```
┌─ 门禁 3.1：scene JSON 完整性 ───────────────────────┐
│  检查：manifest 中所有 scene 含 required 字段            │
│  命令：python tools/PT038_converter/converter.py --validate │
│  结果：schema 错误 → 拒绝渲染                         │
└──────────────────────────────────────────────────────┘
┌─ 门禁 3.2：TTS 时长偏差 ───────────────────────────┐
│  检查：实际时长 vs 预期时长 ≤ 15%                      │
│  命令：ffprobe -i scene_01.mp3 -show_entries format=duration │
│  结果：偏差 > 15% → 重新编辑旁白文本                  │
└──────────────────────────────────────────────────────┘
┌─ 门禁 3.3：音画语义对齐 ★ 当前最大短板 ───────────┐
│  检查：每个 scene 的旁白与画面在语义上对齐              │
│  标准：旁白关键句出现时，对应画面元素已呈现             │
│  操作：python tools/check_audio_video_alignment.py --package <pkg_dir> │
│  结果：alignment_confirmed ≠ true → 不得发布           │
│  注：见第六章 §6.4 门禁3.3自动化检查说明             │
└──────────────────────────────────────────────────────┘
┌─ 门禁 3.4：移动端技术规格 ─────────────────────────┐
│  检查：ffprobe 验证分辨率/码率/编码                    │
│  命令：python tools/check_mobile_spec.py episode.mp4   │
│  结果：不满足适配规范 → 转码处理                       │
└──────────────────────────────────────────────────────┘
┌─ 门禁 3.5：scene_timeline 时长一致性 ──────────────┐
│  检查：timeline 各 entry.time 之和 ≤ duration_seconds  │
│  结果：timeline 总时长 > 视频时长 → 数据错误         │
└──────────────────────────────────────────────────────┘
```

---

## 六、内容包版本生命周期与发布审批规程

> **新增章节 v1.1** | **生效日期**：2026-07-19

### 6.1 内容包与接口协议的版本关系

内容包版本（`PKG_VERSION`）与接口协议版本（IF-A/B/C）是**独立管理**的：

| 层次 | 版本字段 | 管理规则 |
|------|----------|----------|
| **接口协议** | `schema_version`（IF-A/B/C 各自由） | 仅大版本升级时变更（如 v1→v2），向后兼容 |
| **内容包** | `package_id` 后缀（如 `_v1.2.0`） | 小版本迭代，接口不变时不升级 schema_version |
| **单集视频** | `ep{NN}` | 可独立发布，内容包整体版本由最高单集版本决定 |

**版本对齐规则**：
- 新增单集 → 内容包 MINOR 版本 +1（`v1.x.0`）
- 内容修正（错字/配音替换/知识点修复）→ PATCH 版本 +1（`v1.2.x`）
- 接口协议不兼容变更 → MAJOR 版本 +1（`v2.0.0`），需同步更新 App 解析代码

### 6.2 内容包生命周期状态机

```
┌─────────┐    Stage 1完成    ┌─────────┐   Stage 2完成   ┌─────────┐
│  DRAFT  │ ──────────────▶  │STAGE1_OK│ ─────────────▶  │STAGE2_OK│
└─────────┘                  └─────────┘                 └─────────┘
     │                            │                           │
     │ 门禁1.1/1.2失败            │ 门禁2.1-2.4失败             │ 门禁3.1-3.5失败
     ▼                            ▼                           ▼
┌─────────┐                  ┌─────────┐                 ┌─────────┐
│ 打回    │                  │ 打回    │                 │ 驳回    │
│(重新提取)│                 │(重写叙事)│                │(重新制作)│
└─────────┘                  └─────────┘                 └─────────┘

┌─────────┐   发布审批通过    ┌─────────┐   App验证通过    ┌─────────┐
│STAGE3_OK│ ──────────────▶  │RELEASED │ ──────────────▶  │LIVE     │
└─────────┘                  └─────────┘                 └─────────┘
     │                            │                           │
     │ 发现严重问题                │ 内容包质量投诉             │ 重大错误
     ▼                            ▼                           ▼
┌──────────────┐            ┌─────────┐                 ┌─────────┐
│ WITHDRAWN    │            │ARCHIVED │                 │ 紧急回滚 │
│ (强制下架)    │            │(内容下架) │                │(→DRAFT) │
└──────────────┘            └─────────┘                 └─────────┘
```

**状态说明**：

| 状态 | 含义 | App可见性 | 审批权限 |
|------|------|----------|----------|
| `DRAFT` | 正在制作中 | ❌ 不可见 | 制作工程师 |
| `STAGE1_OK` | Stage 1 门禁通过 | ❌ 不可见 | 内容专家 |
| `STAGE2_OK` | Stage 2 门禁通过 | ❌ 不可见 | 编剧/内容专家 |
| `STAGE3_OK` | Stage 3 门禁通过 | ❌ 不可见 | 制作工程师 |
| `RELEASED` | 已通过发布审批 | ✅ 可导入 | 内容负责人审批 |
| `LIVE` | App 验证通过 | ✅ 已发布 | 用户可使用 |
| `WITHDRAWN` | 强制下架 | ❌ 移除 | 内容负责人 + 技术负责人 |
| `ARCHIVED` | 归档下架 | ❌ 移除 | 内容负责人 |

### 6.3 发布审批流程

```
内容包完成Stage 3
    │
    ▼
Step 1: 门禁全量检查（自动化）
  python tools/check_package_release.py --package <pkg_dir>
  → 门禁 1.1/1.2/2.1-2.4/3.1-3.5 全部通过
  → 输出: check_report.json（含各门禁通过状态）
    │
    ▼  有任何门禁失败 → 驳回，打回对应Stage重新处理
    │
Step 2: 内容负责人初审
  → 审查内容包是否符合学科定位和难度要求
  → 确认 metadata.json 中 subject 字段映射正确
  → 审查人签字（电子签或文档注释）
    │
    ▼  初审不通过 → 打回 Stage 2/3 修正
    │
Step 3: 试导入验证（手动）
  → 将内容包导入 rujing App
  → 跑通：导入→播放→卡组学习→AI问答 全流程
  → 记录试导入报告
    │
    ▼  试导入失败 → 驳回，附具体错误截图
    │
Step 4: 内容负责人终审
  → 审查试导入报告
  → 确认版本号命名正确（见 §6.1）
  → 确认无敏感内容/版权问题
  → 确认音频旁白与视频内容匹配（Gate 3.3 人工复查）
    │
    ▼  终审不通过 → 打回修正
    │
Step 5: 发布审批签字
  → 填写《内容包发布审批单》（见 §6.5）
  → 内容负责人 + 技术负责人双方签字
  → 审批单存档至内容包目录 /audit/
    │
    ▼
  package_status → RELEASED
    │
    ▼
Step 6: App 集成发布（PT-RUJ）
  → 将内容包纳入 App rawfile/ 或发布到外部导入路径
  → 更新 rawfile_contents.json（如有）
  → 重新构建 App（Hvigor build）
  → 部署到设备验证
    │
    ▼
  package_status → LIVE
```

### 6.4 门禁3.3自动化检查说明

音画语义对齐是**语义层面的主观判断**，无法完全自动化。以下为分级自动化策略：

| 检查层 | 自动化程度 | 检查内容 |
|--------|----------|----------|
| **L1 元数据完整性** | ✅ 全自动 | `scene_timeline` 各字段非空；`five_skandha` 完整 |
| **L2 场景时间逻辑** | ✅ 全自动 | timeline 各 `time` 单调递增；无重叠；总和 ≤ 视频时长 |
| **L3 关键词匹配** | ✅ 全自动 | `color_base` 关键词与 `scene_name` 文本相关性检查 |
| **L4 音频存在性** | ✅ 全自动 | 视频文件存在；时长与 `duration_seconds` 偏差 ≤ 1% |
| **L5 语义对齐人工区** | ❌ 需人工 | 旁白内容是否与画面视觉内容匹配（见门禁3.3） |

> **L5 人工检查触发条件**：
> - 新系列第一集（必须人工审）
> - L1-L4 任一报警（WARNING 级别以上）
> - 音频轨道曾重制（替换后必须重新人工审）
> - 跨学科内容包（如历史+书法、历史+古诗文）

### 6.5 内容包发布审批单

每个内容包发布前填写，存档于 `/audit/release_approval_{pkg_id}_{date}.json`：

```json
{
  "package_id": "墨骨山河_EP06_v1.0.0",
  "pkg_version": "v1.0.0",
  "series_title": "墨骨山河",
  "subject": "书法",
  "episodes": [1],
  "chains": ["墨骨山河_ep06"],
  "total_cards": 17,
  "produced_by": "PT-VFX",
  "produced_at": "2026-07-16T23:32:52+08:00",
  "gate_check_report": {
    "gate_1_1": { "passed": true, "tool": "check_tag_coverage.py" },
    "gate_1_2": { "passed": true, "tool": "check_tag_registry.py" },
    "gate_2_1": { "passed": true, "tool": "check_five_skandha.py" },
    "gate_2_2": { "passed": true, "tool": "check_narrative_length.py" },
    "gate_2_3": { "passed": true, "tool": "check_subject_field.py" },
    "gate_3_1": { "passed": true, "tool": "converter.py --validate" },
    "gate_3_2": { "passed": true, "tool": "check_tts_duration.py" },
    "gate_3_3": {
      "passed": false,
      "tool": "check_audio_video_alignment.py",
      "l1_l4": "PASSED",
      "l5_human_review": {
        "required": true,
        "status": "PENDING",
        "reviewer": null,
        "notes": "ep06音频旁白为颜真卿内容，视频画面为秦始皇/李斯，语义不匹配，音频需重制"
      }
    },
    "gate_3_4": { "passed": true, "tool": "check_mobile_spec.py" },
    "gate_3_5": { "passed": true, "tool": "check_timeline_consistency.py" }
  },
  "trial_import": {
    "status": "PENDING",
    "tester": null,
    "test_date": null,
    "result": null
  },
  "approvals": {
    "初审": { "reviewer": null, "date": null, "signature": null, "notes": null },
    "终审": { "reviewer": null, "date": null, "signature": null, "notes": null }
  },
  "release_status": "PENDING_APPROVAL",
  "audit_file": "audit/release_approval_墨骨山河_EP06_v1.0.0_20260719.json"
}
```

### 6.6 回滚规程

**触发条件**：RELEASED 或 LIVE 包发现以下任一问题：
- 知识性错误（史实/书法/古诗文内容错误）
- 严重音画错位（导致知识理解偏差）
- 版权/合规问题

**回滚操作流程**：

```
Step 1: 问题定性
  ├─ P0（阻断）：立即从 App 移除内容包 → RELEASED→WITHDRAWN
  └─ P1（严重）：从 App 移除 → RELEASED→ARCHIVED

Step 2: 修复处理
  → 在原包目录新建 patch 版本（v{x}.{y}.{z+1}）
  → 修复对应问题（重录音频/修正知识/替换视频）
  → 重新跑门禁全量检查

Step 3: 重新发布审批
  → 新版本包走 §6.3 完整审批流程

Step 4: 原版本归档
  → 原版本目录移入 /archive/{pkg_id}_v{w.z}/
  → App rawfile/ 替换为新版本
  → App 构建+部署
```

**版本替换原则**：同一 `EPISODE_ID` 同一时间只维护一个 LIVE 版本。

---

## 七、质量门禁自动化脚本清单

> **新增章节 v1.1** | **脚本位置**：`{video_factory}/tools/`

| 门禁 | 脚本 | 自动化级别 | 依赖 | 输出 |
|------|------|----------|------|------|
| 门禁 1.1 | `check_tag_coverage.py` | ✅ 全自动 | `kb/*.json` | PASS/FAIL + 覆盖率% |
| 门禁 1.2 | `check_tag_registry.py` | ✅ 全自动 | `kb/*.json` | PASS/FAIL + 未登记标签列表 |
| 门禁 2.2 | `check_five_skandha.py` | ✅ 全自动 | `micro_drama JSON` | PASS/FAIL + 空字段列表 |
| 门禁 2.3 | `check_narrative_length.py` | ✅ 全自动 | `chain_meta JSON` | PASS/FAIL + 字数不足链列表 |
| 门禁 2.4 | `check_subject_field.py` | ✅ 全自动 | `chain_meta JSON` | PASS/FAIL + 缺失subject链列表 |
| 门禁 3.1 | `converter.py --validate` | ✅ 全自动 | `micro_drama JSON` | PASS/FAIL + schema错误 |
| 门禁 3.2 | `check_tts_duration.py` | ✅ 全自动 | 音频文件 + manifest | PASS/FAIL + 偏差>15%文件列表 |
| **门禁 3.3** | **`check_audio_video_alignment.py`** | **⚠️ L1-L4自动 / L5人工** | `metadata.json` + 视频文件 | **L1-L4 PASS/FAIL + L5人工复查清单** |
| 门禁 3.4 | `check_mobile_spec.py` | ✅ 全自动 | MP4 文件 | PASS/FAIL + 不合规参数 |
| 门禁 3.5 | `check_timeline_consistency.py` | ✅ 全自动 | `metadata.json` | PASS/FAIL + 时长不一致集 |
| **包发布审批** | **`check_package_release.py`** | **✅ 全自动（门禁汇总）** | **内容包目录** | **check_report.json（含各门禁状态）** |

### 7.1 check_package_release.py 用法

```bash
# 检查整个内容包（所有门禁）
python tools/check_package_release.py --package "D:/content_pkg/墨骨山河_EP06"

# 输出: check_report.json（标准输出 + JSON报告）
# 退出码: 0=全部通过, 1=有门禁失败, 2=参数错误

# 只跑特定门禁（调试用）
python tools/check_package_release.py --package "..." --gates "3.1,3.3,3.4"

# 生成审批单草稿
python tools/check_package_release.py --package "..." --gen-approval-draft
```

### 7.2 check_audio_video_alignment.py 用法

```bash
# 标准检查（L1-L4 自动，L5 输出人工复查清单）
python tools/check_audio_video_alignment.py \
  --metadata "rawfile/ep06_metadata.json" \
  --video "rawfile/ep01_pipeline.mp4"

# 完整报告（含人工复查状态）
python tools/check_audio_video_alignment.py \
  --metadata "..." \
  --video "..." \
  --verbose

# 输出示例:
# [GATE 3.3] Audio-Video Alignment Check
# L1 元数据完整性: PASS (13/13 scenes完整)
# L2 场景时间逻辑: PASS (无重叠, 时序正确)
# L3 关键词匹配: WARNING (scene[0] color_base与scene_name相关性<0.3)
# L4 音频存在性: PASS (视频存在, 时长149.8s vs metadata 149.8s, 偏差0.0%)
# L5 语义对齐人工区: REQUIRED (音频轨道替换历史, 需人工复查)
# OVERALL: FAIL - L5 human review required before release
```

---

## 八、内容包发布规范

### 8.1 发布前清单

- [ ] Stage 1 → Stage 2 门禁全过（1.1/1.2）
- [ ] Stage 2 → Stage 3 门禁全过（2.1-2.4）
- [ ] Stage 3 → App 发布门禁全过（3.1-3.5）
- [ ] `metadata.json` 纳入版本控制（不得手动编辑）
- [ ] 视频文件 MD5 校验值记录在 metadata 中
- [ ] App 端测试：导入 → 播放 → 卡组学习 → AI 问答 全流程通过
- [ ] 内容包发布审批单（§6.5）完成，双方签字
- [ ] 门禁3.3 L5 人工复查签字

### 8.2 目录结构规范（内容包）

```
{内容包名称}/
├── metadata.json              # IF-B 协议（自动生成，不得手动编辑）
├── audit/                    # 审批存档
│   ├── release_approval_{pkg_id}_{date}.json
│   └── gate_check_report_{date}.json
├── kb/                       # Stage 1 产出
│   ├── kb_vocab.json
│   └── kb_tags.json
├── scripts/                  # Stage 2 产出
│   ├── {episode_id}_micro_drama.json
│   └── {episode_id}_chain_meta.json
├── flashcard/                # 三型卡片包（IF-A 协议）
│   └── {episode_id}_cards.json
└── video/                    # Stage 3 产出
    ├── {episode_id}.mp4
    └── {episode_id}_audio.mp3
```

---

## 九、已知问题与待办

| 编号 | 问题 | 影响 | 状态 | 负责人 |
|------|------|------|------|--------|
| Q1 | ep06 音频旁白与视频画面语义不匹配 | 无法发布 | ✅ **2026-07-19完成：旁白重制+音频合并+Gate3.3全通过** | ✅ Mavis |
| Q2 | 书法/古诗文 TTS 语速未按规范调整（当前统一 1.0x） | 移动端体验 | 🟡 待优化 | PT-VFX |
| Q3 | scene_timeline 由手工编辑，易出错 | metadata 质量 | 🟡 待优化 | PT-VFX |
| Q4 | 门禁 3.3（音画对齐）无自动化检查脚本 | 发布质量 | 🔴 **v1.1已交付** | ✅ Mavis |
| Q5 | 内容包版本管理机制未建立 | 可追溯性 | 🟡 **v1.1已交付** | ✅ Mavis |
| Q6 | 用户学习行为数据未采集 | 持续优化 | 🟢 待规划 | PT-RUJ |
| Q7 | 移动端适配验证无自动化脚本 | 发布效率 | 🟡 **v1.1已交付** | ✅ Mavis |
| Q8 | 内容包发布审批流程无自动化检查 | 发布效率 | 🟡 **v1.1已交付** | ✅ Mavis |

---

## 十、附录

### A. 工具链速查

| 工具 | 位置 | 用途 |
|------|------|------|
| `PT038_converter` | `video_factory/tools/` | micro_drama → scene JSON |
| `scene_renderer_pillow.py` | `video_factory/tools/` | scene JSON → 帧渲染 |
| `compose_video.py` | `video_factory/tools/` | 帧序列 → MP4 合成 |
| `check_tag_coverage.py` | `tools/` | Stage 1 门禁 |
| `check_five_skandha.py` | `tools/` | Stage 2 门禁 |
| `check_audio_video_alignment.py` | `tools/` | **Stage 3 门禁 3.3（L1-L4自动，L5人工）** |
| `check_mobile_spec.py` | `tools/` | Stage 3 门禁 3.4 |
| `check_timeline_consistency.py` | `tools/` | Stage 3 门禁 3.5 |
| `check_package_release.py` | `tools/` | **包发布审批全量门禁** |
| `gaokao_gen.py` | `PT-038/` | 高考古诗文卡包生成 |
| `fill_missing_eps.py` | `PT-038/` | 补全缺失集 |

### B. 接口文件清单

| 接口 | 文件 | 版本 |
|------|------|------|
| IF-A | `{package}_cards.json` | v1.0.0 |
| IF-B | `metadata.json` | v1.0.0 |
| IF-C | `{episode}_chain_meta.json` | v1.0.0 |

### C. SOP 修订记录

| 版本 | 日期 | 变更内容 | 责任人 |
|------|------|----------|--------|
| v1.0 | 2026-07-19 | 初稿，整合现有管线文档 | Mavis |
| v1.1 | 2026-07-19 | 新增第六章（版本生命周期+发布审批）、第七章（自动化脚本清单）、更新Q4/Q5/Q7/Q8状态 | Mavis |

---

*本文档为 CGM 内容生产唯一操作入口，修改需注明版本变更。*
