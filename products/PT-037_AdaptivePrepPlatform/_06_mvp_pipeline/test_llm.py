# -*- coding: utf-8 -*-
import os, json
os.environ["PYTHONIOENCODING"] = "utf-8"
_api_key_path = "D:/_CEO/bulletin/SECRET_KEY/zhipu_api.txt"
with open(_api_key_path, encoding="utf-8") as f:
    os.environ["ZHIPU_API_KEY"] = f.read().strip()

import sys
sys.path.insert(0, "_01_platform_core")
from llm.llm_wrapper import create_llm_client

llm = create_llm_client(mode="glm")
print("LLM mode:", llm.mode if hasattr(llm, "mode") else "unknown")

prompt = '请为"天下三大行书"写一段背景介绍，50字以内，直接输出文字，不要加引号。'
resp = llm.chat([{"role": "user", "content": prompt}])
print("Type:", type(resp))
print("Resp:", str(resp)[:300])
if isinstance(resp, dict):
    print("Text field:", resp.get("text", "")[:300])
