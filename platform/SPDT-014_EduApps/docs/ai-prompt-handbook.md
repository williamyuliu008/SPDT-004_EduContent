# AI 提示词手册 — 鸿蒙爆款App工作室

> 适用版本：HarmonyOS NEXT / ArkTS + ArkUI Stage 模型  
> 建议模型：Claude 4 / GPT-4o / DeepSeek-V3 / DevEco CodeGenie  
> 本文档供团队开发人员使用——把每个模板复制到 AI 对话中，填入页面规格即可生成代码

---

## 一、通用约束（每次对话必须带上）

```
你是精通 HarmonyOS NEXT（ArkTS + ArkUI Stage 模型）的高级移动端开发。

🚨 强制规则：
1. 禁止使用 any 类型，所有变量/参数必须显式标注类型
2. 所有颜色、字号、间距从 theme tokens 读取，禁止硬编码 #xxxxxx
3. 优先使用 common/components 下的 HButton / HCard / HEmptyState / HFormItem / HProgressBar / HToast
4. 存储操作通过 StorageService<T>，不直接操作 preferences API
5. 使用 @State / @Link / @Prop / @Provide-@Consume 管理状态
6. 路由使用 Navigation + NavPathStack（非 router.pushUrl）
7. 变量名/函数名用英文，注释用中文
8. 遵循 Stage 模型生命周期：aboutToAppear / aboutToDisappear
9. 所有文本使用 $r('app.string.xxx') 资源引用（若未设置资源文件则用字符串，注释标注）
10. 点击热区最小 40vp × 40vp
```

---

## 二、页面类型提示词模板

### 2.1 列表页（ListPage）

**场景描述**：展示数据列表，支持搜索/筛选、跳转详情、空状态、FAB 新建

**提示词**：

````
生成 ListPage.ets：

功能要求：
- 顶部 Search 组件（placeholder='搜索...'）+ 可选标签筛选栏
- List 渲染数据条目，每个条目包含：标题(加粗)、副标题(灰色小字)、右侧辅助文字
- 条目使用 HCard 组件（从 '../common/components/HCard' 导入）
- 点击条目跳转详情页：router.pushUrl({ url: 'pages/DetailPage', params: { id: item.id } })
- 列表为空时显示 HEmptyState（message='暂无数据', actionLabel='新建', onAction=跳转新建页）
- 右下角 FAB 按钮跳转新建页，使用 HButton（type='primary'）
- 从 StorageService 加载真实数据（勿用假数据）
- 使用 @State 管理列表数据，onPageShow 时重新加载

技术约束：
- 布局：Column > Search/FilterRow + List(使用LazyForEach)
- List 条目需设置 .onClick() 跳转
- 禁止 any，所有回调显式标注类型

仅输出代码，用 ```ets 包裹。
````

**预期输出**：一个完整的 ListPage.ets，包含搜索栏、条件筛选、LazyForEach 列表、空状态、FAB

---

### 2.2 详情页（DetailPage）

**场景描述**：展示单条数据的完整信息，支持编辑/删除操作

**提示词**：

````
生成 DetailPage.ets：

功能要求：
- 通过 router.getParams() 获取 id
- 从 StorageService 按 id 加载数据，存入 @State
- 顶部 NavBar：返回按钮 + 标题 + 编辑/删除图标按钮
- 内容区：标题(大字号)、创建时间(灰色)、正文内容
- 底部：编辑按钮(HButton type='primary') + 删除按钮(HButton type='ghost')
- 支持下拉刷新 onRefresh
- 删除前弹窗确认 AlertDialog.show()
- 编辑后 router.back() 回到列表页刷新

技术约束：
- 使用 aboutToAppear 加载数据
- 禁止 any，数据模型显式 import

仅输出代码，用 ```ets 包裹。
````

**预期输出**：DetailPage.ets，包含数据加载、NavBar、内容展示、编辑/删除操作

---

### 2.3 表单页（FormPage）

**场景描述**：新建或编辑数据记录

**提示词**：

````
生成 FormPage.ets（新建/编辑）：

功能要求：
- 路由取 params.id（有 = 编辑，无 = 新建）
- 使用 HFormItem 组件构建表单字段（标题、内容、标签、开关等）
- 表单字段：
  1. 标题 TextInput（必填，maxLength=80，validator=非空校验）
  2. 正文 TextArea（选填，height=200）
  3. 标签 TextInput（逗号分隔，onChange 转数组）
  4. 选项 Toggle/Checkbox（按需）
