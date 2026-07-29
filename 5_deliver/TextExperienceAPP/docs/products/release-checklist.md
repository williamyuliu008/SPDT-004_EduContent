# 华为应用市场上架检查清单 (Release Checklist)

> 适用：鸿蒙工坊所有 App | 更新：2026-06-16 | 华为 AppGallery Connect

---

## 一、上架前必检项（每项必须通过）

### 1.1 应用信息

- [ ] `AppScope/app.json5` 中 `bundleName` 全网唯一
- [ ] `versionCode` 递增（首次上架 ≥ 1000000）
- [ ] `versionName` 语义化（如 `1.0.0`）
- [ ] `vendor` 统一为 `鸿蒙爆款工作室`
- [ ] `icon` 和 `label` 正确引用资源文件

### 1.2 图标与截图

- [ ] `AppScope/resources/base/media/app_icon.png` — 512×512 PNG，无透明背景
- [ ] `AppScope/resources/base/media/start_icon.png` — 启动图标
- [ ] 应用市场截图：至少 3 张（手机竖屏 1080×2340），不包含其他品牌设备边框
- [ ] 截图展示核心功能（非空白页/占位图）

### 1.3 权限声明

- [ ] `module.json5` 的 `requestPermissions` 仅为必要权限
- [ ] 每项权限的 `reason` 已翻译为中文并写入 `string.json`
- [ ] **本地工具类 App（笔记/闪卡/极客工具）：权限数组为空 `[]`**
- [ ] 含网络功能 App：仅声明 `ohos.permission.INTERNET`
- [ ] 含后台任务 App：声明 `ohos.permission.KEEP_BACKGROUND_RUNNING` 并注明使用场景

### 1.4 隐私合规

- [ ] App 不收集任何个人可识别信息（PII）
- [ ] 不请求通讯录/位置/相机/麦克风等敏感权限（除非核心功能强依赖）
- [ ] 无第三方 SDK 数据上报
- [ ] 无隐藏的后台网络请求
- [ ] 如需隐私政策：在 `AppScope/resources/base/element/string.json` 中提供 `privacy_url`
- [ ] 所有数据存储在本地 Preferences，不上传任何服务器

---

## 二、功能自检

### 2.1 基础功能

- [ ] CRUD 操作：新建 → 保存 → 列表显示 → 点击查看 → 编辑 → 删除 → 列表更新
- [ ] 空状态显示正确（首次打开无数据时显示 HEmptyState）
- [ ] 返回键行为正确（不直接退出 App，回到上一页）
- [ ] 应用切换到后台再切回，数据不丢失
- [ ] 应用被系统杀死后重启，数据持久化正常

### 2.2 适配测试

- [ ] **折叠屏**：展开/折叠状态下列表页正常，编辑页无布局错乱
- [ ] **平板**：列表+详情分栏显示（如适用）
- [ ] **深色模式**：所有页面在深色/浅色模式下可读，对比度合格
- [ ] 字体缩放：系统字体调至最大时，页面不截断不溢出

### 2.3 网络相关（如声明了 INTERNET 权限）

- [ ] 无网络时 App 不崩溃（优雅降级，显示离线提示）
- [ ] 网络请求有合理的超时时间（≤ 15s）
- [ ] 所有 `http.createHttp()` 调用后有 `req.destroy()` 释放

---

## 三、元服务卡片（如适用）

- [ ] `form_config.json` 中卡片尺寸正确（2×2 / 2×4 / 4×4）
- [ ] `FormAbility.ts` 的 `onUpdateForm` 正确更新卡片数据
- [ ] 卡片点击跳转到指定页面
- [ ] 卡片定期刷新间隔合理（≥ 30 分钟）

---

## 四、ASO 与应用市场

### 4.1 应用信息

- [ ] 应用名称：2-8 个中文字符，含品类关键词（如 `静·闪卡 - 间隔记忆`）
- [ ] 简短描述（< 80 字）：一句话价值主张 + 核心关键词
- [ ] 完整描述：300-2000 字，包含功能列表、使用场景、技术亮点
- [ ] 关键词标签：5-8 个，覆盖品类词 + 场景词 + 长尾词
- [ ] 分类选择正确（参考各 App 的 `store.category` 字段）

### 4.2 截图文案

- [ ] 每张截图上有简洁的功能标注（非纯截图）
- [ ] 不使用「最好」「第一」等绝对化用语
- [ ] 不使用 Apple/Google 品牌元素

---

## 五、编译与签名

- [ ] 使用 Release 模式编译：`hvigorw assembleHap --mode module -p buildMode=release`
- [ ] HAP 文件大小合理（≤ 50MB 为佳，超过需考虑分包）
- [ ] 在 AppGallery Connect 中配置签名证书（.p12 / .cer）
- [ ] 编译的 HAP 使用正确 Profile 签名（非 debug 签名）

---

## 六、发布后监控（上架 7 天内）

- [ ] 首日下载量 & 崩溃率监控（AppGallery Connect → 质量 → 崩溃）
- [ ] 用户评分 & 评论：48 小时内回复所有评论
- [ ] 关键词排名变化：上架第 3 天和第 7 天分别检查
- [ ] 如崩溃率 > 1%：立即修复并提交新版本

---

## 七、快速参考：每个 App 的权限声明

| App | 权限 | 说明 |
|-----|------|------|
| `craftsman-utils` | 无 | 纯本地工具 |
| `thinkkit-flashcard` | 无 | 纯本地笔记 |
| `thinkkit-zknote` | 无 | 纯本地笔记 |
| `rhythm-habit` | `KEEP_BACKGROUND_RUNNING` | 番茄钟后台计时 |

---

## 八、常见被拒原因及对策

| 原因 | 对策 |
|------|------|
| 应用名称含竞品品牌词 | 去掉所有 Apple/Google/Anki/Forest 等词 |
| 权限声明无 reason | 每个权限在 string.json 中添加 reason 字段 |
| 截图含非鸿蒙设备 | 使用纯色背景截图，不套设备框 |
| 功能过于简单 | 确保至少有 3 个独立页面和完整 CRUD |
| 隐私政策缺失 | 即使是纯本地 App 也建议提供简易隐私声明链接 |
| 图标含透明背景 | 确认 icon 为不透明 PNG |
| bundleName 与其他 App 冲突 | 使用 `com.harmonystudio.{track}.{app}` 格式 |

---

## 九、版本迭代检查项

- [ ] 新版本 `versionCode` > 旧版本
- [ ] 更新日志包含用户可感知的变化（非「修复了一些 bug」）
- [ ] 新权限声明附有充分的 reason 说明
- [ ] 数据库迁移处理（如果 StorageService key 或数据结构变化）
