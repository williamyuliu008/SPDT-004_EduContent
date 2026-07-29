# Common 内核规范文档 (Kernel Specification)

> 版本：1.0.0 | 更新：2026-06-16 | 维护：模块库管理 (agent-6z1oi)

---

## 一、概述

Common 内核是鸿蒙工坊所有 App 的共享基础库，提供 **12 个 UI 组件 + 存储层 + 主题系统 + 9 个工具函数 + 2 个算法**。所有 App 通过 `import { ... } from './common'` 统一引入。

### 设计原则

| 原则 | 说明 |
|------|------|
| **零硬编码** | 颜色/字号/间距/圆角 100% 从 ThemeTokens 读取 |
| **禁止 any** | 所有类型显式标注，编译期捕获错误 |
| **本地优先** | 基于 Preferences 的纯本地存储，零网络依赖 |
| **组件自包含** | 每个组件独立可用，不依赖全局状态（除 theme） |
| **渐进增强** | Feature Flag 控制功能开关，同内核跑不同 App |

---

## 二、组件 API 参考

### 2.1 HButton — 标准化按钮

```typescript
import { HButton } from './common';
```

| Prop | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `label` | `string` | `''` | 按钮文字（必填） |
| `type` | `'primary' \| 'secondary' \| 'ghost'` | `'primary'` | 按钮样式 |
| `size` | `'small' \| 'medium' \| 'large'` | `'medium'` | 按钮尺寸 |
| `disabled` | `boolean` | `false` | 是否禁用 |
| `loading` | `boolean` | `false` | 是否加载中（自动禁用点击） |
| `fullWidth` | `boolean` | `false` | 是否撑满父容器 |
| `onTap` | `() => void` | — | 点击回调 |

```typescript
// 示例
HButton({ label: '保存', type: 'primary', onTap: () => { this.save() } })
HButton({ label: '提交中...', type: 'secondary', loading: true })
HButton({ label: '已删除', type: 'ghost', disabled: true })
```

---

### 2.2 HCard — 卡片容器

```typescript
import { HCard } from './common';
```

| Prop | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `title` | `string` | `''` | 卡片标题（必填） |
| `subtitle` | `string` | `''` | 副标题 |
| `icon` | `Resource` | — | 左侧图标（可选） |
| `trailing` | `string` | `''` | 右侧辅助文字 |
| `enabled` | `boolean` | `true` | 是否可点击 |
| `swipeEnabled` | `boolean` | `false` | 是否支持右滑操作 |
| `swipeActionLabel` | `string` | `'删除'` | 右滑操作文案 |
| `swipeActionColor` | `string` | `'#FF3B30'` | 右滑操作区颜色 |
| `onTap` | `() => void` | — | 点击回调 |
| `onSwipeAction` | `() => void` | — | 右滑操作回调 |

```typescript
// 基础卡片
HCard({ title: '笔记标题', subtitle: '2小时前', onTap: () => { ... } })

// 右滑删除
HCard({
  title: '临时笔记',
  swipeEnabled: true,
  swipeActionLabel: '删除',
  onSwipeAction: () => { this.deleteNote(id) }
})
```

---

### 2.3 HEmptyState — 空状态占位

```typescript
import { HEmptyState } from './common';
```

| Prop | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `message` | `string` | `''` | 提示文案（必填） |
| `description` | `string` | `''` | 补充说明 |
| `actionLabel` | `string` | `''` | 操作按钮文案 |
| `icon` | `Resource` | — | 自定义图标 |
| `onAction` | `() => void` | — | 按钮点击回调 |

```typescript
// 纯提示
HEmptyState({ message: '还没有笔记' })

// 带操作
HEmptyState({
  message: '还没有习惯',
  description: '点击下方按钮创建第一个习惯',
  actionLabel: '添加习惯',
  onAction: () => { router.pushUrl({ url: 'pages/FormPage' }) }
})
```

---

### 2.4 HFormItem — 表单项

```typescript
import { HFormItem } from './common';
```

