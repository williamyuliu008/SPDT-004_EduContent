# RUJING 项目交接文档

> **目的**：本项目从 SPDT-004 主窗口交接至另一窗口推进
> **依据**：willi 决策（"对 RUJING 项目的处理，请你总结一下交接文档，我们在另一个窗口推进"）
> **当前位置**：`D:/2_products/education/SPDT-004_EduContent/handoff/rujing.md`
> **配套**：MANIFEST.yaml（已闭环字段）+ git tag v2.0-approved

---

## 1. 一句话定位

**rujing = 高考备考 HarmonyOS APP**，由 SPDT-001_Harmony 框架承载，**内容由 SPDT-004 提供**。本交接文档聚焦于"内容生产 → APP 推送"链路，不涉及 APP 端开发。

---

## 2. 当前状态（实测）

| 维度 | 数据 |
|:---|:---|
| rujing APP 链总数 | **188 链** |
| rujing APP 卡总数 | **1293 卡** |
| 学科分布 | 历史 62 链 441 卡 / 政治 61 链 427 卡 / 地理 49 链 345 卡 / 其他 16 链 80 卡 |
| 推送成功率 | **100%**（0 失败）|
| 准确性审计 | P-002 93/93 / P-003 1/1 / P-004 1/1 全 GOLD |
| 待 ship | 0 |
| 总体成熟度 | 准出门（v2.0-approved 锁档）|

---

## 3. 文件位置地图（接手人必看）

### 3.1 rujing APP 端（不归本窗口管）

```
D:/92_products/SPDT-001_Harmony/apps/rujing/         ← APP 源码（鸿蒙）
D:/92_products/SPDT-001_Harmony/SPDT-001_Harmony_Build_SOP.md   ← 构建 SOP
```

### 3.2 内容生产（SPDT-004 范围）

```
D:/2_products/education/SPDT-004_EduContent/        ← SPDT-004 仓库
  PRODUCT_LINE.md v2.0                              ← 产品线（P-002 知识卡片）
  1_ingest/ENVELOPE_SPEC.md                         ← 输入端规范
  tools/accuracy_auditor.py                         ← 4 真产品准确性审计
  templates/default_config.yaml                     ← 4 真产品参数集
  handoff/rujing.md                                 ← 本文件
```

### 3.3 转换 + 推送工具（**关键**）

```
D:/4_data/knowledge_cards/                          ← 内容库
  00-项目文档/MANIFEST.yaml                          ← 全局索引（已闭环）
  历史/cards/                                       ← 62 套历史卡
  地理/cards/                                       ← 49 套地理卡
  政治/cards/                                       ← 61 套政治卡
  rujing_out/                                       ← 转换产物（v3 73 + v6 113 + 历史新转 62 = 248）
  autoclaw_kit/08_tools/
    ru_cardpkg_convert.py                           ← v6.0 转换器（单套转换）
    _push_to_rujing.py                              ← 单套推送
    _batch_convert_push.py                          ← 批量转换+推送（已修 bug）
    _validate_cards.py                              ← autoclaw 校验
    push_log_<ts>.txt                               ← 推送日志
    _failed_<ts>/                                   ← 失败文件备份
```

---

## 4. 已交付的 3 个关键工具

### 4.1 `ru_cardpkg_convert.py` v6.0
- 单套卡 → rujing CardPackage JSON
- 用法：`python ru_cardpkg_convert.py --card-dir <套卡路径> --output <输出 JSON>`
- 详见脚本头注释

### 4.2 `_push_to_rujing.py`
- 单套推送（POST 到 `http://192.168.1.102:18999/upload`）
- 用法：`python _push_to_rujing.py [文件路径 | /list | /all]`
- 默认推最近 1 个修改的 rujing_*.json

### 4.3 `_batch_convert_push.py` v2.0（W23 修 bug）
- 批量转换 + 推送
- 修过的 bug：之前只跑 111 套（漏历史 62），现在跑 172 套
- 集成 accuracy_auditor 验收
- 失败重试 3 次 + 失败目录
- 用法：
  ```bash
  # 全量（转+推+验）
  python _batch_convert_push.py
  
  # 只推已有 rujing_*.json（不重转）
  python _batch_convert_push.py --skip-convert
  
  # 单学科
  python _batch_convert_push.py --subjects 历史
  
  # 干跑
  python _batch_convert_push.py --dry-run
  ```

### 4.4 `accuracy_auditor.py`（在 SPDT-004）
- 4 真产品 P0 样本准确性审计
- W23 修了 source_citation bug（之前检查整个 JSON 顶层，现在查 node_cards[].sources[]）
- W23 加了"按产品分级"（P-002 严，P-001/P-003/P-004 弱）
- 用法：`python tools/accuracy_auditor.py --product P-002 --input <file>`

---

## 5. 关键技术细节（**接手必看**）

### 5.1 手机 IP
- **PHONE_IP = `192.168.1.102:18999`**（之前是 `192.168.43.1`，**换 wifi 会变**）
- WiFi 切换后必须更新 `_batch_convert_push.py` 和 `_push_to_rujing.py` 的 `PHONE_IP` 常量

