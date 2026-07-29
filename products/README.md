# products/ — 课程产品包

> **定位**：内容层。按课程系列组织源内容，生成物入 D:/4_data/education/。

## 目录结构

```
products/
├── courses/                   ← 备考课程包（按学科）
│   ├── 书法备考_墨骨山河/       ← 国美书法校考课程
│   └── 历史备考_古史知识链/     ← 高考历史课程
├── PT-033_CorpTraining/       ← 企业培训（独立内容包）
└── PT-039_CalligraphyVision/  ← 书法视觉素材库
```

## 课程产品

### 书法备考_墨骨山河

国美书法校考备考课程，含墨骨山河系列剧本杀、古汉语训练、辨析卡。

- **数据目录**：D:/4_data/education/TextExperience/书法备考_墨骨山河/
- **ephemera**：墨骨山河_ep09（Ep01-08 待人工创作）
- **资产**：草书辨析卡v4、碑帖素材库

### 历史备考_古史知识链

高考历史备考课程，含古代史+近代史+世界史知识链卡片包。

- **数据目录**：D:/4_data/education/TextExperience/历史备考_古史知识链/
- **内容**：古史_v1~v4（4卷，60集，448张知识链卡）

## 数据架构原则

| 内容类型 | 存放位置 | 说明 |
|:---|:---|:---|
| 源内容（剧本JSON/知识链源码） | products/courses/ | Git 管理 |
| 生成脚本（ep*.py） | platform/TextExperience/ | Git 管理 |
| 中间产物（scene JSONs） | D:/4_data/education/TextExperience/*/_intermediate/ | 数据目录 |
| 最终交付物（audio/ebook/cards） | D:/4_data/education/TextExperience/*/_output/ | 数据目录 |

## 与平台层的关系

```
products/courses/（源内容包）
  → platform/TextExperience（执行生成）
  → D:/4_data/education/TextExperience/*/_output/（成品）
  → AdaptivePrepPlatform（编排）
  → TextExperienceAPP（APP交付）
  → 用户终端
```

