# PT-038 TextExperience · SPDT-KTE 接入规范

> **版本**：v1.0 | **PT**：PT-038 | **对接管线**：SPDT-KTE

---

## 一、PT-038 在管线中的角色

PT-038 是 SPDT-KTE 的**内容工厂**——接收 PT-037 知识库的结构化知识，输出：

1. **微剧本 JSON**（scene JSON v2 的上游输入）
2. **Flashcard 包 JSON**（IF-C，PT-RUJ 消费）
3. **电子书**（DOCX + MD，辅助学习）
4. **广播剧音频 MP3**（声尘原料，供 PT-RUJ 直接播放）

---

## 二、管线输出规范

### 2.1 微剧本（scene JSON v2 上游）

PT-038 不直接输出 scene JSON v2，而是输出**episode .py**（微剧本数据），再经 `PT038_to_VideoFactory.py` 转换器生成 scene JSON v2。

**episode .py 需增加的字段（v2 兼容）**：

```python
dramatic_beats = [
    {
        "beat_type": "narrative",
        "content": "乾元元年……",
        # === 管线要求字段 ===
        "knowledge_type": "II",            # 必填：I/II/III/IV
        "emotion_trigger": "resonance",   # 必填：curiosity/resonance/solemnity/sober_reflection/none
        "analogy_block": { ... },         # knowledge_type 为 I/II 时必填
        "five_skandha": { ... },          # 必填
        "semantic_alignment": { ... }     # 核心 scene 必填
    }
]
```

**生成器升级**：card_generator.py 和 ebook_generator.py 保持向后兼容；PT038_to_VideoFactory.py 由 PT-VFX 维护。

### 2.2 Flashcard 包（IF-C）

- **输出路径**：`PT-038/ebooks/{series}_cards.json`
- **Schema**：见 `SPDT-KTE/interface_protocols/card_package_schema.json`
- **导入 PT-RUJ**：复制到 rujing 沙箱目录 → ImportService 读取

### 2.3 广播剧音频（IF-B 上游）

- **输出路径**：`PT-038/audio/{ep}_audio.wav`
- **PT-VFX 消费**：作为 TTS 旁白原料
- **PT-RUJ 直接消费**：通过 audio_meta.json 映射，HarmonyOS MediaService 直接播放

---

## 三、SOP 升级要求（v1.2）

SPDT-KTE 要求 PT-038 SOP 升级到 v1.2，增加以下章节：

| 章节 | 内容 | 优先级 |
|---|---|---|
| §14 | 脑科学约束（5条规则） | P0 |
| §15 | 类比专属通道（Type I-IV 判定 + analogy_block 规范） | P0 |
| §16 | 声尘精细化设计（语气/停顿/节奏标注） | P1 |
| §17 | v2 字段规范（knowledge_type / five_skandha / semantic_alignment） | P0 |

---

## 四、跨 PT 协调规范

### 4.1 接口版本管理

- PT-038 是 IF-A（scene_json_v2）和 IF-C（card_package）的 **producer**
- Schema 变更由 SPDT-KTE DRC（Design Review Committee）统筹
- PT-038 有权提出接口变更提案，但必须经过 PT-VFX 和 PT-RUJ 影响评估

### 4.2 质量门

- **G-AUDIT-A**（历史准确性）：PT-038 所有 episode 必须通过
- **G-COGNITION**（认知合规性）：scene JSON v2 五蕴字段完整性由 PT038_to_VideoFactory.py 校验，PT-038 提供正确字段即可
- **G-INTERFACE**：IF-A/B/C schema 校验，PT-038 需确保输出 JSON 符合 schema

### 4.3 反馈接收（Phase C）

PT-038 将在 Phase C 接收来自 PT-RUJ 的 `learning_feedback`（IF-D），驱动五蕴卡点自适应机制。具体接口定义见 `SPDT-KTE/interface_protocols/learning_feedback.json`。