| Prop | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `label` | `string` | `''` | 标签文字（必填） |
| `value` | `string` (@Link) | — | 双向绑定值 |
| `placeholder` | `string` | `'请输入'` | 占位文字 |
| `type` | `'text' \| 'textarea' \| 'number'` | `'text'` | 字段类型 |
| `maxLength` | `number` | `200` | 最大长度 |
| `required` | `boolean` | `false` | 是否必填（显示红色*） |
| `errorMessage` | `string` | — | 外部错误信息 |
| `onChange` | `(value: string) => void` | — | 值变更回调 |
| `validator` | `(value: string) => string \| null` | — | 自定义校验器 |

```typescript
// 基础输入
HFormItem({
  label: '标题',
  value: $title,
  placeholder: '请输入标题',
  required: true,
  onChange: (val: string) => { this.title = val }
})

// 带校验
HFormItem({
  label: '邮箱',
  value: $email,
  validator: (val: string) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val) ? null : '邮箱格式不正确'
})
```

---

### 2.5 HProgressBar — 进度条

```typescript
import { HProgressBar } from './common';
```

| Prop | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `current` | `number` | `0` | 当前值 |
| `total` | `number` | `1` | 最大值 |
| `type` | `'linear' \| 'segments'` | `'linear'` | 线性/分段 |
| `segments` | `number` | `7` | 分段数（type=segments 时） |
| `completedSegments` | `number` | `0` | 已完成分段数 |
| `showLabel` | `boolean` | `true` | 显示文字标签 |
| `showAnimation` | `boolean` | `true` | 播放动画 |
| `color` | `string` | — | 进度条颜色 |
| `labelFormat` | `'percent' \| 'fraction'` | `'fraction'` | 文字格式 |

```typescript
// 线性进度
HProgressBar({ current: 3, total: 10 })

// 习惯打卡（7天分段）
HProgressBar({
  type: 'segments',
  segments: 7,
  completedSegments: 5,
  labelFormat: 'fraction'
})
```

---

### 2.6 HToast — 轻提示

```typescript
import { HToast } from './common';

// 静态方法调用，无需实例化
HToast.show({ message: '保存成功', type: 'success' })
HToast.show({ message: '网络错误', type: 'error', duration: 3000 })
HToast.show({ message: '标题不能为空', type: 'warning', position: 'top' })
HToast.hide()  // 手动隐藏
```

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `message` | `string` | — | 提示文字（必填） |
| `type` | `'info' \| 'success' \| 'warning' \| 'error'` | `'info'` | 提示类型 |
| `duration` | `number` | `2000` | 显示时长(ms) |
| `position` | `'top' \| 'center' \| 'bottom'` | `'center'` | 显示位置 |

---

### 2.7 HNavBar — 导航栏

```typescript
import { HNavBar, NavBarAction } from './common';

// 可选的右侧操作按钮
const actions: NavBarAction[] = [
  { icon: $r('app.media.ic_edit'), onTap: () => { this.edit() } },
  { icon: $r('app.media.ic_delete'), onTap: () => { this.confirmDelete() } }
];
```

| Prop | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `title` | `string` | `''` | 标题文字（必填） |
| `showBack` | `boolean` | `true` | 显示返回按钮 |
| `backLabel` | `string` | `''` | 返回按钮文字 |
| `rightActions` | `NavBarAction[]` | — | 右侧操作按钮组 |
| `backgroundColor` | `string` | — | 背景色 |
| `onBack` | `() => void` | — | 返回回调 |

---

### 2.8 HSearchBar — 搜索栏

```typescript
import { HSearchBar } from './common';

// value 使用 @Link 双向绑定
HSearchBar({
  placeholder: '搜索笔记...',
  value: $keyword,
  debounceMs: 300,
  onChange: (val: string) => { this.filter(val) },
  onCancel: () => { this.showSearch = false }
})
```

