/**
 * app.config.ts — GaokaoAgent 高考助手
 * 六科统一框架，数学首版精磨
 */
export const AppConfig = {
  appName: '高考助手',
  shortDesc: '六科统一的高考AI辅导Agent',
  primaryColor: '#2563eb',
  themeBg: '#f0f4f8',
  features: {
    enableDiagnostic: true,
    enableTutoring: true,
    enableKnowledgeMap: true,
    enableDashboard: true,
    enableSubjectSwitch: true,
  },
  api: {
    baseUrl: 'http://127.0.0.1:8000',
    timeout: 15000,
  }
} as const;
