"""补跑 K10 GLM 验证 (重试 3 次, 防止 escape 错)"""
import json
import os
import re
import sys
import time
from pathlib import Path

import httpx

ROOT = Path(r'D:\Z_学习平台\knowledge-cards-prod\projects\math\cards\线面平行证明')
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
  "your_answer": "你的答案",
  "your_proof_sketch": "你的解题思路（30-80 字）",
  "verdict": "完全一致" 或 "答案一致但证明不同" 或 "答案部分一致" 或 "答案不一致",
  "issue": "如果不一致，描述问题（20-50 字）；一致则填 '无'",
  "confidence": "high" 或 "medium" 或 "low"
}}

只输出 JSON，不要其他文字。
"""

def call_glm(prompt, api_key):
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
    m = re.search(r'\{.*\}', content, flags=re.DOTALL)
    if not m:
        return {"_error": "no JSON in response", "_elapsed": elapsed, "_raw": content[:500]}
    try:
        return json.loads(m.group(0))
    except Exception as e:
        return {"_error": f"JSON parse: {e}", "_elapsed": elapsed, "_raw": content[:500]}


api_key = os.environ.get('ZHIPU_API_KEY', '')
if not api_key:
    api_key = 'dfe1418d08b54255bb46f7e70cf96b99.IuQdU4ak2mIKqIGK'
print(f'GLM API key: {api_key[:10]}...')

f = ROOT / 'K10.json'
data = json.loads(f.read_text(encoding='utf-8'))
front = data.get('front', '')
back = data.get('back', '')

# 简化 front (避免特殊字符触发 escape 错)
front_simple = front[:500].replace('\\', '').replace('\n', ' ')

prompt = VERIFY_PROMPT.format(front=front_simple, back=back[:1000])

print('==== K10 (重试) ====')
print(f'  front (前 80): {front[:80].replace(chr(10), " ")}')

for attempt in range(3):
    result = call_glm(prompt, api_key)
    elapsed = result.get('_elapsed', 0)
    if result.get('_error'):
        print(f'  [尝试 {attempt+1}/3, {elapsed:.1f}s] ERR: {result["_error"][:100]}')
        if attempt < 2:
            time.sleep(2)
        continue
    print(f'  GLM 答案: {result.get("your_answer", "")[:200]}')
    print(f'  GLM 思路: {result.get("your_proof_sketch", "")[:200]}')
    print(f'  verdict: {result.get("verdict", "")}  ({elapsed:.1f}s)')
    print(f'  issue: {result.get("issue", "")}')
    print(f'  confidence: {result.get("confidence", "")}')
    break