| Prop | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `placeholder` | `string` | `'搜索'` | 占位文字 |
| `value` | `string` (@Link) | — | 当前输入值（双向绑定） |
| `debounceMs` | `number` | `300` | 防抖延迟(ms)，0=不防抖 |
| `showCancel` | `boolean` | `true` | 显示取消按钮 |
| `onChange` | `(value: string) => void` | — | 输入变更回调 |
| `onSearch` | `(value: string) => void` | — | 搜索提交回调 |
| `onCancel` | `() => void` | — | 取消回调 |

---

### 2.9 HConfirmDialog — 确认弹窗

```typescript
import { HConfirmDialog } from './common';

// 危险操作确认
HConfirmDialog.show({
  title: '确认删除',
  message: '删除后不可恢复，确定吗？',
  danger: true,
  onConfirm: () => { this.deleteNote() }
})

// 信息提示（单按钮）
HConfirmDialog.alert('提示', '保存成功', '知道了')
```

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `title` | `string` | — | 弹窗标题（必填） |
| `message` | `string` | — | 弹窗内容（必填） |
| `confirmLabel` | `string` | `'确定'` | 确认按钮文字 |
| `cancelLabel` | `string` | `'取消'` | 取消按钮文字 |
| `danger` | `boolean` | `true` | 危险操作（确认按钮变红） |
| `onConfirm` | `() => void` | — | 确认回调 |
| `onCancel` | `() => void` | — | 取消回调 |

---

### 2.10 HTag — 标签

```typescript
import { HTag } from './common';

HTag({ label: '技术', selected: true, onTap: () => { ... } })
HTag({ label: '鸿蒙', removable: true, onRemove: () => { this.removeTag('鸿蒙') } })
```

| Prop | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `label` | `string` | `''` | 标签文字 |
| `selected` | `boolean` | `false` | 选中态 |
| `color` | `string` | — | 自定义颜色 |
| `size` | `'small' \| 'medium'` | `'medium'` | 尺寸 |
| `removable` | `boolean` | `false` | 显示删除按钮 |
| `onTap` | `() => void` | — | 点击回调 |
| `onRemove` | `() => void` | — | 删除回调 |

---

### 2.11 HTagGroup — 标签组（多选/单选）

```typescript
import { HTagGroup, TagItem } from './common';

const tags: TagItem[] = [
  { id: 'all', label: '全部' },
  { id: 'tech', label: '技术' },
  { id: 'life', label: '生活' }
];

// 单选模式
HTagGroup({ tags, selectedIds: $category, onChange: (ids) => { this.filter(ids) } })

// 多选模式
HTagGroup({ tags, selectedIds: $tags, multiSelect: true, onChange: (ids) => { ... } })
```

| Prop | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `tags` | `TagItem[]` | `[]` | 标签列表 |
| `selectedIds` | `string[]` (@Link) | — | 选中标签 ID 列表 |
| `multiSelect` | `boolean` | `false` | 多选模式 |
| `onChange` | `(ids: string[]) => void` | — | 选中变更回调 |

---

### 2.12 HFAB — 浮动操作按钮

```typescript
import { HFAB } from './common';

HFAB({ onTap: () => { this.navPathStack.pushPathByName('FormPage', undefined) } })
HFAB({ label: '新建笔记', onTap: () => { this.createNote() } })
HFAB({ icon: $r('app.media.ic_add'), position: 'bottomCenter', onTap: () => { ... } })
```

| Prop | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `icon` | `Resource` | — | 图标（默认显示 +） |
| `label` | `string` | `''` | 扩展标签文字 |
| `position` | `'bottomRight' \| 'bottomCenter'` | `'bottomRight'` | 屏幕位置 |
| `color` | `string` | — | 按钮颜色 |
| `onTap` | `() => void` | — | 点击回调（必填） |

---

## 三、存储层 API

### StorageService\<T\>

```typescript
import { StorageService, STORAGE_KEYS } from './common';

// 1. 在 EntryAbility 中初始化（仅一次）
StorageService.init(this.context);

// 2. 创建存储实例
interface Note { id: string; title: string; body: string; }
const noteStore = new StorageService<Note>(STORAGE_KEYS.NOTES);

// 3. CRUD
const notes: Note[] = await noteStore.getAll();
await noteStore.save(newNote, (n) => n.id);    // upsert
await noteStore.saveAll(filteredNotes);         // 批量替换
await noteStore.delete(noteId, (n) => n.id);    // 按 ID 删除
await noteStore.clear();                        // 清空
```

