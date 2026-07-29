/**
 * app.config.ts — ThinkKit Quiz 互动测验
 *
 * 品牌：ThinkKit（森绿 #5B8C5A）
 * 设计语言：知识感、专注、舒适
 */
export const AppConfig = {
  // ---- 品牌 ----
  appName: '互动测验',
  shortDesc: '知识互动测验工具',
  primaryColor: '#5B8C5A',
  accentColor: '#7BC67E',
  bgColor: '#F5F9F5',

  // ---- 卡片颜色 ----
  cardBg: '#FFFFFF',
  cardBorder: '#D5E8D5',
  textPrimary: '#1A2E1A',
  textSecondary: '#5A7A5A',
  textTertiary: '#8AA88A',

  // ---- 功能色 ----
  successColor: '#4CAF50',
  warningColor: '#FF9800',
  errorColor: '#F44336',
  correctColor: '#34C759',
  wrongColor: '#FF3B30',

  // ---- 圆角 ----
  radius: 12,
  radiusSm: 8,

  // ---- 计时器 ----
  defaultQuizTime: 60,     // 默认答题时间（秒）
  timeWarning: 10,          // 时间警告阈值（秒）
} as const;
