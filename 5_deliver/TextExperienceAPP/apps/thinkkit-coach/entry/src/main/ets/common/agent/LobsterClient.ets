/**
 * agent/LobsterClient.ets — G 维度：小龙虾HTTP客户端
 * mock模式 + 降级策略 · Phase 1B
 */

import http from '@ohos.net.http';
import { TaskRequest, TaskResponse, ErrorAttribution, TaskError } from './types';

interface MockQuestion {
  id: string; domain: string; board: string; difficulty: number;
  text: string; options: string[]; answer: number; explanation: string;
}

interface MockGenResult {
  questions: MockQuestion[]
  set_id: string
}

interface MockRecItem {
  type: string
  message: string
}

interface MockPlanItem {
  week: number
  focus: string
  hours: number
}

interface MockErrorResult {
  attribution: ErrorAttribution
  recommendations: MockRecItem[]
}

interface MockPlanResult {
  weeklyPlan: MockPlanItem[]
  focusAreas: string[]
}

const MOCK_QS: MockQuestion[] = [
  { id: 'mock_001', domain: 'math', board: '函数与导数', difficulty: 2,
    text: '函数 f(x)=x³-3x 的单调递增区间是？',
    options: ['(-∞,-1)∪(1,+∞)', '(-1,1)', '(0,+∞)', '(-∞,0)'], answer: 0,
    explanation: '求导 f\'(x)=3x²-3=3(x+1)(x-1)，当 x<-1 或 x>1 时 f\'(x)>0' },
  { id: 'mock_002', domain: 'math', board: '解析几何', difficulty: 2,
    text: '椭圆 x²/9 + y²/4 = 1 的长轴长为？',
    options: ['6', '4', '3', '2'], answer: 0, explanation: 'a²=9 → a=3，长轴=2a=6' },
  { id: 'mock_003', domain: 'math', board: '数列', difficulty: 1,
    text: '等差数列 {aₙ} 中，a₁=2，d=3，则 a₅=？',
    options: ['14', '11', '17', '8'], answer: 0, explanation: 'a₅ = a₁ + 4d = 2 + 4×3 = 14' },
  { id: 'mock_004', domain: 'math', board: '概率统计', difficulty: 1,
    text: '从5人中选3人组成小组，有几种选法？',
    options: ['10', '20', '30', '60'], answer: 0, explanation: 'C(5,3) = C(5,2) = 10' },
  { id: 'mock_005', domain: 'math', board: '三角函数', difficulty: 2,
    text: 'sin(45°+30°) = ?',
    options: ['(√6+√2)/4', '(√6-√2)/4', '√2/2', '√3/2'], answer: 0,
    explanation: 'sin(α+β) = sinαcosβ + cosαsinβ' },
];

export class LobsterClient {
  private baseUrl: string;
  private mockMode: boolean;

  constructor(baseUrl: string, mockMode: boolean) {
    this.baseUrl = baseUrl;
    this.mockMode = mockMode;
  }

  setMockMode(enabled: boolean): void { this.mockMode = enabled; }
  isMockMode(): boolean { return this.mockMode; }

  async health(): Promise<string> {
    if (this.mockMode) return 'ok';
    try { const r = http.createHttp(); await r.request(this.baseUrl + '/health', { method: http.RequestMethod.GET }); r.destroy(); return 'ok'; }
    catch { return 'down'; }
  }

  async task(request: TaskRequest): Promise<TaskResponse> {
    if (this.mockMode) return this.mockTask(request);
    try {
      const req = http.createHttp();
      const headers: Record<string, string> = { 'Content-Type': 'application/json' };
      const resp = await req.request(this.baseUrl + '/task', {
        method: http.RequestMethod.POST, header: headers, extraData: JSON.stringify(request)
      });
      const data = JSON.parse(resp.result as string) as TaskResponse;
      req.destroy();
      return data;
    } catch {
      console.info('[LobsterClient] 降级到本地规则引擎');
      return this.mockTask(request);
    }
  }

  async generateQuestions(domain: string, difficulty: number, count: number): Promise<MockQuestion[]> {
    if (this.mockMode) {
      return this.mockGenerate(difficulty, count);
    }
    const resp = await this.task({
      appId: 'gaokao-agent',
      taskType: 'generate_questions',
      payload: { domain: domain, difficulty: difficulty, count: count }
    });
    if (resp.status === 'ok' && resp.result !== undefined) {
      return resp.result['questions'] as MockQuestion[];
    }
    return [];
  }

  async writeBackState(appId: string, updates: ESObject[]): Promise<boolean> {
    if (this.mockMode) return true;
    try {
      const req = http.createHttp();
      await req.request(this.baseUrl + '/state/write-back', {
        method: http.RequestMethod.POST,
        header: { 'Content-Type': 'application/json' } as Record<string, string>,
        extraData: JSON.stringify({ app_id: appId, updates: updates })
      });
      req.destroy();
      return true;
    } catch { return false; }
  }

  // ---- Mock 规则引擎 ----

  private mockTask(request: TaskRequest): TaskResponse {
    const traceId = 'mock_' + Date.now().toString();

    if (request.taskType === 'generate_questions') {
      const d: number = typeof request.payload['difficulty'] === 'number' ? request.payload['difficulty'] as number : 0;
      const c: number = typeof request.payload['count'] === 'number' ? request.payload['count'] as number : 3;
      const qs: MockQuestion[] = this.mockGenerate(d, c);
      const genResult: MockGenResult = { questions: qs, set_id: traceId };
      return { status: 'ok', traceId: traceId, result: genResult };
    }

    if (request.taskType === 'analyze_errors') {
      const attr: ErrorAttribution = { conceptual: 0.5, calculative: 0.3, timePressure: 0.2 };
      const rec1: MockRecItem = { type: 'review', message: '建议回顾基本概念' };
      const rec2: MockRecItem = { type: 'practice', message: '多做题提高计算速度' };
      const recs: MockRecItem[] = [rec1, rec2];
      const result: MockErrorResult = { attribution: attr, recommendations: recs };
      return { status: 'ok', traceId: traceId, result: result };
    }

    if (request.taskType === 'recommend_plan') {
      const p1: MockPlanItem = { week: 1, focus: '函数与导数', hours: 4 };
      const p2: MockPlanItem = { week: 2, focus: '解析几何', hours: 4 };
      const plans: MockPlanItem[] = [p1, p2];
      const areas: string[] = ['函数与导数', '解析几何'];
      const result: MockPlanResult = { weeklyPlan: plans, focusAreas: areas };
      return { status: 'ok', traceId: traceId, result: result };
    }

    const err: TaskError = { code: 'UNSUPPORTED', message: request.taskType };
    return { status: 'error', traceId: traceId, error: err };
  }

  private mockGenerate(difficulty: number, count: number): MockQuestion[] {
    let filtered: MockQuestion[] = MOCK_QS;
    if (difficulty > 0) {
      filtered = [];
      for (let i = 0; i < MOCK_QS.length; i++) {
        if (MOCK_QS[i].difficulty === difficulty) filtered.push(MOCK_QS[i]);
      }
    }
    const result: MockQuestion[] = [];
    const max: number = count < filtered.length ? count : filtered.length;
    for (let i = 0; i < max; i++) result.push(filtered[i]);
    return result;
  }
}
