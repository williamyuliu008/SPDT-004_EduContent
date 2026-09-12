"""GLM-4-flash check: 单题反向推演（绕开 GLM-5 reasoning 占满问题）"""
import json
import urllib.request
from pathlib import Path
import sys

ZHIPU_KEY_PATH = Path(r'D:\3_infra\_SECRET_KEY\zhipu_api.txt')
KEY = ZHIPU_KEY_PATH.read_text(encoding='utf-8').strip()
API = 'https://open.bigmodel.cn/api/paas/v4/chat/completions'
MODEL = 'glm-4-flash'  # 改用 4-flash, 无自动 reasoning 链

def ask(prompt: str, max_tokens: int = 1500) -> tuple[str, dict]:
    payload = {
        'model': MODEL,
        'messages': [{'role': 'user', 'content': prompt}],
        'max_tokens': max_tokens,
        'temperature': 0.1
    }
    req = urllib.request.Request(API,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Authorization': 'Bearer ' + KEY, 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=60) as resp:
        r = json.loads(resp.read().decode('utf-8'))
    content = r['choices'][0]['message'].get('content', '')
    usage = r.get('usage', {})
    return content, {'usage': usage}

if __name__ == '__main__':
    pp_id = sys.argv[1] if len(sys.argv) > 1 else 'pp_001'
    KB = Path(r'D:\4_data\knowledge_cards\数学\4step\parent_problems')
    pp_path = next(KB.glob(f'{pp_id}*.json'), None)
    if not pp_path:
        print(f'NOT FOUND: {pp_id}')
        sys.exit(1)
    pp = json.loads(pp_path.read_text(encoding='utf-8'))
    problem = pp.get('problem_statement', pp.get('graph_bg', ''))
    goal = pp.get('goal', '')
    steps = pp.get('standard_steps', [])

    # 极简 prompt
    prompt = f"""你是数学老师。学生做了这道立体几何题：

题目：{problem}
学生答案：{goal}
学生步骤：
{chr(10).join(steps)}

请独立推导这道题，确认学生答案是否正确。
如果正确输出"✓ 正确"。
如果不正确输出"✗ 错误，原因是：..."，然后给出正确答案。
不要其他内容。"""

    print(f'=== 反向推演: {pp["id"]} (model={MODEL}) ===')
    content, info = ask(prompt)
    print(f'content_len: {len(content)}')
    print(f'usage: {info["usage"]}')
    print(f'CONTENT: {content[:800]}')
    if '✓' in content:
        print('VERDICT: PASS')
    elif '✗' in content:
        print('VERDICT: FAIL')
    else:
        print('VERDICT: UNKNOWN')
