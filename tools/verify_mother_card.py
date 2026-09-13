"""
用 GLM 验证 K10-K15 母题 back 答案准确率
- 把 front + back 喂给 GLM
- 让 GLM 重新解题，对比 K 卡 back 答案
- 输出 verdict: 一致/部分一致/不一致
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, r'D:\Z_学习平台\SPDT-004_EduContent\tools')
from review_httpx import get_api_key
import httpx

ROOT = Path(r'D:\Z_学习平台\knowledge-cards-prod\projects\math\cards\线面平行证明')
MOTHERS = [ROOT / f'K{i}.json' for i in range(10, 16)]

GLM_ENDPOINT = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
MODEL = "glm-4-flash"
TIMEOUT = 60.0

VERIFY_PROMPT = """你是高考数学解题专家。请独立解答以下母题，然后对比给定的 back 答案，判定一致程度。

【母题题干】
{front}

【给定答案 + 解析】
{back}

请输出 (JSON 格式):
{{
  "your_answer": "你的答案（用 LaTeX 表达最终数值）",
  "your_proof_sketch": "你的解题思路（30-80 字）",
  "verdict": "完全一致" 或 "答案一致但证明不同" 或 "答案部分一致" 或 "答案不一致",
  "issue": "如果不一致，描述问题（20-50 字）；一致则填 '无'",
  "confidence": "high" 或 "medium" 或 "low"
}}

只输出 JSON，不要其他文字。
"""

def call_glm(prompt: str, api_key: str) -> dict:
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
        "max_tokens": 1500,
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    t0 = time.time()
    with httpx.Client(timeout=TIMEOUT) as client:
        r = client.post(GLM_ENDPOINT, json=payload, headers=headers)
    elapsed = time.time() - t0
    if r.status_code != 200:
        return {"_error": f"HTTP {r.status_code}: {r.text[:200]}", "_elapsed": elapsed}
    j = r.json()
    content = j.get('choices', [{}])[0].get('message', {}).get('content', '')
    # 提取 JSON
    import re
    m = re.search(r'\{.*\}', content, flags=re.DOTALL)
    if not m:
        return {"_error": "no JSON in response", "_elapsed": elapsed, "_raw": content[:500]}
    try:
        return json.loads(m.group(0))
    except Exception as e:
        return {"_error": f"JSON parse: {e}", "_elapsed": elapsed, "_raw": content[:500]}

api_key = get_api_key()
print(f'GLM API key: {api_key[:10]}...{api_key[-4:]}')
print()

results = []
for f in MOTHERS:
    if not f.exists():
        continue
    data = json.loads(f.read_text(encoding='utf-8'))
    kid = data.get('id') or f.stem
    front = data.get('front', '')
    back = data.get('back', '')
    prompt = VERIFY_PROMPT.format(front=front, back=back)
    print(f'==== K{kid[1:]} ({f.name}) ====')
    print(f'  front (前 100): {front[:100].replace(chr(10), " ")}')
    t0 = time.time()
    result = call_glm(prompt, api_key)
    elapsed = time.time() - t0
    if result.get('_error'):
        print(f'  [ERR {elapsed:.1f}s] {result["_error"]}')
        results.append({'id': kid, 'error': result['_error']})
        continue
    print(f'  GLM 答案: {result.get("your_answer", "")}')
    print(f'  GLM 思路: {result.get("your_proof_sketch", "")}')
    print(f'  verdict: {result.get("verdict", "")}')
    print(f'  issue: {result.get("issue", "")}')
    print(f'  confidence: {result.get("confidence", "")}  ({elapsed:.1f}s)')
    results.append({
        'id': kid,
        'front_snippet': front[:80].replace('\n', ' '),
        'glm_answer': result.get('your_answer'),
        'glm_proof': result.get('your_proof_sketch'),
        'verdict': result.get('verdict'),
        'issue': result.get('issue'),
        'confidence': result.get('confidence'),
        'elapsed': elapsed,
    })
    # 间隔 3s 避免 GLM 限流
    time.sleep(3)

# 写报告
report = ROOT / '_mother_card_verify.md'
with open(report, 'w', encoding='utf-8') as fh:
    fh.write('# K10-K15 母题答案 GLM 验证报告\n\n')
    fh.write(f'**生成时间**: 2026-09-13 14:25\n')
    fh.write(f'**验证模型**: {MODEL}\n\n')
    fh.write('## 验证结果\n\n')
    fh.write('| K 卡 | verdict | GLM 答案 | GLM 思路 | issue | confidence |\n')
    fh.write('|------|---------|---------|---------|-------|------------|\n')
    for r in results:
        if 'error' in r:
            fh.write(f"| {r['id']} | [ERR] | - | - | {r['error']} | - |\n")
        else:
            fh.write(f"| {r['id']} | {r['verdict']} | {r['glm_answer']} | {r['glm_proof']} | {r['issue']} | {r['confidence']} |\n")
print()
print(f'报告写入: {report}')