### 5.2 DevEco Studio 依赖（**重要！踩过坑**）
- rujing APP 是鸿蒙 APP，**DevEco Studio 关闭时 APP 服务不响应**（端口 18999 不可达）
- 每次跑推送前**确认 DevEco Studio 在运行**（或 APP 在前台）
- 验证方法：`curl http://192.168.1.102:18999/subjects` → 应该 200
- 如果超时，先开 DevEco Studio 启动模拟器/真机调试

### 5.3 HarmonyOS 后台休眠
- 即使 DevEco Studio 在开，**手机锁屏超过几分钟**后 rujing APP 服务会进入省电模式
- 表现为"第一次通，之后全超时"
- 解决：点亮手机屏幕 + 解锁 + 保持 APP 前台

### 5.4 rujing APP 端点
- `/subjects` - 各学科链/卡数（GET）
- `/upload` - 推 CardPackage（POST，body 是 rujing_*.json 全文）
- `/import_result` - 最近一次导入结果（GET）
- `/health` - 服务健康（GET）
- `/` - 同 health
- `/chains` - **不存在**（404 正常）

### 5.5 CardPackage 格式
- 当前版本 v6.0（ru_cardpkg_convert.py 生成）
- 字段：version / series / total_chains / total_cards / node_cards[] / strategy_cards[] / chain_meta
- chain_id 唯一性去重（重复推会忽略）
- 卡片结构：card_id / chain_id / chain_title / card_type (NODE/STRATEGY) / chain_role / front / back_core / back_detail / maturity / tags[] / sources[]

---

## 6. 待办清单（接手人按优先级）

### P0 · 持续运营
- [ ] 监控 autoclaw 持续产新卡（MANIFEST.yaml 的 in_progress/done 流）
- [ ] 新卡 ship 到 rujing（_batch_convert_push.py --subjects X）
- [ ] accuracy_auditor 跑全量验收

### P1 · APP 端完善
- [ ] rujing APP 端 UI 优化（已 188 链 1293 卡够用，但 UX 还要打磨）
- [ ] CardPackage v7.0（如果需要新增字段：exercises / video_link 等）
- [ ] cooked 流程（当前 raw_count=全部，cooked_count=0）

### P2 · 跨学科扩展
- [ ] 英语 / 物理 / 化学 / 生物（当前 3 学科，5 学科缺）
- [ ] 真产品 4 选 1 之外的扩产（P-001 视频 / P-003 电子书 / P-004 音频 → rujing APP 集成）

### P3 · 不做的（避免范围漂移）
- ❌ 复活已废止产品（v1.0-P-004 微剧本 / v1.0-P-007 Skill）
- ❌ 4_adapt L2 平台层（资源未到）
- ❌ 输入端 watcher/CLI（自动化运营 W24 推）

---

## 7. 已知坑（**别再踩**）

| # | 坑 | 表现 | 解决 |
|:---:|:---|:---|:---|
| 1 | DevEco Studio 关闭 | APP 18999 端口不响应，全超时 | 启动 DevEco + APP |
| 2 | 手机锁屏 | 第一次通，之后超时 | 点亮屏幕 + 解锁 |
| 3 | WiFi 切换 | PHONE_IP 变 192.168.x.x | 更新脚本常量 |
| 4 | `_batch_convert_push.py` 只跑 111 套 | 历史 62 套漏 | 已修（W23 commit 90b0f6b 之前）|
| 5 | `accuracy_auditor` 报"全缺 sources" | 检查顶层而非卡片内 | 已修（W23 commit 90b0f6b）|
| 6 | 重复推已 ship 链 | rujing APP 按 chain_id 去重，**不报错** | 安全但浪费带宽 |

---

## 8. 接手人需要的能力

- 鸿蒙 APP 基础（DevEco Studio / 模拟器 / 真机调试）
- Python 脚本读写（`ru_cardpkg_convert.py` 等 4 个 .py）
- YAML 读写（MANIFEST.yaml / SPDT.yaml）
- Git 基础（autoclaw 推 Git → 本机 pull → Mavis 推 rujing）

---

## 9. 紧急情况

| 情况 | 处置 |
|:---|:---|
| 手机 IP 变了 | `arp -a` 查新 IP，更新 `_batch_convert_push.py` + `_push_to_rujing.py` |
| DevEco 启动失败 | 看 SPDT-001_Harmony_Build_SOP.md |
| rujing APP 数据损坏 | 用 `card_auditor.py` 校验本地 rujing_*.json，从未 ship 的恢复 |
| MANIFEST.yaml 误改 | git reflog + 回滚（MANIFEST 在 D:/4_data 仓库外，用 Git 跟踪需先初始化）|

---

## 10. 联系 / 上下文

- **本交接出自**：SPDT-004 主窗口（W22-W23 治理精简 + 输入端接口 + 4 真产品 P0 样本 + P1A 推送）
- **SPDT-004 主窗口继续**：项目管理和优化（LAYERS.md / WINDOWS.md / CI 工具 / 模板 / 治理）
- **RUJING 接手窗口**：内容生产 + 推送 + APP 集成
- **共享资源**：
  - `D:/4_data/knowledge_cards/` - 知识库（autoclaw + Mavis 共写）
  - `D:/4_data/rujing_out/` - 转换产物
  - `tools/accuracy_auditor.py` - 质量工具（SPDT-004 维护）

---

## 11. 版本历史

| 版本 | 变更 |
|:---|:---|
| v1.0 | 首发：W23 准出门完成，188 链 1293 卡 |