- 保存按钮使用 HButton(type='primary')，loading 态
- onBackPress 拦截：若内容已修改，弹窗确认是否放弃
- 保存时调用 StorageService.save()，保存后 router.back()
- 编辑模式：先加载已有数据填充表单

技术约束：
- 从 '../common/components/HFormItem' 导入 HFormItem
- 从 '../common/utils/validate' 导入校验函数
- 禁止 any

仅输出代码，用 ```ets 包裹。
````

**预期输出**：FormPage.ets，包含表单字段、校验、保存逻辑、返回拦截

---

### 2.4 设置页（SettingsPage）

**场景描述**：App 设置面板（主题切换、关于、反馈等）

**提示词**：

````
生成 SettingsPage.ets：

功能要求：
- 分组列表（使用 List + ListItemGroup）：
  1. 【外观】主题选择（浅色/深色/护眼）、字体大小
  2. 【数据】导出数据、清除所有数据(AlertDialog确认)
  3. 【关于】版本号、隐私政策链接、用户协议链接、反馈邮箱
- 主题切换：调用 AppStorage.Set('theme', newTheme)
- 清除数据：调用所有 StorageService 实例的 clear()
- 使用 HCard 作为每组的容器
- 列表项使用 Row（左侧 label + 右侧 value/开关）

技术约束：
- 从 '../common/theme/tokens' 导入 ALL_THEMES / ALL_THEME_NAMES
- 禁止 any

仅输出代码，用 ```ets 包裹。
````

**预期输出**：SettingsPage.ets，包含主题切换、数据管理、关于信息

---

### 2.5 空状态页（EmptyState 组件调用）

**场景描述**：在列表/页面中嵌入空状态占位

**提示词**：

````
在现有的 ListPage 中添加空状态逻辑：

- 当 @State dataList 长度为 0 时，显示 HEmptyState
- HEmptyState props：
  - message: '还没有笔记' （根据页面类型调整）
  - description: '点击下方按钮创建第一条记录'
  - actionLabel: '新建'
  - onAction: 跳转新建页
- 当 dataList.length > 0 时，显示 List

代码片段示例：

if (this.dataList.length === 0) {
  HEmptyState({
    message: '还没有笔记',
    description: '点击下方按钮创建第一条记录',
    actionLabel: '新建笔记',
    onAction: () => { router.pushUrl({ url: 'pages/NoteEditPage' }) }
  })
} else {
  List() { /* ... */ }
}
````

---

## 三、组件/功能类型提示词模板

### 3.1 CRUD 存储操作

**场景描述**：对数据进行增删改查，基于 StorageService

**提示词**：

````
基于 StorageService<T> 实现 CRUD：

1. 导入 StorageService 和 STORAGE_KEYS：
   import { StorageService } from '../common/storage/storageService';
   import { STORAGE_KEYS } from '../common/storage/keys';

2. 在 EntryAbility 中初始化：
   StorageService.init(this.context);

3. 创建存储实例：
   const store = new StorageService<ItemType>(STORAGE_KEYS.XXX);

4. CRUD 操作：
   - 查询：const items = await store.getAll();
   - 新增/更新：await store.save(item, (i) => i.id);
   - 删除：await store.delete(id, (i) => i.id);
   - 清空：await store.clear();

5. 页面中用法：
   - aboutToAppear: 加载数据
   - onPageShow: 重新加载（从详情/编辑页返回时刷新）

生成包含完整错误处理的代码。禁止 any，ItemType 需显式 import。
````

---

### 3.2 状态管理

**场景描述**：父子组件通信、跨页面状态共享

**提示词**：

````
HarmonyOS NEXT ArkTS 状态管理最佳实践：

1. 父子组件单向传递：@Prop（子组件接收，只读）
2. 父子组件双向绑定：@Link（子组件可写回父组件）
3. 爷孙/跨层级：@Provide + @Consume
4. 全局配置：AppStorage（存储 theme、用户偏好）
5. 本地 UI 状态：@State
6. 禁止使用全局单例管理业务状态

示例场景：
- ListPage @State items → ListItem @Prop item
- FormPage @State formData → HFormItem @Link value
- ThemeSwitch → @Consume theme → 子组件自动响应

