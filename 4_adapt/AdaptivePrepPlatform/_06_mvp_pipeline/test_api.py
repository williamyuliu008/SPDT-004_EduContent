# -*- coding: utf-8 -*-
import urllib.request, json, time

time.sleep(3)

# Test /api/kb/entry/KB_CAFA_S010
url = "http://localhost:5188/api/kb/entry/KB_CAFA_S010"
try:
    with urllib.request.urlopen(url, timeout=10) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        if data.get("ok"):
            e = data.get("entry", {})
            print("=== KB_CAFA_S010 ===")
            print(f"concept: {e.get('concept')}")
            sc = e.get("structured_content", {})
            print(f"sc keys: {list(sc.keys())}")
            bg = sc.get("background", "")
            print(f"background len: {len(bg)}")
            print(f"background preview: {bg[:100]}...")
            hp = sc.get("historical_period", "")
            print(f"historical_period: {hp[:80]}...")
            at = e.get("answer_template", "")
            print(f"answer_template len: {len(at)}")
            print(f"answer_template preview: {at[:80]}...")
            tips = e.get("exam_tips", {})
            print(f"exam_tips keys: {list(tips.keys())}")
            print(f"cross_pack_links: {len(e.get('cross_pack_links',[]))} items")
        else:
            print("API returned error:", data.get("error"))
    # Test /api/kb/summary
    url2 = "http://localhost:5188/api/kb/summary"
    with urllib.request.urlopen(url2, timeout=10) as resp:
        data2 = json.loads(resp.read().decode("utf-8"))
        if data2.get("ok"):
            s = data2.get("summary", {})
            print(f"\n=== KB Summary ===")
            print(f"total_kb_entries: {s.get('total_kb_entries')}")
            print(f"total_translation_entries: {s.get('total_translation_entries')}")
            print(f"total_punctuation_texts: {s.get('total_punctuation_texts')}")
            print(f"total_error_scripts: {s.get('total_error_scripts')}")
except Exception as ex:
    print(f"Error: {ex}")
