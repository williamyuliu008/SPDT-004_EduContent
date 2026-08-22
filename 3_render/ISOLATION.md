# 3_render 隔离声明 (L1)

> **层级**：L1 (Evolutionary) — 与 L0 严格通过接口消费
> **隔离性质**：软隔离（不搬动文件，只标边界）
> **关联**：[README.md](README.md) / [LAYERS.md §3](../LAYERS.md#3-物理隔离不是搬动是标注)

## 1. 与 L0 的接口边界

3_render 消费 L0 的接口（**单向**，不允许反向依赖）：

| 来源 (L0) | 接口 | 用途 |
|:---|:---|:---|
| 2_structure (submodule) | `ep.get_data()` | 读 ep 脚本的 timeline + events |
| `tools/accuracy_auditor.py` | `audit_accuracy("P-001", input)` | P-001 视频准确性审计 |
| `templates/audio_spec.yaml` | TTS voice / rate 字段 | 配音参数（待集成）|

## 2. 暴露给下游 (4_adapt / 5_deliver) 的产物

| 产物 | 路径 | 下游消费者 |
|:---|:---|:---|
| P-001 成品 mp4 | `3_render/P-001_video/media/final/*.mp4` | 5_deliver (rujing APP 推送) |
| W28 批量报告 | `3_render/P-001_video/media/batch/w28/report.json` | 4_adapt (调度决策) |
| P-001 审计报告 | `3_render/P-001_video/media/batch/w28/audit_p001.json` | 4_adapt (质量门禁) |

## 3. 禁止的依赖

- ❌ 3_render → 4_adapt / 5_deliver (反向依赖)
- ❌ 3_render → L2 实验性代码 (`4_adapt/_06_mvp_pipeline/` 等)
- ❌ 3_render 修改 L0 工具脚本 (`tools/accuracy_auditor.py` 等只能 PR 改)

## 4. 升级到 L0 的条件

见 [README.md §4](README.md#4-升级路径)

## 5. 历史数据迁移

按 [PROJECT_DASHBOARD §11](../PROJECT_DASHBOARD.md) 已知坑：
- `3_render/SPDT-KTE/` → 已迁到 D:\4_data\work\media\renders\
- `3_render/video_factory` → 已迁到 D:\4_data\work\media\renders\
- 当前 3_render 只剩 P-001_video（gitignore 规则已修复）
