# 经验教训库

> 来源：5 个 App 开发实战 | 更新时间：2026-06-18

---

## LESSON-001: SDK 版本不匹配导致白屏/闪退

**现象**: App 编译通过但模拟器白屏或闪退，无任何报错信息。

**根因**: `build-profile.json5` 中 `compatibleSdkVersion` 与模拟器实际 API 版本不一致。模拟器运行 OpenHarmony 7.0 (API 26)，但配置为 `5.0.0(12)`。

**修复**: 将所有版本号统一为 `26.0.0`，包括 `build-profile.json5`、`hvigor-config.json5`、`oh-package.json5`。

**预防**: 新项目必须从 DevEco Studio 官方 Empty Ability 模板起步，而非自己拼凑配置文件。

---

## LESSON-002: 模拟器 @ohos.net.http 永久挂起

**现象**: HTTP 请求在模拟器上不返回也不报错，timeout 参数无效。

**根因**: SDK 26 模拟器的网络栈缺陷——`connectTimeout`/`readTimeout` 不被正确执行。

**修复**: 模拟器阶段使用 mock 数据开发。HTTP 层代码保持正确（编译通过），真机上自动生效。

**预防**: 所有网络相关 App 必须有 mock 数据层，`USE_REAL` 开关控制。

---

## LESSON-003: 组件 Prop 名与内置属性冲突

**现象**: 编译错误 `Property 'size' is not assignable to same property in base type 'CustomComponent'`。

**根因**: ArkUI 所有组件继承自 `CommonAttribute`，后者有 `size()`、`height()`、`position()`、`backgroundColor()`、`enabled()` 等方法。自定义 Prop 与这些方法同名时冲突。

**修复**: 改名规则：
- `size` → `buttonSize` / `chartSize` / `tagSize`
- `height` → `barHeight`
- `position` → `fabPos`
- `backgroundColor` → `navBgColor`
- `enabled` → `isEnabled`

**预防**: 新建组件时检查 [禁止 Prop 名清单]。

---

## LESSON-004: 命令行 vs DevEco Studio 构建产物不一致

**现象**: 命令行 `hvigorw` 编译的 HAP 安装后白屏，但 DevEco Studio 构建的正常。

**根因**: 命令行打包缺少关键资源链接元数据。DevEco Studio 的构建流程包含额外的 resource linking 步骤。

**修复**: **一切正式构建必须通过 DevEco Studio。** 命令行仅用于快速语法检查。

**预防**: `build.ps1` 脚本添加警告注释，明确标注"仅用于快速验证"。
