# 项目脚手架模板 — 鸿蒙爆款App工作室

> 本文档定义标准的鸿蒙项目目录结构和从 0 到 MVP 的创建步骤  
> 适用：HarmonyOS NEXT Stage 模型 / DevEco Studio 5.0+

---

## 一、标准鸿蒙项目目录结构

```
YourApp/                              # App 根目录（如 thinkkit-flashcard）
├── AppScope/                         # 应用级配置（各 App 单独修改）
│   ├── app.json5                     # 应用名、图标、版本号、bundleName
│   └── resources/
│       └── base/
│           ├── element/
│           │   └── string.json       # App 文案（应用名、描述等）
│           └── media/
│               ├── app_icon.png      # 应用图标 512×512
│               └── start_icon.png    # 启动图标
│
├── entry/                            # 入口模块
│   └── src/
│       ├── main/
│       │   ├── ets/
│       │   │   ├── entryability/
│       │   │   │   └── EntryAbility.ts      # 应用入口（在此初始化 Storage/Theme）
│       │   │   │
│       │   │   ├── pages/                   # 页面文件
│       │   │   │   ├── IndexPage.ets         # 首页（主列表）
│       │   │   │   ├── DetailPage.ets        # 详情页
│       │   │   │   └── FormPage.ets          # 新建/编辑表单页
│       │   │   │
│       │   │   ├── widgets/                  # 元服务卡片
│       │   │   │   └── AppWidget.ets
│       │   │   │
│       │   │   └── formability/
│       │   │       └── FormAbility.ts       # 卡片数据提供者
│       │   │
│       │   ├── module.json5                 # 模块配置（权限、路由、卡片）
│       │   └── resources/                   # 模块级资源
│       │       └── base/
│       │           ├── element/
│       │           │   ├── string.json      # 页面文案
│       │           │   └── color.json       # 基础颜色
│       │           ├── media/               # 页面图标
│       │           └── profile/
│       │               ├── main_pages.json   # 页面路由注册
│       │               └── form_config.json  # 卡片配置
│       │
│       └── test/                            # 单元测试
│
├── app.config.ts                     # App 配置（Feature Flag、品牌信息）
│
├── build-profile.json5               # 构建配置
├── hvigorfile.ts                     # 构建脚本入口
└── oh-package.json5                  # 依赖管理
```

### 公共模块目录（workspace 级别，所有 App 引用）

```
harmony-capability-center/
└── common/
    ├── components/                   # UI 组件库
    │   ├── HButton.ets
    │   ├── HCard.ets
    │   ├── HEmptyState.ets
    │   ├── HFormItem.ets
    │   ├── HProgressBar.ets
    │   └── HToast.ets
    ├── storage/                      # 存储层
    │   ├── storageService.ts
    │   └── keys.ts
    ├── theme/                        # 主题系统
    │   └── tokens.ts
    ├── utils/                        # 工具函数
    │   ├── date.ts
    │   ├── format.ts
    │   └── validate.ts
    └── algo/                         # 算法库
        ├── sm2.ts
        └── streak.ts
```

---

## 二、新 App 创建步骤（从 0 到 MVP）

### Step 1：复制模板工程（5 分钟）

```powershell
# 1. 在 DevEco Studio 中新建 Empty Ability 项目
#    模板选：Empty Ability > Stage 模型 > ArkTS

# 2. 项目名按赛道命名规范：
#    {赛道前缀}-{AppKey}
#    例：thinkkit-flashcard / rhythm-habit / craftsman-jsonfmt

# 3. bundleName 格式：
#    com.{studio}.{track}.{app}
#    例：com.harmonystudio.thinkkit.flashcard
```

### Step 2：引入 common/ 内核（5 分钟）

```powershell
# 方式一：复制到 App 目录（简单直接）
cp -r ../common ./common

# 方式二：通过 ohpm 本地依赖（推荐生产环境）
# 在 oh-package.json5 中添加：
# "dependencies": { "common": "file:../common" }
```

### Step 3：配置应用信息（10 分钟）

**`AppScope/app.json5`**：

```json5
{
  "app": {
    "bundleName": "com.harmonystudio.thinkkit.flashcard",
    "vendor": "鸿蒙爆款工作室",
    "versionCode": 1000000,
    "versionName": "1.0.0",
    "icon": "$media:app_icon",
    "label": "$string:app_name"
  }
}
```

**`AppScope/resources/base/element/string.json`**：

```json
{
  "string": [
    { "name": "app_name", "value": "静·闪卡" },
    { "name": "app_desc", "value": "简约双向闪卡记忆工具" }
  ]
}
```

