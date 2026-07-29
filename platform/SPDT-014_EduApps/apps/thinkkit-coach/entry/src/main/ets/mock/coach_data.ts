/**
 * mock/coach_data.ts — 学习教练 Mock 数据
 * 复用 GaokaoAgent 数学知识底座
 */

// ---- 知识全景数据 ----
export interface KpNode {
  name: string; mastery: number; level: number;
  children: KpNode[];
  classicTrap?: string;
  relatedKps?: string[];
  templateFile?: string;
}

export const MOCK_KNOWLEDGE_TREE: KpNode[] = [
  {
    name: '函数与导数', mastery: 65, level: 0, children: [
      { name: '函数定义域', mastery: 95, level: 1, children: [], classicTrap: '忽略对数真数>0', relatedKps: ['不等式求解'] },
      { name: '单调性判断', mastery: 85, level: 1, children: [], classicTrap: '导数符号与单调性方向搞反', templateFile: 'function_monotonicity.yaml' },
      {
        name: '极值与最值', mastery: 55, level: 1, children: [
          { name: '极值点判定', mastery: 70, level: 2, children: [], classicTrap: '驻点不一定是极值点' },
          { name: '含参讨论', mastery: 25, level: 2, children: [], classicTrap: '忘记 a=0 的情况', relatedKps: ['不等式求解', '分类讨论'] },
        ]
      },
      { name: '导数应用', mastery: 50, level: 1, children: [], classicTrap: '混淆切线方程与法线方程', templateFile: 'function_derivative.yaml' },
    ]
  },
  {
    name: '解析几何', mastery: 55, level: 0, children: [
      { name: '椭圆方程', mastery: 70, level: 1, children: [], classicTrap: 'a²与b²位置记反' },
      { name: '离心率计算', mastery: 50, level: 1, children: [], classicTrap: '椭圆/双曲线离心率公式混淆' },
    ]
  },
  {
    name: '数列', mastery: 75, level: 0, children: [
      { name: '等差数列', mastery: 90, level: 1, children: [] },
      { name: '等比数列', mastery: 60, level: 1, children: [], classicTrap: '公比 q=1 时前n项和公式不同' },
    ]
  },
  { name: '三角函数', mastery: 60, level: 0, children: [] },
  { name: '概率统计', mastery: 45, level: 0, children: [] },
  { name: '立体几何', mastery: 35, level: 0, children: [] },
  { name: '向量', mastery: 70, level: 0, children: [] },
  { name: '不等式', mastery: 30, level: 0, children: [], classicTrap: '乘除负数忘记变号' },
];

// ---- AI 闪卡生成 ----
export interface FlashCard { front: string; back: string; kp: string; }

export function generateFlashCards(kpName: string): FlashCard[] {
  const bank: Record<string, FlashCard[]> = {
    '极值点判定': [
      { front: 'f\'(x)=0 的点一定是极值点吗？', back: '不一定。f\'(x)=0 只是必要条件，还需要检查导数在该点两侧是否变号。例如 f(x)=x³ 在 x=0 处 f\'(0)=0 但不是极值点。', kp: '极值点判定' },
      { front: '判断极值点的两步法是什么？', back: '① 求 f\'(x)=0 的解（驻点）；② 检查每个驻点两侧 f\'(x) 的符号变化。左正右负→极大；左负右正→极小；不变号→非极值。', kp: '极值点判定' },
    ],
    '含参讨论': [
      { front: '含参讨论中最容易遗漏什么？', back: 'a=0 的情况！含参函数 f(x)=ax²+bx+c 中，a=0 时退化为一次函数，讨论方法与二次函数完全不同。', kp: '含参讨论' },
    ],
    '导数应用': [
      { front: '如何用导数求曲线 y=f(x) 在点(a, f(a))处的切线方程？', back: '切点(a, f(a))，斜率 k=f\'(a)，切线方程：y-f(a)=f\'(a)(x-a)', kp: '导数应用' },
    ],
  };
  return bank[kpName] ?? [
    { front: kpName + '的核心定义是什么？', back: '请参考教材相关章节，掌握核心定义后再来练习。', kp: kpName },
  ];
}

// ---- 学习计划 ----
export interface StudyPlan {
  id: string; goal: string; kps: string[]; durationDays: number;
  dailyMinutes: number; startDate: string; status: string; tasks: StudyTask[];
}
export interface StudyTask { day: number; kp: string; type: string; completed: boolean; score?: number; }

export const MOCK_PLAN: StudyPlan = {
  id: 'p1', goal: '攻克函数与导数', kps: ['函数定义域', '单调性判断', '极值与最值', '导数应用'],
  durationDays: 14, dailyMinutes: 40, startDate: '2026-06-18', status: 'active',
  tasks: [
    { day: 1, kp: '函数定义域', type: 'template', completed: false },
    { day: 2, kp: '单调性判断', type: 'template', completed: false },
    { day: 3, kp: '极值点判定', type: 'template', completed: false },
    { day: 4, kp: '极值点判定', type: 'lingkong', completed: false },
    { day: 5, kp: '含参讨论', type: 'template', completed: false },
    { day: 6, kp: '含参讨论', type: 'lingkong', completed: false },
    { day: 7, kp: '函数与导数', type: 'review', completed: false },
  ]
};

// ---- Dashboard ----
export interface CoachDashboard {
  todayTasks: StudyTask[]; streak: number; totalKps: number; masteredKps: number;
  planProgress: number; weekActivity: number[];
}
export const MOCK_DASHBOARD: CoachDashboard = {
  todayTasks: [
    { day: 3, kp: '极值点判定', type: 'template', completed: false },
    { day: 3, kp: '极值点判定', type: 'flashcard', completed: false },
  ],
  streak: 3, totalKps: 18, masteredKps: 8,
  planProgress: 21, weekActivity: [3, 5, 4, 2, 6, 4, 0],
};