生成一个包含 @Provide-@Consume 的父子页面示例，禁止 any。
````

---

### 3.3 路由跳转

**场景描述**：页面间导航与参数传递

**提示词**：

````
HarmonyOS NEXT 路由跳转模板（Navigation + NavPathStack）：

1. 在 EntryView 中配置：
   @Provide navPathStack: NavPathStack = new NavPathStack();
   Navigation(this.navPathStack) { /* 页面内容 */ }

2. 跳转并传参：
   this.navPathStack.pushPathByName('DetailPage', { id: item.id });

3. 目标页面接收参数：
   @Consume navPathStack: NavPathStack;
   aboutToAppear() {
     const params = this.navPathStack.getParamByName('DetailPage');
     this.id = params?.[0]?.id as string ?? '';
   }

4. 返回上一页：
   this.navPathStack.pop();

5. 返回到根页面：
   this.navPathStack.clear();

6. 在 main_pages.json 中注册所有页面路径。

生成完整配置代码。不允许使用旧版 router.pushUrl。
````

---

### 3.4 权限声明

**场景描述**：在 module.json5 中声明权限

**提示词**：

````
HarmonyOS NEXT 权限声明模板：

在实际需要时才声明权限，最小化原则。

1. 在 module.json5 的 requestPermissions 中添加：
   {
     "name": "ohos.permission.INTERNET",
     "reason": "$string:internet_reason",
     "usedScene": { "abilities": ["EntryAbility"], "when": "inuse" }
   }

2. 在 resources/base/element/string.json 中添加权限理由：
   { "name": "internet_reason", "value": "用于获取在线模板和检查更新" }

3. 动态申请（仅敏感权限需要）：
   import abilityAccessCtrl from '@ohos.abilityAccessCtrl';
   const atManager = abilityAccessCtrl.createAtManager();
   await atManager.requestPermissionsFromUser(context, ['ohos.permission.XXX']);

4. 本地工具类 App 建议声明：
   - ohos.permission.INTERNET（仅需网络功能时）
   - ohos.permission.KEEP_BACKGROUND_RUNNING（番茄钟等计时场景）

其他权限一律不声明。生成完整 module.json5 权限区块。
````

---

### 3.5 网络请求

**场景描述**：HTTP 请求封装（云端模板下载、检查更新等）

**提示词**：

````
HarmonyOS NEXT 网络请求模板（@ohos.net.http）：

import http from '@ohos.net.http';

class ApiService {
  private baseUrl: string = 'https://api.example.com';

  async get<T>(path: string): Promise<T | null> {
    try {
      const req = http.createHttp();
      const resp = await req.request(`${this.baseUrl}${path}`, {
        method: http.RequestMethod.GET,
        connectTimeout: 10000,
        readTimeout: 15000,
      });
      req.destroy();
      if (resp.responseCode === 200) {
        return JSON.parse(resp.result.toString()) as T;
      }
      console.error(`HTTP ${resp.responseCode}: ${resp.result}`);
      return null;
    } catch (err) {
      console.error('网络请求失败:', JSON.stringify(err));
      return null;
    }
  }

  async post<T>(path: string, body: object): Promise<T | null> {
    // 类似 get，method 改为 POST，extraData 传入 body
  }
}

注意：
1. 必须在请求结束后调用 req.destroy() 释放资源
2. 所有网络调用必须 try/catch
3. 敏感数据不上传（本地工具类通常不需要网络层）
4. 需要在 module.json5 中声明 ohos.permission.INTERNET

生成完整代码，禁止 any，T 显式泛型约束。
````

---

## 四、让 AI 严格引用 common/ 组件的技巧

### 🎯 技巧 1：在提示词开头声明组件路径

```
你可以使用以下组件（已存在，不要重复定义）：
- HButton from '../common/components/HButton'   → Props: label, type('primary'|'secondary'|'ghost'), loading, disabled, onTap
- HCard from '../common/components/HCard'       → Props: title, subtitle, trailing, icon, swipeEnabled, onTap, onSwipeAction
- HEmptyState from '../common/components/HEmptyState' → Props: message, description, actionLabel, onAction
- HFormItem from '../common/components/HFormItem' → Props: label, value, placeholder, type, validator, onChange
- HProgressBar from '../common/components/HProgressBar' → Props: current, total, type('linear'|'segments'), segments, completedSegments
- HToast from '../common/components/HToast'     → 静态方法: HToast.show({ message, type, duration })
```