### Step 4：编写 app.config.ts（10 分钟）

```typescript
// app.config.ts — 每 App 独立配置
import { StorageService } from './common/storage/storageService';
import { STORAGE_KEYS } from './common/storage/keys';
import { lightTheme } from './common/theme/tokens';

export const AppConfig = {
  // 品牌信息
  appName: '静·闪卡',
  shortDesc: '简约双向闪卡记忆工具',
  trackName: 'ThinkKit',
  primaryColor: '#5B8C5A',

  // Feature Flag（赛马差异点）
  features: {
    enableFlashCard: true,       // 闪卡功能
    enableOutlineNote: false,    // 大纲笔记
    enableExportCSV: false,      // CSV 导出
    enableWeeklyReport: false,   // 周报
    enableBadge: false,          // 成就徽章
    enableCloudBackup: false,    // 云备份（V1 关闭）
  },

  // 存储配置
  storage: {
    notes: new StorageService<Note>(STORAGE_KEYS.NOTES),
  },

  // 主题
  defaultTheme: lightTheme,
};

// 导入数据模型（与其他页面共用）
export interface Note {
  id: string;
  title: string;
  body: string;
  tags: string[];
  isCard: boolean;
  createdAt: number;
}
```

### Step 5：注册页面路由（5 分钟）

**`entry/src/main/resources/base/profile/main_pages.json`**：

```json
{
  "src": [
    "pages/IndexPage",
    "pages/DetailPage",
    "pages/FormPage"
  ]
}
```

### Step 6：配置 EntryAbility（5 分钟）

```typescript
// entry/src/main/ets/entryability/EntryAbility.ts
import { UIAbility, Want, AbilityConstant } from '@kit.AbilityKit';
import { window } from '@kit.ArkUI';
import { StorageService } from '../common/storage/storageService';
import { AppConfig } from '../app.config';

export default class EntryAbility extends UIAbility {
  onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void {
    // 初始化存储
    StorageService.init(this.context);

    // 初始化主题
    AppStorage.SetOrCreate('theme', AppConfig.defaultTheme);
  }

  onWindowStageCreate(windowStage: window.WindowStage): void {
    windowStage.loadContent('pages/IndexPage', (err) => {
      if (err.code) {
        console.error('Failed to load content:', JSON.stringify(err));
      }
    });
  }
}
```

### Step 7：配置 module.json5 权限（3 分钟）

```json5
// entry/src/main/module.json5 — 权限声明模板
{
  "module": {
    "name": "entry",
    "type": "entry",
    "abilities": [
      {
        "name": "EntryAbility",
        "srcEntry": "./ets/entryability/EntryAbility.ts",
        "launchType": "singleton",
        "visible": true,
        "skills": [
          {
            "entities": ["entity.system.home"],
            "actions": ["action.system.home"]
          }
        ]
      }
    ],
    "extensionAbilities": [
      // 元服务卡片（如需要）
      {
        "name": "AppFormAbility",
        "srcEntry": "./ets/formability/FormAbility.ts",
        "type": "form",
        "metadata": [
          {
            "name": "ohos.extension.form",
            "resource": "$profile:form_config"
          }
        ]
      }
    ],
    "requestPermissions": [
      // 本地工具类 App 最小权限声明
      // 仅在需要网络功能时声明 INTERNET
      // {
      //   "name": "ohos.permission.INTERNET",
      //   "reason": "$string:internet_reason",
      //   "usedScene": { "abilities": ["EntryAbility"], "when": "inuse" }
      // }
    ]
  }
}
```

### Step 8：AI 生成页面 → Review → 跑真机

```powershell
# 1. 用 AI 提示词手册生成页面
# 2. 放入 pages/ 目录
# 3. 编译
hvigorw assembleHap --mode module -p product=default

# 4. 安装到真机
hdc install .\entry\build\default\outputs\default\entry-default-unsigned.hap

# 5. 测试：CRUD 操作 → 折叠屏 → 深色模式 → 返回键
```

---

## 三、app.config.ts 样板（Feature Flag 控制）

