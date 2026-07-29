/**
 * theme/tokens.ts — Design Token 主题系统 (ThinkKit Reader 定制版)
 *
 * ============================================================================
 * 设计理念
 * ============================================================================
 * 1. 所有颜色、字号、间距、圆角、阴影均从此文件导出
 * 2. 提供 3 套主题：浅色（light）、深色（dark）、护眼/阅读（reading）
 * 3. 通过 AppStorage 全局注入当前主题
 * 4. 专为阅读场景优化：阅读主题米黄底 + 适中字号 + 降低对比度
 *
 * ThinkKit 品牌色: #5B8C5A 森绿
 * ============================================================================
 */

export interface ThemeTokens {
  primary: string;
  primaryVariant: string;
  secondary: string;
  background: string;
  surface: string;
  surfaceVariant: string;
  onPrimary: string;
  onSurface: string;
  onBackground: string;
  outline: string;
  error: string;
  success: string;
  warning: string;

  // === 阅读专用 ===
  textColor: string;         // 正文字色
  textColorSecondary: string;// 辅助文字

  radiusSmall: number;
  radiusMedium: number;
  radiusLarge: number;

  fontSizeCaption: number;
  fontSizeBody: number;
  fontSizeSubtitle: number;
  fontSizeTitle: number;
  fontSizeHeading: number;

  fontWeightRegular: number;
  fontWeightMedium: number;
  fontWeightBold: number;

  spacingXs: number;
  spacingSmall: number;
  spacingMedium: number;
  spacingLarge: number;
  spacingXl: number;

  animationDurationShort: number;
  animationDurationMedium: number;
  animationDurationLong: number;
}

const sharedRadius = {
  radiusSmall: 8,
  radiusMedium: 12,
  radiusLarge: 20,
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
// 主题 1：浅色主题
// ============================================================================

export const lightTheme: ThemeTokens = {
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

  textColor: '#1C1C1E',
  textColorSecondary: '#8E8E93',

  ...sharedRadius,
  fontSizeCaption: 12,
  fontSizeBody: 14,
  fontSizeSubtitle: 16,
  fontSizeTitle: 18,
  fontSizeHeading: 24,
  ...sharedFontWeight,
  ...sharedSpacing,
  ...sharedAnimation,
};

// ============================================================================
// 主题 2：深色主题（夜间模式）
// ============================================================================

export const darkTheme: ThemeTokens = {
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

  textColor: '#E5E5E7',
  textColorSecondary: '#8E8E93',

  ...sharedRadius,
  fontSizeCaption: 12,
  fontSizeBody: 14,
  fontSizeSubtitle: 16,
  fontSizeTitle: 18,
  fontSizeHeading: 24,
  ...sharedFontWeight,
  ...sharedSpacing,
  ...sharedAnimation,
};

// ============================================================================
// 主题 3：护眼阅读主题
// ============================================================================

export const eyeCareTheme: ThemeTokens = {
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

  textColor: '#3C3C3C',
  textColorSecondary: '#8A8278',

  ...sharedRadius,
  fontSizeCaption: 13,
  fontSizeBody: 15,
  fontSizeSubtitle: 17,
  fontSizeTitle: 19,
  fontSizeHeading: 25,
  ...sharedFontWeight,
  spacingXs: 5,
  spacingSmall: 10,
  spacingMedium: 14,
  spacingLarge: 20,
  spacingXl: 28,
  ...sharedAnimation,
};

export function autoTheme(systemIsDark: boolean): ThemeTokens {
  return systemIsDark ? darkTheme : lightTheme;
}

export const ALL_THEMES: Record<string, ThemeTokens> = {
  light: lightTheme,
  dark: darkTheme,
  eyeCare: eyeCareTheme,
};

export const ALL_THEME_NAMES: Record<string, string> = {
  light: '浅色',
  dark: '夜间',
  eyeCare: '护眼',
};