### 🎯 技巧 2：用具体示例代替抽象描述

❌ 差：`"添加一个按钮"`  
✅ 好：`"使用 HButton({ label: '保存', type: 'primary', onTap: () => { this.save() } })"`

### 🎯 技巧 3：给 AI 看"不要做什么"

在提示词末尾追加：

```
❌ 不要做的事：
- 不要使用系统原始 Button/TextInput（用 HButton/HFormItem 替代）
- 不要硬编码颜色（从 @StorageProp('theme') 读取）
- 不要直接操作 preferences（用 StorageService）
- 不要使用 router.pushUrl（用 NavPathStack）
- 不要使用 any 类型
- 不要生成重复的组件定义
```

### 🎯 技巧 4：分步生成，每步 Review

1. 先让 AI 生成 Model interface → Review
2. 再生成 Storage 调用 → Review
3. 逐页生成 → Review
4. 最后生成路由配置

---

## 五、禁止的做法清单（AI 容易犯的错）

| 错误 | 说明 | 正确做法 |
|------|------|----------|
| 使用 `any` 类型 | AI 习惯偷懒 | 显式定义 `interface` 并 import |
| 硬编码颜色 `#5B8C5A` | 导致换肤失效 | `this.theme?.primary ?? '#5B8C5A'` |
| 直接 `new preferences.getPreferences()` | API 废弃，Stage 模型不兼容 | 用 `StorageService.init(this.context)` |
| `router.pushUrl` | 已废弃 | 用 `Navigation` + `NavPathStack` |
| `@State` 滥用所有变量 | 性能下降 | 仅 UI 需要双向绑定的用 @State，其余用普通变量 |
| `JSON.parse` 无类型断言 | 类型丢失 | `JSON.parse(str) as Note[]` |
| `ForEach` 大量数据 | 长列表卡顿 | 改用 `LazyForEach` + `DataSource` |
| 忘记 `req.destroy()` | 内存泄漏 | 网络请求 finally 块中释放 |
| setInterval 未 clear | 页面退出后定时器仍在跑 | 在 `aboutToDisappear` 中 `clearInterval` |
| 忽略 onBackPress | 编辑页返回数据丢失 | 拦截返回键，弹窗确认或自动保存 |

---

## 六、快速参考卡

### 常用 import 路径

```typescript
// 组件
import { HButton } from '../common/components/HButton';
import { HCard } from '../common/components/HCard';
import { HEmptyState } from '../common/components/HEmptyState';
import { HFormItem } from '../common/components/HFormItem';
import { HProgressBar } from '../common/components/HProgressBar';
import { HToast } from '../common/components/HToast';

// 存储
import { StorageService } from '../common/storage/storageService';
import { STORAGE_KEYS } from '../common/storage/keys';

// 主题
import { lightTheme, darkTheme, eyeCareTheme, autoTheme } from '../common/theme/tokens';

// 工具
import { formatDate, timeAgo, getWeekday, isSameDay } from '../common/utils/date';
import { formatNumber, formatCurrency, formatDuration } from '../common/utils/format';
import { isNotEmpty, lengthBetween, isValidEmail, isValidPhone, validateAll } from '../common/utils/validate';

// 算法
import { SM2, SM2Quality } from '../common/algo/sm2';
import { StreakCalculator } from '../common/algo/streak';
```

### 常用代码片段

```typescript
// 读取主题
@StorageProp('theme') theme: ThemeTokens | null = null;

// 加载数据
aboutToAppear(): void {
  this.loadData();
}
private async loadData(): Promise<void> {
  this.dataList = await this.store.getAll();
}

// Toast 提示
import { HToast } from '../common/components/HToast';
HToast.show({ message: '保存成功', type: 'success' });

// 空状态判断
if (this.dataList.length === 0) {
  HEmptyState({ message: '暂无数据', actionLabel: '新建', onAction: () => { /* ... */ } })
}

// 删除确认
AlertDialog.show({
  title: '确认删除',
  message: '删除后不可恢复',
  buttons: [
    { text: '取消', color: '#888888' },
    { text: '删除', color: '#FF3B30', action: () => { /* delete logic */ } }
  ]
});
```