### STORAGE_KEYS 常量

| Key | 用途 | 所属赛道 |
|-----|------|---------|
| `NOTES` | 笔记/闪卡数据 | ThinkKit |
| `FLASHCARD_PROGRESS` | SM-2 复习进度 | ThinkKit |
| `HABITS` | 习惯定义 | RhythmLife |
| `HABIT_CHECKINS` | 打卡记录 | RhythmLife |
| `FOCUS_SESSIONS` | 专注计时 | RhythmLife |
| `SUBSCRIPTIONS` | 订阅追踪 | 财务 |
| `DEV_TOOLS_PREFS` | 极客工具偏好 | CraftsmanUtils |
| `APP_SETTINGS` | 全局设置 | 通用 |

---

## 四、主题系统

### 三套内置主题

```typescript
import { lightTheme, darkTheme, eyeCareTheme, autoTheme, ALL_THEMES, ALL_THEME_NAMES } from './common';

// 自动跟随系统
AppStorage.Set('theme', autoTheme(systemIsDark));

// 手动切换
AppStorage.Set('theme', darkTheme);

// 设置页展示
ALL_THEME_NAMES  // → { light: '浅色', dark: '深色', eyeCare: '护眼' }
```

### 组件中使用主题

```typescript
@StorageProp('theme') theme: ThemeTokens | null = null;

// 使用 token（带 fallback）
.backgroundColor(this.theme?.surface ?? '#FFFFFF')
.fontSize(this.theme?.fontSizeBody ?? 14)
.fontColor(this.theme?.onSurface ?? '#1C1C1E')
```

### ThemeTokens 完整字段

| 分类 | 字段 | 类型 | 说明 |
|------|------|------|------|
| 颜色 | `primary` | `string` | 主色 |
| | `primaryVariant` | `string` | 主色变体 |
| | `secondary` | `string` | 辅色 |
| | `background` | `string` | 页面背景 |
| | `surface` | `string` | 卡片/表面 |
| | `surfaceVariant` | `string` | 表面变体 |
| | `onPrimary` | `string` | 叠加在主色上的文字色 |
| | `onSurface` | `string` | 叠加在表面上的文字色 |
| | `outline` | `string` | 边框色 |
| | `error` | `string` | 错误色 |
| | `success` | `string` | 成功色 |
| | `warning` | `string` | 警告色 |
| 圆角 | `radiusSmall/Medium/Large` | `number` | 8/12/20 |
| 字号 | `fontSizeCaption/Body/Subtitle/Title/Heading` | `number` | 12/14/16/18/24 |
| 字重 | `fontWeightRegular/Medium/Bold` | `number` | 400/500/700 |
| 间距 | `spacingXs/Small/Medium/Large/Xl` | `number` | 4/8/12/16/24 |
| 阴影 | `shadowCard/Dialog/Button` | `ShadowOptions` | — |
| 动画 | `animationDurationShort/Medium/Long` | `number` | 180/350/550ms |

---

## 五、工具函数

### date.ts

| 函数 | 签名 | 说明 |
|------|------|------|
| `formatDate` | `(date, format) => string` | 格式化日期 `YYYY-MM-DD HH:mm` |
| `timeAgo` | `(date, now?) => string` | 相对时间：`刚刚/5分钟前/2天前` |
| `getWeekday` | `(date, lang?) => string` | 星期名称 `'星期二'` / `'Tue'` |
| `isSameDay` | `(a, b?) => boolean` | 同一天判断 |
| `getWeekRange` | `(date) => {start, end}` | 所在周的起止日期 |
| `daysBetween` | `(a, b) => number` | 天数差 |
| `daysInMonth` | `(year, month) => number` | 月天数 |

### format.ts

