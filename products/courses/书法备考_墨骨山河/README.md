# 书法备考_墨骨山河

> **数据目录**：D:/4_data/education/TextExperience/书法备考_墨骨山河/

> **课程**：国美书法校考备考
> **内容来源**：PT-038_TextExperience / PT-039_CalligraphyVision

## 课程内容

| 资产 | 路径 | 状态 |
|:---|:---|:---|
| 墨骨山河_ep09（许慎·说文解字） | 墨骨山河_ep09/ | ✅ 完整 |
| 墨骨山河_ep01~ep08 | 墨骨山河_ep*/ | ❌ 缺失（待人工创作） |
| 草书辨析卡 v4 | 草书辨析卡/ | ✅ 13张+6脚本 |
| 国美书法配置包 | 配置包_cafa_calligraphy_2026/ | ✅ |

## 考试科目覆盖

- **古汉语**：译篆 / 句读（《说文解字》六书体系）
- **书法史论**：各代书家风格辨析（辨析卡）
- **书写实践**：碑帖临摹（PT-039 素材库）

## 交付形态

- APP（剧本杀）：→ `platform/SPDT-014_EduApps/apps/rujing/`
- 辨析卡 PDF：→ `PT-039_CalligraphyVision/`
- 广播剧 MP3：→ PT-038 `audio/`
- 电子书：→ PT-038 `ebooks/`

## 制作流水线

```
platform/TextExperience/（生成脚本）
  ↓ 生成
D:/4_data/education/TextExperience/书法备考_墨骨山河/_source/（源脚本+meta）
  ↓ SPDT-KTE/PT-VFX
D:/4_data/education/TextExperience/书法备考_墨骨山河/_intermediate/（scene JSONs）
  ↓ PT-VFX渲染
D:/4_data/education/TextExperience/书法备考_墨骨山河/_output/
  ├── audio/       → TextExperienceAPP 消费
  ├── ebooks/     → TextExperienceAPP 消费
  └── cards/      → AdaptivePrepPlatform 消费
```

## ⚠️ 待完成

- [ ] 人工创作墨骨山河 Ep01-08（王羲之/苏轼/阮元/张旭怀素/李斯/康有为）
