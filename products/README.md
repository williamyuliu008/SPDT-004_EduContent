# products/ — 课程产品包

> **定位**：内容层。按课程系列组织，不含平台代码。

## 目录结构

```
products/
├── courses/                   ← 备考课程包（按学科）
│   ├── 书法备考_墨骨山河/       ← 国美书法校考课程
│   └── 历史备考_古史知识链/     ← 高考历史课程
├── PT-033_CorpTraining/       ← 企业培训（独立内容包）
└── PT-039_CalligraphyVision/  ← 书法视觉素材库（平台资产）
```

## 课程产品

### 书法备考_墨骨山河

国美书法校考备考课程，含墨骨山河系列剧本杀、古汉语训练、辨析卡。

- **Git 仓库**：PT-038_TextExperience（`../PT-038_TextExperience/`）
- **ephemera**：墨骨山河_ep09（Ep01-08 待人工创作）
- **资产**：草书辨析卡v4、碑帖素材库（`PT-039_CalligraphyVision/`）

### 历史备考_古史知识链

高考历史备考课程，含古代史+近代史+世界史知识链卡片包。

- **Git 仓库**：PT-038_TextExperience（`../PT-038_TextExperience/`）
- **内容**：古史_v1~v4（4卷，60集，448张知识链卡）

## 与平台层的关系

```
products/courses/（内容包）
  └── platform/PT-037_AdaptivePrepPlatform/（编排平台）
  └── platform/SPDT-014_EduApps/（APP交付）
  └── SPDT-KTE/（渲染管线）
```
