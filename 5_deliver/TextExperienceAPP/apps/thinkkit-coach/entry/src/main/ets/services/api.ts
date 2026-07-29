/**
 * services/api.ts — 调试版 v3
 * 每阶段更新 lastError
 */
import http from '@ohos.net.http';
import { AppConfig } from '../app.config';
import { MOCK_DOMAINS, DomainProfile, MOCK_DIAG_QUESTIONS, MOCK_DIAG_RESULT, DiagnosticResult, DiagnosticQuestion, MOCK_TUTOR_QUESTIONS, TutoringQuestion, MOCK_KNOWLEDGE, KnowledgeNode, MOCK_DASHBOARD, DashboardData } from '../mock/data';

let lastError: string = '';
export function getLastError(): string { return lastError; }
const USE_REAL: boolean = false; // 模拟器 HTTP 挂起，真机上改为 true
const BASE_URL: string = AppConfig.api.baseUrl;

export async function fetchDomains(): Promise<DomainProfile[]> {
  if (!USE_REAL) return MOCK_DOMAINS;
  lastError = 'GET domains';
  try { const d = await httpGet<DomainProfile[]>('/api/domains'); lastError = ''; return d; }
  catch (e) { lastError = 'FAIL:domains'; return MOCK_DOMAINS; }
}
export async function fetchDiagnosticQuestions(): Promise<DiagnosticQuestion[]> {
  if (!USE_REAL) return MOCK_DIAG_QUESTIONS;
  lastError = 'GET diag_q';
  try { const d = await httpGet<DiagnosticQuestion[]>('/api/diagnostic/questions'); lastError = ''; return d; }
  catch (e) { lastError = 'FAIL:diag_q'; return MOCK_DIAG_QUESTIONS; }
}
export async function submitDiagnostic(answers: number[]): Promise<DiagnosticResult> {
  if (!USE_REAL) return MOCK_DIAG_RESULT;
  lastError = 'POST diag';
  try { const d = await httpPost<DiagnosticResult>('/api/diagnostic', { answers: answers }); lastError = ''; return d; }
  catch (e) { lastError = 'FAIL:diag'; return MOCK_DIAG_RESULT; }
}
export async function fetchTutoringQuestions(board?: string): Promise<TutoringQuestion[]> {
  const fb: TutoringQuestion[] = board ? MOCK_TUTOR_QUESTIONS.filter((q: TutoringQuestion) => q.board === board) : MOCK_TUTOR_QUESTIONS;
  if (!USE_REAL) return fb;
  lastError = 'GET tutor';
  try { const d = await httpGet<TutoringQuestion[]>('/api/tutoring/questions'); lastError = ''; return d; }
  catch (e) { lastError = 'FAIL:tutor'; return fb; }
}
export interface TutorResult { correct: boolean; feedback: string; errorType: string; variantId: string; }
export async function submitTutoring(questionId: string, answer: string): Promise<TutorResult> {
  const fb: TutorResult = { correct: Math.random() > 0.3, feedback: '离线', errorType: '', variantId: 'v' + questionId };
  if (!USE_REAL) return fb;
  try { return await httpPost<TutorResult>('/api/tutoring', { question_id: questionId, answer: answer }); }
  catch (e) { return fb; }
}
export async function fetchKnowledgeMap(): Promise<KnowledgeNode[]> {
  if (!USE_REAL) return MOCK_KNOWLEDGE;
  try { return await httpGet<KnowledgeNode[]>('/api/knowledge'); }
  catch (e) { return MOCK_KNOWLEDGE; }
}
export async function fetchDashboard(): Promise<DashboardData> {
  if (!USE_REAL) return MOCK_DASHBOARD;
  try { return await httpGet<DashboardData>('/api/dashboard'); }
  catch (e) { return MOCK_DASHBOARD; }
}

async function httpGet<T>(path: string): Promise<T> {
  const req = http.createHttp();
  try {
    const resp = await req.request(BASE_URL + path, { method: http.RequestMethod.GET, connectTimeout: 3000, readTimeout: 3000 });
    if (resp.responseCode === 200) { return JSON.parse(resp.result as string) as T; }
    throw new Error('code=' + resp.responseCode);
  } finally { req.destroy(); }
}
async function httpPost<T>(path: string, body: Object): Promise<T> {
  const req = http.createHttp();
  try {
    const resp = await req.request(BASE_URL + path, { method: http.RequestMethod.POST, connectTimeout: 3000, readTimeout: 3000, extraData: JSON.stringify(body) });
    if (resp.responseCode === 200) { return JSON.parse(resp.result as string) as T; }
    throw new Error('code=' + resp.responseCode);
  } finally { req.destroy(); }
}
