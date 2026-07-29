# 鸿蒙工坊标准操作流程 (SOP)

> 版本 2.0 | 鸿蒙工坊统一交付 | 2026-06-17

## 角色定位

鸿蒙工坊是**鸿蒙生态的统一交付端**：
- MKT 内阁直接向鸿蒙工坊下单
- 鸿蒙工坊整合各内阁输出（PV/DLV 后端、KG 知识底座、DESIGN 设计）
- 鸿蒙工坊负责：前端开发 → 编译签名 → 真机验证 → 打包发布
- 所有鸿蒙 App 均由鸿蒙工坊统一交付



## 一、环境准备

### 1.1 必备工具

| 工具 | 安装方式 | 验证命令 |
|------|---------|---------|
| DevEco Studio | winget install "DevEco Studio" | 启动后创建 Empty Ability 项目并运行 |
| Node.js | 已预装 | `node -v` |
| Java (JBR) | DevEco 自带 | 位于 DevEco 安装目录 `\jbr\bin\java.exe` |

### 1.2 关键环境变量（系统级）

```
JAVA_HOME = {DevEco目录}\jbr
DEVECO_SDK_HOME = {DevEco目录}\sdk
PATH 追加 = {DevEco目录}\tools\hvigor\bin;{DevEco目录}\jbr\bin
```

⚠️ 设为**系统变量**（非用户变量），否则 DevEco 子进程找不到 JVM DLL。**设完重启系统生效。**



## 二、新 App 创建流程

### 2.1 从模板起步（推荐）

```
1. DevEco Studio → File → New → Create Project → Empty Ability
2. 运行一次确认 Hello World 正常显示
3. 关闭 DevEco Studio
4. 将我提供的 common/、app.config.ts、Index.ets 复制到项目中
5. 重新打开 DevEco Studio → 运行
```

### 2.2 模板文件注入清单

| 文件 | 目的 | 位置 |
|------|------|------|
| `common/` 目录（23 文件） | 组件库 + 存储 + 主题 + 工具 + 算法 | `entry/src/main/ets/common/` |
| `app.config.ts` | 品牌 + Feature Flag | `entry/src/main/ets/app.config.ts` |
| `Index.ets` | 首页 | `entry/src/main/ets/pages/Index.ets` |
| AppScope 图标资源 | 应用图标 | `AppScope/resources/base/media/*.png` |

### 2.3 品牌定制检查清单

- [ ] `AppScope/app.json5`：bundleName（唯一）、vendor（鸿蒙爆款工作室）
- [ ] `AppScope/resources/base/element/string.json`：app_name
- [ ] `entry/src/main/resources/base/element/string.json`：EntryAbility_label、module_desc
- [ ] `entry/src/main/ets/app.config.ts`：appName、shortDesc、primaryColor



## 三、ArkTS 编码铁律（API 26 严格模式）

### 3.1 禁止事项（编译器会直接报错）

| ❌ 禁止 | ✅ 正确做法 |
|---------|-----------|
| 使用 `any` 或 `unknown` 类型 | 显式标注 interface/type |
| 组件 Prop 与内置属性重名（`size`/`height`/`enabled`/`position`/`backgroundColor`） | 改名：`buttonSize`/`barHeight`/`isEnabled`/`fabPos`/`navBgColor` |
| 对象索引访问 `obj[key]` | 用 `if/else` 分支或 switch |
| 行内对象类型 `(x: {a: string}) =>` | 先声明 `interface`，再用接口名 |
| `build()` 方法中提前 `return` | 用条件渲染替代（`if (visible) { ... }`） |
| `Array.from()` 的 `unknown` | 显式类型 `new Array(n).fill(0).map(...)` |
| 无类型标注的对象字面量 | 加 `as InterfaceName` 断言 |
| `.ts` 扩展名（入口文件/页面） | 用 `.ets` |

### 3.2 Page 开发模板

```typescript
import { HNavBar } from '../common';

@Entry
@Component
struct Index {
  @State page: string = 'home';

  build() {
    Column() {
      HNavBar({ title: '页面标题', navBgColor: '#333333' })
      // 页面内容用 if/else 切换
      if (this.page === 'home') {
        // 列表内容
      }
    }
    .width('100%').height('100%')
  }
}
```

### 3.3 可用 Common 组件速查

| 组件 | import | 核心 Props |
|------|--------|-----------|
| HNavBar | `'../common'` | title, showBack, navBgColor, rightActions, onBack |
| HButton | `'../common'` | label, type, buttonSize, loading, onTap |
| HCard | `'../common'` | title, subtitle, trailing, isEnabled, onTap |
| HProgressBar | `'../common'` | current, total, type, barHeight |
| HToast | `'../common'` | `HToast.show({message, type})` |
| HEmptyState | `'../common'` | message, actionLabel, onAction |
| HFormItem | `'../common'` | label, value(@Link), type, required, validator |

> 完整 API 参考：`docs/kernel-spec.md`



## 四、编译排错流程

```
1. 代码编写 → 2. 点绿色 ▶ 运行 → 3. 看输出面板
                                      ↓
                           ✅ 成功 → 在模拟器上测试
                           ❌ 失败 → 复制错误日志
                                      ↓
                           4. 常见错误自检（见下方）
                                      ↓
                           5. 修复 → 回到步骤 2
```

### 4.1 常见错误速查表

