/**
 * theme/tokens.ts — Design Token 主题系统
 *
 * ============================================================================
 * 设计理念
 * ============================================================================
 * 1. 所有颜色、字号、间距、圆角、阴影均从此文件导出，禁止在组件中硬编码
 * 2. 提供 3 套完整主题：浅色（light）、深色（dark）、护眼（eyeCare）
 * 3. 通过 AppStorage 全局注入当前主题，组件通过 @StorageProp('theme') 读取
 * 4. 支持运行时动态切换主题（深色模式跟随系统 / 用户手动选择）
 *
 * ============================================================================
 * 用法示例
 * ============================================================================
 * // 1. 在 EntryAbility 中注入默认主题
 * import { lightTheme, darkTheme } from '../common/theme/tokens';
 * AppStorage.SetOrCreate('theme', lightTheme);
 *
 * // 2. 在组件中使用
 * @StorageProp('theme') theme: ThemeTokens | null = null;
 * .backgroundColor(this.theme?.surface ?? '#FFFFFF')
 * .fontSize(this.theme?.fontSizeBody ?? 14)
 *
 * // 3. 运行时切换主题
 * import { lightTheme, darkTheme } from '../common/theme/tokens';
 * AppStorage.Set('theme', systemDark ? darkTheme : lightTheme);
 *
 * ============================================================================
 * 对应赛道品牌色映射（后续扩展）
 * ============================================================================
 * ThinkKit (Productivity & Knowledge): #5B8C5A 森绿
 * RhythmLife (Habit & Life):          #4A90D9 靛蓝
 * CraftsmanUtils (Pro Utility):       #3C3C3C 深灰
 *
 * 可在 app.config.ts 中选择对应赛道的 primary 色覆盖默认主题
 * ============================================================================
 */

// ---- 类型定义 ----

export interface ThemeTokens {
  // === 颜色 ===
  primary: string;           // 主色（按钮、强调文字、进度条）
  primaryVariant: string;    // 主色变体（长按态、淡化背景）
  secondary: string;         // 辅色（次要按钮、标签）
  background: string;        // 页面背景色
  surface: string;           // 卡片/弹窗/输入框 表面色
  surfaceVariant: string;    // 表面色变体（分割线区域背景）
  onPrimary: string;         // 叠加在主色上的文字颜色
  onSurface: string;         // 叠加在表面色上的文字颜色
  onBackground: string;      // 叠加在背景色上的文字颜色
  outline: string;           // 边框线颜色
  error: string;             // 错误/危险操作色
  success: string;           // 成功色
  warning: string;           // 警告色

  // === 圆角 ===
  radiusSmall: number;       // 小圆角（标签/徽章）   建议 6-8
  radiusMedium: number;      // 中圆角（卡片/按钮）   建议 10-14
  radiusLarge: number;       // 大圆角（弹窗/面板）   建议 16-24

  // === 字号 ===
  fontSizeCaption: number;   // 辅助说明文字           建议 11-12
  fontSizeBody: number;      // 正文                   建议 14-15
  fontSizeSubtitle: number;  // 副标题                 建议 16-17
  fontSizeTitle: number;     // 标题                   建议 18-20
  fontSizeHeading: number;   // 大标题                 建议 22-28

  // === 字重 ===
  fontWeightRegular: number; // 常规 400
  fontWeightMedium: number;  // 中等 500
  fontWeightBold: number;    // 粗体 700

  // === 间距 ===
  spacingXs: number;         // 极小间距 4
  spacingSmall: number;      // 小间距   8
  spacingMedium: number;     // 中间距   12
  spacingLarge: number;      // 大间距   16
  spacingXl: number;         // 超大间距 24

  // === 阴影 ===
  shadowCard: ShadowOptions;       // 卡片阴影
  shadowDialog: ShadowOptions;     // 弹窗阴影
  shadowButton: ShadowOptions;     // 按钮阴影

  // === 动画 ===
  animationDurationShort: number;  // 短动画时长(ms) 150-200
  animationDurationMedium: number; // 中动画时长(ms) 300-400
  animationDurationLong: number;   // 长动画时长(ms) 500-600
}

/** 阴影配置类型 */
export interface ShadowOptions {
  radius: number;
  color: string;
  offsetX: number;
  offsetY: number;
}

// ============================================================================
// 主题配置
// ============================================================================

// ---- 共享的规格常量（跨主题不变） ----

const sharedRadius = {
  radiusSmall: 8,
  radiusMedium: 12,
  radiusLarge: 20,
} as const;

const sharedFontSize = {
  fontSizeCaption: 12,
  fontSizeBody: 14,
  fontSizeSubtitle: 16,
  fontSizeTitle: 18,
  fontSizeHeading: 24,
} as const;

const sharedFontWeight = {
  fontWeightRegular: 400,
  fontWeightMedium: 500,
  fontWeightBold: 700,
} as const;

const sharedSpacing = {
  spacingXs: 4,
  spacingSmall: 8,
  spacingMedium: 12,
  spacingLarge: 16,
  spacingXl: 24,
} as const;

const sharedAnimation = {
  animationDurationShort: 180,
  animationDurationMedium: 350,
  animationDurationLong: 550,
} as const;

