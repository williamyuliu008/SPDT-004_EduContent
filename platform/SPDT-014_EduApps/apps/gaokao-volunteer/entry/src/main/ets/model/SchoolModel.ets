/**
 * gaokao-volunteer · 数据模型
 * 院校信息 + 专业 + 历年分数
 */

export interface School {
  id: string;              // 院校代码（6位）
  name: string;            // 院校名称
  province: string;        // 所在地省份
  city: string;            // 城市
  type: string;             // 院校类型: 综合/理工/师范/文科/农林/医药/艺术/军事
  tags: string[];          // 标签: 985/211/双一流/公办/民办
  rank_national: number;   // 全国排名
  description: string;     // 院校简介
  majorCategories: MajorCategory[];  // 专业门类
  scoreLines: ScoreLine[];           // 历年录取分数线
  minScore: number;        // 本省最低分（参考）
}

export interface MajorCategory {
  category: string;        // 学科门类: 哲学/经济学/法学/教育学/文学/历史学/理学/工学/农学/医学/管理学/艺术学
  majors: string[];         // 代表专业列表
}

export interface ScoreLine {
  year: number;
  arts_score: number;       // 文科一本线（各省不同，此为示例基准）
  science_score: number;    // 理科一本线
  arts_admit_min: number;   // 文科录取最低分
  science_admit_min: number; // 理科录取最低分
}
