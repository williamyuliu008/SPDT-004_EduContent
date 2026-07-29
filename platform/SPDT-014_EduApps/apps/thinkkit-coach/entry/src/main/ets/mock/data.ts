/**
 * mock/data.ts — 数学学科开发用 Mock 数据
 * 后端就绪后替换为 services/api.ts 的真实 HTTP 调用
 */

// ---- 学科配置 ----
export interface DomainProfile {
  id: string; name: string; icon: string; color: string;
  kpCount: number; questionCount: number; boards: string[];
}

export const MOCK_DOMAINS: DomainProfile[] = [
  { id: 'math', name: '数学', icon: '📐', color: '#2563eb', kpCount: 120, questionCount: 500, boards: ['函数与导数', '解析几何', '数列', '概率统计', '三角函数', '立体几何', '向量', '不等式'] },
  { id: 'english', name: '英语', icon: '📝', color: '#10b981', kpCount: 80, questionCount: 300, boards: ['阅读理解', '完形填空', '语法', '写作', '听力'] },
  { id: 'physics', name: '物理', icon: '⚡', color: '#f59e0b', kpCount: 90, questionCount: 280, boards: ['力学', '电磁学', '热学', '光学', '原子物理'] },
];

// ---- 冷启动诊断 ----
export interface DiagnosticQuestion {
  id: number; text: string; options: string[]; board: string;
}
export const MOCK_DIAG_QUESTIONS: DiagnosticQuestion[] = [
  { id: 1, text: '函数 f(x)=x²+2x-3 的最小值是？', options: ['-4', '-3', '-2', '-1'], board: '函数与导数' },
  { id: 2, text: '圆 x²+y²=4 的半径是？', options: ['1', '2', '3', '4'], board: '解析几何' },
  { id: 3, text: '等差数列 2,5,8,... 的第10项是？', options: ['26', '29', '32', '35'], board: '数列' },
  { id: 4, text: '掷一枚硬币两次，至少一次正面的概率？', options: ['1/4', '1/2', '3/4', '1'], board: '概率统计' },
  { id: 5, text: 'sin(30°) = ?', options: ['0', '1/2', '√2/2', '√3/2'], board: '三角函数' },
  { id: 6, text: '向量 a=(1,2), b=(3,4) 的点积是？', options: ['7', '8', '10', '11'], board: '向量' },
  { id: 7, text: '不等式 |x-1|<3 的解集是？', options: ['(-2,4)', '(-4,2)', '(1,4)', '(2,5)'], board: '不等式' },
  { id: 8, text: '正方体的体积是 27，棱长是？', options: ['2', '3', '4', '6'], board: '立体几何' },
  { id: 9, text: 'sin²x+cos²x = ?', options: ['0', '1', '2', '-1'], board: '三角函数' },
  { id: 10, text: '等比数列 1,2,4,... 的公比是？', options: ['1', '2', '3', '4'], board: '数列' },
  { id: 11, text: '函数 y=ln(x) 的定义域是？', options: ['(0,+∞)', '(-∞,+∞)', '[0,+∞)', '(1,+∞)'], board: '函数与导数' },
  { id: 12, text: '抛物线 y=x² 的焦点坐标是？', options: ['(0,1/4)', '(1/4,0)', '(0,1)', '(1,0)'], board: '解析几何' },
  { id: 13, text: '从5人中选3人，有几种选法？', options: ['10', '20', '30', '60'], board: '概率统计' },
  { id: 14, text: 'a·(b+c) = ?', options: ['a·b+a·c', 'a·b·c', '|a|·|b|', 'a+b·c'], board: '向量' },
  { id: 15, text: 'x²-5x+6=0 的根是？', options: ['2和3', '1和6', '-2和-3', '0和5'], board: '不等式' },
];

export interface DiagnosticResult {
  totalScore: number; maxScore: number;
  boards: { name: string; score: number; level: 'green' | 'yellow' | 'red'; color: string; }[];
}
export const MOCK_DIAG_RESULT: DiagnosticResult = {
  totalScore: 11, maxScore: 15,
  boards: [
    { name: '函数与导数', score: 80, level: 'green', color: '#34d399' },
    { name: '解析几何', score: 65, level: 'green', color: '#34d399' },
    { name: '数列', score: 90, level: 'green', color: '#34d399' },
    { name: '概率统计', score: 55, level: 'yellow', color: '#fbbf24' },
    { name: '三角函数', score: 70, level: 'green', color: '#34d399' },
    { name: '立体几何', score: 40, level: 'yellow', color: '#fbbf24' },
    { name: '向量', score: 85, level: 'green', color: '#34d399' },
    { name: '不等式', score: 30, level: 'red', color: '#f87171' },
  ]
};