// ============================================================================
// 主题 1：浅色主题（默认）
// ============================================================================

export const lightTheme: ThemeTokens = {
  // 颜色 — 浅色系，白底黑字
  primary: '#5B8C5A',
  primaryVariant: '#7BAF7A',
  secondary: '#BCAAA4',
  background: '#F5F5F5',
  surface: '#FFFFFF',
  surfaceVariant: '#F0F0F0',
  onPrimary: '#FFFFFF',
  onSurface: '#1C1C1E',
  onBackground: '#1C1C1E',
  outline: '#DCDCDC',
  error: '#FF3B30',
  success: '#34C759',
  warning: '#FF9500',

  // 圆角
  ...sharedRadius,

  // 字号
  ...sharedFontSize,

  // 字重
  ...sharedFontWeight,

  // 间距
  ...sharedSpacing,

  // 阴影 — 浅色环境阴影更深
  shadowCard: {
    radius: 8,
    color: '#00000010',
    offsetX: 0,
    offsetY: 2,
  },
  shadowDialog: {
    radius: 16,
    color: '#00000020',
    offsetX: 0,
    offsetY: 4,
  },
  shadowButton: {
    radius: 4,
    color: '#5B8C5A30',
    offsetX: 0,
    offsetY: 2,
  },

  // 动画
  ...sharedAnimation,
};

// ============================================================================
// 主题 2：深色主题
// ============================================================================

export const darkTheme: ThemeTokens = {
  // 颜色 — 深色系，黑底白字
  primary: '#7BAF7A',
  primaryVariant: '#5B8C5A',
  secondary: '#8D8D93',
  background: '#000000',
  surface: '#1C1C1E',
  surfaceVariant: '#2C2C2E',
  onPrimary: '#000000',
  onSurface: '#FFFFFF',
  onBackground: '#FFFFFF',
  outline: '#38383A',
  error: '#FF453A',
  success: '#30D158',
  warning: '#FF9F0A',

  // 圆角
  ...sharedRadius,

  // 字号
  ...sharedFontSize,

  // 字重
  ...sharedFontWeight,

  // 间距
  ...sharedSpacing,

  // 阴影 — 深色环境阴影微弱
  shadowCard: {
    radius: 8,
    color: '#00000040',
    offsetX: 0,
    offsetY: 2,
  },
  shadowDialog: {
    radius: 16,
    color: '#00000060',
    offsetX: 0,
    offsetY: 4,
  },
  shadowButton: {
    radius: 4,
    color: '#7BAF7A20',
    offsetX: 0,
    offsetY: 1,
  },

  // 动画
  ...sharedAnimation,
};

// ============================================================================
// 主题 3：护眼主题（暖色调，适合阅读/笔记场景）
// ============================================================================

export const eyeCareTheme: ThemeTokens = {
  // 颜色 — 米黄底色，降低蓝光
  primary: '#8B6F47',
  primaryVariant: '#A08B63',
  secondary: '#B8A99A',
  background: '#F5ECD7',
  surface: '#FDF8EE',
  surfaceVariant: '#EDE4D0',
  onPrimary: '#FFFFFF',
  onSurface: '#3C3C3C',
  onBackground: '#3C3C3C',
  outline: '#D4C9B5',
  error: '#C0392B',
  success: '#27AE60',
  warning: '#E67E22',

  // 圆角
  ...sharedRadius,

  // 字号 — 护眼模式字号稍大
  fontSizeCaption: 13,
  fontSizeBody: 15,
  fontSizeSubtitle: 17,
  fontSizeTitle: 19,
  fontSizeHeading: 25,

  // 字重
  ...sharedFontWeight,

  // 间距 — 护眼模式留白更多
  spacingXs: 5,
  spacingSmall: 10,
  spacingMedium: 14,
  spacingLarge: 20,
  spacingXl: 28,

  // 阴影 — 柔和阴影
  shadowCard: {
    radius: 6,
    color: '#8B6F4710',
    offsetX: 0,
    offsetY: 1,
  },
  shadowDialog: {
    radius: 12,
    color: '#8B6F4720',
    offsetX: 0,
    offsetY: 3,
  },
  shadowButton: {
    radius: 3,
    color: '#8B6F4720',
    offsetX: 0,
    offsetY: 1,
  },

  // 动画 — 护眼模式动画稍慢，减少视觉刺激
  animationDurationShort: 250,
  animationDurationMedium: 450,
  animationDurationLong: 650,
};

// ============================================================================
// 主题切换辅助函数
// ============================================================================

/**
 * 根据系统深色模式自动选择主题
 * @param systemIsDark 系统是否处于深色模式
 * @returns 对应的浅色/深色主题
 */
export function autoTheme(systemIsDark: boolean): ThemeTokens {
  return systemIsDark ? darkTheme : lightTheme;
}

/**
 * 所有可用主题集合
 * 供设置页展示主题选择列表
 */
export const ALL_THEMES: Record<string, ThemeTokens> = {
  light: lightTheme,
  dark: darkTheme,
  eyeCare: eyeCareTheme,
};

export const ALL_THEME_NAMES: Record<string, string> = {
  light: '浅色',
  dark: '深色',
  eyeCare: '护眼',
};
