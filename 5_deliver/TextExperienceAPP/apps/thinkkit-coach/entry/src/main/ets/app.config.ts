/**
 * app.config.ts — 学习教练 (ThinkKit)
 */
export const AppConfig = {
  appName: '学习教练',
  shortDesc: 'Agent驱动的高考数学个性化学习系统',
  primaryColor: '#5B8C5A',
  features: {
    enableCoach: true,
    enableFlashCardGen: true,
    enableKnowledgePanorama: true,
    enableTemplates: true,
    enableLingkong: true,
  }
} as const;
