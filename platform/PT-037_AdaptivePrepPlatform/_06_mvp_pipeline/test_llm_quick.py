# -*- coding: utf-8 -*-
import os, time
from pathlib import Path

API_KEY = Path(r"D:\_CEO\bulletin\SECRET_KEY\zhipu_api.txt").read_text(encoding="utf-8").strip()
os.environ["ZHIPU_API_KEY"] = API_KEY
print(f"Key: {API_KEY[:8]}...")

try:
    from openai import OpenAI
    client = OpenAI(api_key=API_KEY, base_url="https://open.bigmodel.cn/api/paas/v4/")
    print("Client created OK")

    start = time.time()
    resp = client.chat.completions.create(
        model="glm-4-flash",
        messages=[
            {"role": "system", "content": "你是书法史专家，简短回答"},
            {"role": "user", "content": "什么是天下三大行书？请用一句话回答"}
        ],
        temperature=0.3,
        timeout=15.0
    )
    elapsed = time.time() - start
    print(f"Response time: {elapsed:.2f}s")
    print(f"Response: {resp.choices[0].message.content}")
except Exception as e:
    print(f"Error: {e}")
