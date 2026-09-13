"""补跑 K13/K14/K15 GLM 验证"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, r'D:\Z_学习平台\SPDT-004_EduContent\tools')
from review_httpx import get_api_key
import httpx

ROOT = Path(r'D:\Z_学习平台\knowledge-cards-prod\projects\math\cards\线面平行证明')
MOTHERS = [ROOT / f'K{i}.json' for i in (13, 14, 15)]

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

def call_glm(prompt, api_key):
    payload = {"model": MODEL, "messages": [{"role":"user","content":prompt}], "temperature":0.1, "max_tokens":1500}
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    t0 = time.time()
    with httpx.Client(timeout=TIMEOUT) as client:
        r = client.post(GLM_ENDPOINT, json=payload, headers=headers)
    elapsed = time.time() - t0
    if r.status_code != 200:
        return {"_error": f"HTTP {r.status_code}: {r.text[:200]}", "_elapsed": elapsed}
    j = r.json()
    content = j.get('choices', [{}])[0].get('message', {}).get('content', '')
    import re
    m = re.search(r'\{.*\}', content, flags=re.DOTALL)
    if not m:
        return {"_error": "no JSON", "_elapsed": elapsed, "_raw": content[:500]}
    try:
        return json.loads(m.group(0))
    except Exception as e:
        return {"_error": f"parse: {e}", "_elapsed": elapsed, "_raw": content[:500]}

api_key = get_api_key()
results = []
for f in MOTHERS:
    if not f.exists():
        print(f'[MISS] {f}')
        continue
    data = json.loads(f.read_text(encoding='utf-8'))
    kid = data.get('id') or f.stem
    front = data.get('front', '')
    back = data.get('back', '')
    prompt = VERIFY_PROMPT.format(front=front, back=back)
    print(f'==== K{kid[1:]} ({f.name}) ====')
    result = call_glm(prompt, api_key)
    if result.get('_error'):
        print(f'  [ERR] {result["_error"]}')
        results.append({'id': kid, 'error': result['_error']})
        continue
    print(f'  GLM 答案: {result.get("your_answer", "")}')
    print(f'  verdict: {result.get("verdict", "")}  ({result.get("_elapsed", 0):.1f}s)')
    print(f'  issue: {result.get("issue", "")}')
    results.append({
        'id': kid,
        'verdict': result.get('verdict'),
        'glm_answer': result.get('your_answer'),
        'issue': result.get('issue'),
    })
    time.sleep(2)

# 追加到报告
report = ROOT / '_mother_card_verify.md'
existing = report.read_text(encoding='utf-8') if report.exists() else ''
addition = '\n## K13-K15 补跑\n\n'
addition += '| K 卡 | verdict | GLM 答案 | issue |\n'
addition += '|------|---------|---------|-------|\n'
for r in results:
    if 'error' in r:
        addition += f"| {r['id']} | [ERR] | - | {r['error']} |\n"
    else:
        addition += f"| {r['id']} | {r['verdict']} | {r['glm_answer']} | {r['issue']} |\n"
report.write_text(existing + addition, encoding='utf-8')
print()
print(f'报告追加到: {report}')