// ---- 凌空刷题 ----
export interface TutoringQuestion {
  id: string; text: string; board: string; kp: string; difficulty: number; type: string;
}
export const MOCK_TUTOR_QUESTIONS: TutoringQuestion[] = [
  { id: 'q1', text: '已知函数 f(x)=x³-3x+1，求 f(x) 的极值点。', board: '函数与导数', kp: '导数应用', difficulty: 3, type: '解答题' },
  { id: 'q2', text: '求椭圆 x²/4+y²/9=1 的离心率。', board: '解析几何', kp: '椭圆性质', difficulty: 2, type: '填空题' },
  { id: 'q3', text: '在等比数列 {an} 中，a₁=2, a₃=8，求公比 q。', board: '数列', kp: '等比公式', difficulty: 2, type: '选择题' },
];

// ---- 知识地图 ----
export interface KnowledgeNode {
  name: string; mastery: number; kpCount: number; completedCount: number;
  children: { name: string; mastery: number; type: string; }[];
}
export const MOCK_KNOWLEDGE: KnowledgeNode[] = [
  { name: '函数与导数', mastery: 80, kpCount: 25, completedCount: 20, children: [
    { name: '函数定义域', mastery: 95, type: '考点' }, { name: '单调性判断', mastery: 85, type: '考点' },
    { name: '极值最值', mastery: 70, type: '方法' }, { name: '含参讨论', mastery: 45, type: '陷阱' },
  ]},
  { name: '解析几何', mastery: 65, kpCount: 20, completedCount: 13, children: [
    { name: '椭圆方程', mastery: 80, type: '考点' }, { name: '离心率计算', mastery: 60, type: '方法' },
    { name: '直线与圆', mastery: 55, type: '陷阱' },
  ]},
  { name: '数列', mastery: 90, kpCount: 12, completedCount: 11, children: [
    { name: '通项公式', mastery: 95, type: '考点' }, { name: '求和方法', mastery: 85, type: '方法' },
  ]},
  { name: '概率统计', mastery: 55, kpCount: 18, completedCount: 8, children: [
    { name: '古典概型', mastery: 60, type: '考点' }, { name: '条件概率', mastery: 40, type: '陷阱' },
  ]},
  { name: '三角函数', mastery: 70, kpCount: 15, completedCount: 10, children: [
    { name: '恒等变换', mastery: 75, type: '方法' }, { name: '图像性质', mastery: 65, type: '考点' },
  ]},
  { name: '立体几何', mastery: 40, kpCount: 14, completedCount: 5, children: [
    { name: '体积计算', mastery: 50, type: '考点' }, { name: '空间角', mastery: 30, type: '陷阱' },
  ]},
  { name: '向量', mastery: 85, kpCount: 8, completedCount: 7, children: [
    { name: '数量积', mastery: 90, type: '考点' }, { name: '坐标运算', mastery: 80, type: '方法' },
  ]},
  { name: '不等式', mastery: 30, kpCount: 8, completedCount: 2, children: [
    { name: '一元二次', mastery: 40, type: '考点' }, { name: '绝对值不等式', mastery: 20, type: '陷阱' },
  ]},
];

// ---- Dashboard ----
export interface DashboardData {
  todayQuestions: number; todayCorrect: number; weekTrend: number[];
  weakBoards: { name: string; score: number; }[];
  totalHours: number; streak: number;
  examDate: string; daysLeft: number;
}
export const MOCK_DASHBOARD: DashboardData = {
  todayQuestions: 23, todayCorrect: 18,
  weekTrend: [12, 15, 20, 18, 25, 22, 23],
  weakBoards: [
    { name: '不等式', score: 30 }, { name: '立体几何', score: 40 }, { name: '概率统计', score: 55 }
  ],
  totalHours: 126, streak: 7,
  examDate: '2027-06-07', daysLeft: 355
};
