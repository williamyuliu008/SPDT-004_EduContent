/**
 * app.config.ts — 深度阅读器 (ThinkKit Reader)
 */
export const AppConfig = {
  appName: 'ThinkKit阅读器',
  shortDesc: '深度阅读，摘录批注',
  primaryColor: '#5B8C5A',
  accentColor: '#FF6B6B',
  bgColor: '#F5F5F5',
  /** 字号档位：小 / 中 / 大 */
  fontSizeLevels: [14, 18, 22] as number[],
  /** 默认字号档位索引 */
  defaultFontLevel: 1,
} as const;