| 错误信息 | 原因 | 解决 |
|---------|------|------|
| `arkts-no-any-unknown` | 用了 any/unknown | 显式声明类型 |
| `Property 'xxx' does not exist` | Prop 与内置属性冲突 | 改 Prop 名 |
| `arkts-no-props-by-index` | 对象索引访问 | 改用分支 |
| `arkts-no-obj-literals-as-types` | 行内类型声明 | 声明 interface |
| `Object literal must correspond to...` | 未标注类型的对象 | 加 `as Type` |
| `Cannot find module 'ets/entryability/EntryAbility'` | 入口文件扩展名错误或 SDK 版本不匹配 | 用 `.ets` 扩展名；检查 build-profile.json5 SDK 版本 |
| 模拟器白屏（无崩溃） | SDK 版本不匹配 | `build-profile.json5` 的 compatibleSdkVersion 必须匹配模拟器 |
| 模拟器闪退 | 代码运行时错误 | 检查 hilog：`hdc shell hilog -x` |

### 4.2 SDK 版本确认

```powershell
# 查看模拟器 API 版本
hdc shell "param get const.ohos.apiversion"

# 查看 DevEco 已安装 SDK 版本
dir "{DevEco目录}\sdk\default\openharmony\ets\api"
```

`build-profile.json5` 中 `compatibleSdkVersion` 必须与模拟器版本一致。



## 五、部署与安装

### 5.1 DevEco Studio 一键运行（推荐）

```
打开项目 → 选择设备（模拟器/真机） → 绿色 ▶
```

自动完成：编译 → 签名 → 安装 → 启动

### 5.2 命令行编译安装（备选）

```powershell
# 环境
$env:JAVA_HOME = "{DevEco}\jbr"
$env:DEVECO_SDK_HOME = "{DevEco}\sdk"
$env:PATH = "{DevEco}\tools\hvigor\bin;...\jbr\bin;$env:PATH"

# 编译
hvigorw assembleHap --mode module -p product=default -p buildMode=debug

# 打包 HAP
java -jar {sdk}\openharmony\toolchains\lib\app_packing_tool.jar --mode hap ...

# 安装
hdc install entry-default-unsigned.hap
```

⚠️ 命令行编译产出可能与 DevEco Studio 有差异。**优先使用 DevEco Studio。**

### 5.3 模拟器日志查看

```powershell
# 查看崩溃日志
hdc shell "ls /data/log/faultlog/faultlogger/" | findstr "craftsman"
hdc shell "cat /data/log/faultlog/faultlogger/{文件名}"

# 实时日志
hdc shell "hilog -x" | findstr "Error|crash|FATAL"
```



## 六、工坊目录规范

```
D:\9_infra\harmony_workshop\
├── common/                  ← 公共内核（API 26 strict mode）
│   ├── components/          ← 12 个 UI 组件
│   ├── storage/             ← StorageService + Keys
│   ├── theme/               ← 3 套主题 Design Token
│   ├── utils/               ← date/format/validate/id/debounce
│   ├── algo/                ← SM-2 + Streak
│   └── index.ets            ← 统一 barrel export
├── apps/
│   ├── craftsman-utils/     ← 极客工具箱
│   ├── thinkkit-flashcard/  ← 静·闪卡
│   ├── thinkkit-zknote/     ← 大纲速记
│   └── rhythm-habit/        ← 律动习惯
├── docs/                    ← 文档中心（8 份）
├── scripts/                 ← 工具脚本（7 个）
├── templates/               ← 项目模板
└── _archive_v1/             ← 废弃的旧版本
```

### 每个 App 内部结构

```
apps/{app}/
├── AppScope/app.json5         ← bundleName, vendor, icon
├── build-profile.json5        ← SDK version = 26.0.0
├── hvigor/hvigor-config.json5 ← modelVersion = 26.0.0
├── oh-package.json5           ← modelVersion = 26.0.0
└── entry/
    ├── build-profile.json5    ← apiType = stageMode
    ├── hvigorfile.ts
    ├── oh-package.json5
    └── src/main/
        ├── module.json5        ← abilities + pages
        ├── ets/
        │   ├── app.config.ts   ← 品牌 + Feature Flag
        │   ├── common/         ← 从 workshop/common/ 同步
        │   ├── entryability/EntryAbility.ets
        │   └── pages/Index.ets  ← 主页面
        └── resources/
            ├── base/profile/main_pages.json
            └── base/element/string.json
```



## 七、质量检查清单（上架前）

- [ ] `validate-common.ps1` 通过（0 any、0 dup ThemeTokens、0 bad imports）
- [ ] 4 个 App 均在 DevEco Studio 编译通过并模拟器运行正常
- [ ] 真机测试：安装 → 启动 → CRUD → 深色模式 → 返回键
- [ ] 折叠屏/平板适配测试
- [ ] 权限声明最小化（本地工具 App 权限为空）
- [ ] AppScope 图标为不透明 PNG（512×512）
- [ ] bundleName 全网唯一
- [ ] 所有字符串资源已中文化



## 八、新 App 开发决策树

```
需要新 App？
  ├─ 同一赛道赛马？（如 ThinkKit 再加一个 App）
  │     → 复制现有 App，修改 app.config.ts Feature Flag + Index.ets
  │
  ├─ 新赛道？
  │     → DevEco Studio 新建 Empty Ability → 注入 common/ → 写 Index.ets
  │     → 参考 track-selection-checklist.md 评估选题
  │
  └─ 纯 UI 变化？（换皮）
        → 只改 app.config.ts 的 primaryColor + Index.ets 的 build()
```