```typescript
// app.config.ts — 完整样板
import { StorageService } from './common/storage/storageService';
import { STORAGE_KEYS } from './common/storage/keys';
import { lightTheme, ThemeTokens } from './common/theme/tokens';

// ============================================================================
// 数据模型定义（统一在这里，所有页面 import from app.config）
// ============================================================================

export interface Note {
  id: string;
  title: string;
  body: string;
  tags: string[];
  isCard: boolean;
  createdAt: number;
  updatedAt: number;
}

export interface Habit {
  id: string;
  name: string;
  description: string;
  icon: string;
  color: string;
  targetDays: number;       // 目标连续天数
  createdAt: number;
}

// ============================================================================
// 应用配置
// ============================================================================

export const AppConfig = {
  // ---- 品牌 ----
  appName: '静·闪卡',
  shortDesc: '简约双向闪卡记忆工具',
  trackName: 'ThinkKit',     // 赛道标识

  // ---- Feature Flag ----
  features: {
    // 页面开关
    enableFlashCard: true,         // 闪卡模式
    enableOutlineNote: false,      // 大纲笔记
    enableNotebookFolder: false,   // 笔记本分组

    // 功能开关
    enableWeeklyReport: false,     // 周报统计
    enableExportCSV: false,        // CSV 导出
    enableBadge: false,            // 成就系统
    enableCloudBackup: false,      // 云同步
    enableAISummary: false,        // AI 摘要

    // 变现开关
    enableSubscription: false,     // IAP 订阅
    enableOneTimePurchase: true,   // 买断制
    showAds: false,                // 广告（永远 false）
  },

  // ---- 存储 ----
  storage: {
    notes: new StorageService<Note>(STORAGE_KEYS.NOTES),
    // habits: new StorageService<Habit>(STORAGE_KEYS.HABITS),
  },

  // ---- 主题 ----
  defaultTheme: lightTheme,

  // ---- 华为应用市场 ----
  store: {
    category: 'EDUCATION',
    keywords: '闪卡,记忆,复习,Anki替代,间隔重复,学习助手,鸿蒙原生,无广告',
  },
} as const;

// ============================================================================
// Feature Flag 辅助工具
// ============================================================================

/**
 * 检查指定 Feature 是否启用
 *
 * @example
 * if (isFeatureEnabled('enableFlashCard')) { /* 显示闪卡入口 *\/ }
 */
export function isFeatureEnabled(feature: keyof typeof AppConfig.features): boolean {
  return AppConfig.features[feature] === true;
}

/**
 * 获取启用的 Feature 列表（调试用）
 */
export function getEnabledFeatures(): string[] {
  return Object.entries(AppConfig.features)
    .filter(([, v]) => v === true)
    .map(([k]) => k);
}
```

**页面中使用 Feature Flag**：

```typescript
import { isFeatureEnabled } from '../app.config';

build() {
  Column() {
    // ...

    // 仅当该功能启用时才渲染
    if (isFeatureEnabled('enableFlashCard')) {
      Button('进入闪卡模式')
        .onClick(() => { /* ... */ })
    }
  }
}
```

---

## 四、module.json5 权限声明模板

### 完全离线 App（笔记/习惯打卡/极客工具）

```json5
{
  "requestPermissions": [
    // 本地工具 — 零权限声明
    // 仅保留注释，实际数组为空
  ]
}
```

### 含网络功能 App（模板下载、检查更新）

```json5
{
  "requestPermissions": [
    {
      "name": "ohos.permission.INTERNET",
      "reason": "$string:internet_reason",
      "usedScene": {
        "abilities": ["EntryAbility"],
        "when": "inuse"
      }
    }
  ]
}
```

### 含后台任务 App（番茄钟/专注计时）

```json5
{
  "requestPermissions": [
    {
      "name": "ohos.permission.KEEP_BACKGROUND_RUNNING",
      "reason": "$string:background_reason",
      "usedScene": {
        "abilities": ["EntryAbility"],
        "when": "always"
      }
    }
  ]
}
```

### 含元服务卡片 App

```json5
{
  "extensionAbilities": [
    {
      "name": "AppFormAbility",
      "srcEntry": "./ets/formability/FormAbility.ts",
      "type": "form",
      "metadata": [
        {
          "name": "ohos.extension.form",
          "resource": "$profile:form_config"
        }
      ]
    }
  ]
}
```

---

## 五、快速检查清单（新建 App 后）

- [ ] bundleName 唯一，不与现有 App 重复
- [ ] AppScope/app.json5 应用名与备案一致
- [ ] common/ 已正确引入，import 路径无报错
- [ ] app.config.ts Feature Flag 已按赛道设定
- [ ] main_pages.json 包含所有页面路径
- [ ] EntryAbility 中调用了 StorageService.init()
- [ ] EntryAbility 中注入了 AppConfig.defaultTheme
- [ ] module.json5 仅声明必要权限
- [ ] resources/base/media/ 包含 app_icon.png
- [ ] 编译通过（hvigorw assembleHap）
- [ ] 真机安装成功并完成 CRUD 测试
