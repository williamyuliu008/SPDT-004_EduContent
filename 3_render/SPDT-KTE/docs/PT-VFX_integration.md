# PT-VFX VideoFactory · SPDT-KTE 接入规范

> **版本**：v1.0 | **PT**：PT-VFX | **对接管线**：SPDT-KTE

---

## 一、PT-VFX 在管线中的角色

PT-VFX 是 SPDT-KTE 的**视觉渲染引擎**——接收 PT-038 的 episode .py，输出 scene JSON v2，再渲染为 Pillow 帧，合成 MP4 视频包，交付给 PT-RUJ。

---

## 二、管线输入规范

### 2.1 PT038_to_VideoFactory.py 转换器

**输入**：PT-038 的 episode .py（微剧本 JSON）
**输出**：scene JSON v2（IF-A）

**升级要求**（v1 → v2）：
- 转换器从 episode .py 读取新增字段：`knowledge_type`、`emotion_trigger`、`analogy_block`、`five_skandha`、`semantic_alignment`
- 透传到 scene JSON v2 输出
- 校验：若 `knowledge_type` 为 I/II 但缺少 `analogy_block`，报警

### 2.2 scene JSON v2 Schema 校验

所有 PT-VFX 生成的 scene JSON v2 必须通过 `SPDT-KTE/interface_protocols/scene_json_v2_schema.json` 校验。

---

## 三、管线输出规范

### 3.1 Pillow 渲染帧

scene_renderer_pillow.py 渲染时：
- 读取 `five_skandha.color_base` → 渲染为高亮关键词标注
- 读取 `emotion_trigger` → 选择视觉色调（solemnity=深墨色，resonance=暖调，curiosity=蓝色）
- `scene_type === "analogy_scene"` → 渲染 analogy_scene 模板（G），显示类比映射图

### 3.2 MP4 视频包（PT-RUJ 消费）

series_builder.py 输出视频包目录：
```
output/{series}_{ep}/
├── metadata.json          ← video_package_metadata (IF-B)
├── ep01_title.mp4         ← 各 scene 合成的 MP4
├── ep01_audio.wav        ← 纯净旁白音频（可选）
└── ep01_scenes.json      ← scene JSON v2 副本（用于 PT-RUJ 跳转）
```

---

## 四、质量门升级

scene_quality_gate.py 需新增三个 Gate（G06-G08）：

| Gate | ID | 内容 | 阻塞级别 |
|---|---|---|---|
| G06 | cognitive_load | 认知负荷 ≤ 4 点 | WARN |
| G07 | five_skandha | five_skandha 字段完整性 | BLOCK |
| G08 | dual_coding | 核心 scene 声尘-色尘语义对齐 | BLOCK |

具体实现见 `三项目协同方案_代码层审计与补全路线图.md` §3.3。

---

## 五、PT038_to_VideoFactory 转换器规范

### 5.1 新增模板类型

scene_renderer_pillow.py 需新增 `analogy_scene` 模板（G）：

```
analogy_scene 模板布局：
┌────────────────────────────────────────┐
│  标题（title）                          │
├──────────────────┬─────────────────────┤
│  源域             │  目标域              │
│  （source_domain） │  （target_domain）  │
│                  │                      │
├──────────────────┴─────────────────────┤
│  映射表（mapping_table）                 │
│  from → to (relation)                  │
├────────────────────────────────────────┤
│  ⚠️ 差异标注（difference_annotations）  │
└────────────────────────────────────────┘
```

### 5.2 认知负荷计算规则

```python
def count_cognitive_points(scene: dict) -> int:
    """计算 scene 的独立信息点数量"""
    points = 0
    c = scene.get('content', {})
    if c.get('title'): points += 1
    if c.get('subtitle'): points += 1
    if c.get('keywords'): points += min(len(c['keywords']), 2)  # 关键词最多2点
    if c.get('labels'): points += min(len(c['labels']), 2)
    if c.get('chain_items'): points += min(len(c['chain_items']), 2)
    if c.get('quote'): points += 1
    if scene.get('analogy_block'): points += 2  # 类比增加2点
    return points
```

---

## 六、跨 PT 协调规范

- PT-VFX 是 IF-A（scene_json_v2）的 **consumer** 和 IF-B（video_package_metadata）的 **producer**
- scene JSON v2 schema 变更需 PT-VFX 评估渲染器适配成本
- PT-VFX 有义务维护 PT038_to_VideoFactory.py 转换器的稳定性和性能