| 函数 | 签名 | 说明 |
|------|------|------|
| `formatNumber` | `(value, decimals?) => string` | 千分位 `1,234,567` |
| `formatCurrency` | `(value, symbol?) => string` | 货币 `¥1,999.00` |
| `formatPercent` | `(value, decimals?) => string` | 百分比 `85.7%` |
| `formatFileSize` | `(bytes) => string` | 文件大小 `1.0 MB` |
| `formatDuration` | `(seconds, format?) => string` | 时长 `01:05` / `1小时5分钟` |
| `abbreviateNumber` | `(value) => string` | 缩写 `1.2万` / `1.2亿` |
| `padZero` | `(value, length) => string` | 补零 `05` |

### validate.ts

| 函数 | 签名 | 说明 |
|------|------|------|
| `isNotEmpty` | `(value, fieldName?) => ValidationResult` | 非空校验 |
| `lengthBetween` | `(value, min, max, fieldName?) => ValidationResult` | 长度校验 |
| `isValidEmail` | `(email) => ValidationResult` | 邮箱格式 |
| `isValidPhone` | `(phone) => ValidationResult` | 手机号格式 |
| `isValidUrl` | `(url) => ValidationResult` | URL 格式 |
| `isStrongPassword` | `(password) => ValidationResult` | 密码强度 |
| `numberInRange` | `(value, min, max, fieldName?) => ValidationResult` | 数字范围 |
| `validateAll` | `(value, validators[]) => ValidationResult` | 组合校验 |

### id.ts

| 函数 | 签名 | 说明 |
|------|------|------|
| `generateId` | `(prefix?) => string` | 唯一 ID `note_l3m5k7n9p2q4` |
| `shortId` | `(length?) => string` | 短 ID `a1b2c3d4` |

### debounce.ts

| 函数 | 签名 | 说明 |
|------|------|------|
| `debounce` | `(fn, delay?) => (...args) => void` | 防抖（搜索输入） |
| `throttle` | `(fn, interval?) => (...args) => void` | 节流（按钮防连点） |

---

## 六、算法库

### SM-2 间隔重复

```typescript
import { SM2, SM2Quality } from './common';

let card = SM2.create();
card = SM2.review(card, SM2Quality.PERFECT);  // 评分 0-5
if (SM2.isDue(card)) { /* 该复习了 */ }
SM2.getDueDescription(card);  // → '明天复习' | '已过期2天'
SM2.getStats(allCards);       // → { total, newCards, dueCards, learned }
```

### StreakCalculator 连续打卡

```typescript
import { StreakCalculator } from './common';

const result = StreakCalculator.calculate(checkinTimestamps);
// → { current: 5, longest: 12, todayDone: false, totalDays: 30 }

StreakCalculator.getWeekHeatmap(checkins);
// → [false, true, true, false, true, true, false]  // 最近7天
```

---

## 七、Feature Flag 机制

每个 App 通过 `app.config.ts` 定义 Feature Flag，页面中条件渲染：

```typescript
import { isFeatureEnabled } from '../app.config';

build() {
  Column() {
    if (isFeatureEnabled('enableFlashCard')) {
      Button('进入闪卡模式').onClick(() => { ... })
    }
    if (isFeatureEnabled('enableOutlineNote')) {
      this.buildOutlineView()
    }
  }
}
```

### 新增 App 时的 Feature Flag 命名规范

- 格式：`enable{FeatureName}`
- 默认值：`false`（显式 opt-in）
- 同一赛道的多个 App 通过 Flag 差异化

---

## 八、Import 路径约定

```
App 根目录/
├── app.config.ts          → import from './common/...'
├── common/                → 内部使用相对路径（../components/...）
└── entry/src/main/ets/
    ├── entryability/      → import from '../../../../common/...'
    └── pages/             → import from '../../../../common/...'
```

**推荐**：所有 App 页面统一从 barrel export 引入：

```typescript
// ✅ 推荐：一次 import
import { HButton, HCard, StorageService, generateId, lightTheme } from '../../../../common';

// ❌ 避免：分散 import
import { HButton } from '../../../../common/components/HButton';
import { StorageService } from '../../../../common/storage/storageService';
```
