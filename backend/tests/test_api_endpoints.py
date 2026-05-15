"""Full API Endpoint Test - Step 2d 前后端联调验证."""
import io
import sys

# Fix Windows GBK encoding for emoji output
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import httpx
import json

base = "http://localhost:8000"

print("=" * 60)
print("  TuringMate Backend - Full API Test (v2)")
print("=" * 60)

results = []

# 1. Health Check
try:
    r = httpx.get(f"{base}/health", timeout=5)
    ok = r.status_code == 200
    print(f"  [{'PASS' if ok else 'FAIL':6s}] {'Health Check':25s} -> {r.json()}")
    results.append(ok)
except Exception as e:
    print(f"  [ERROR ] {'Health Check':25s} -> {e}")
    results.append(False)

# 2. Question Parse (multipart file upload)
try:
    fake_img = io.BytesIO(b"fake_image_data")
    files = {"image": ("test.jpg", fake_img, "image/jpeg")}
    r = httpx.post(f"{base}/api/v1/question/parse", files=files, timeout=10)
    ok = r.status_code == 200
    data = json.dumps(r.json(), ensure_ascii=False)[:120]
    print(f"  [{'PASS' if ok else f'FAIL({r.status_code})':6s}] {'Question Parse':25s} -> {data}")
    results.append(ok)
except Exception as e:
    print(f"  [ERROR ] {'Question Parse':25s} -> {e}")
    results.append(False)

# 3. Chat Start (needs question_id, not question)
try:
    r = httpx.post(
        f"{base}/api/v1/chat/start",
        json={"question_id": "q_001"},
        timeout=10,
    )
    ok = r.status_code == 200
    data = json.dumps(r.json(), ensure_ascii=False)[:120]
    print(f"  [{'PASS' if ok else f'FAIL({r.status_code})':6s}] {'Chat Start':25s} -> {data}")
    results.append(ok)
except Exception as e:
    print(f"  [ERROR ] {'Chat Start':25s} -> {e}")
    results.append(False)

# 4. Chat Message
try:
    r = httpx.post(
        f"{base}/api/v1/chat/message",
        json={"session_id": "s1", "message": "我不懂"},
        timeout=10,
    )
    ok = r.status_code == 200
    data = json.dumps(r.json(), ensure_ascii=False)[:120]
    print(f"  [{'PASS' if ok else f'FAIL({r.status_code})':6s}] {'Chat Message':25s} -> {data}")
    results.append(ok)
except Exception as e:
    print(f"  [ERROR ] {'Chat Message':25s} -> {e}")
    results.append(False)

# 5. Correction Analyze (multipart file upload)
try:
    fake_draft = io.BytesIO(b"fake_draft_data")
    files = {"image": ("draft.jpg", fake_draft, "image/jpeg")}
    r = httpx.post(f"{base}/api/v1/correction/analyze", files=files, timeout=10)
    ok = r.status_code == 200
    data = json.dumps(r.json(), ensure_ascii=False)[:120]
    print(f"  [{'PASS' if ok else f'FAIL({r.status_code})':6s}] {'Correction Analyze':25s} -> {data}")
    results.append(ok)
except Exception as e:
    print(f"  [ERROR ] {'Correction Analyze':25s} -> {e}")
    results.append(False)

# 6. Diagnosis Report
try:
    r = httpx.get(f"{base}/api/v1/diagnosis/report?user_id=u1", timeout=10)
    ok = r.status_code == 200
    data = json.dumps(r.json(), ensure_ascii=False)[:120]
    print(f"  [{'PASS' if ok else f'FAIL({r.status_code})':6s}] {'Diagnosis Report':25s} -> {data}")
    results.append(ok)
except Exception as e:
    print(f"  [ERROR ] {'Diagnosis Report':25s} -> {e}")
    results.append(False)

# 7. Visualize Execute (query params)
try:
    r = httpx.post(
        f"{base}/api/v1/visualize/execute?code=print('hello')&language=python",
        timeout=10,
    )
    ok = r.status_code == 200
    data = json.dumps(r.json(), ensure_ascii=False)[:120]
    print(f"  [{'PASS' if ok else f'FAIL({r.status_code})':6s}] {'Visualize Execute':25s} -> {data}")
    results.append(ok)
except Exception as e:
    print(f"  [ERROR ] {'Visualize Execute':25s} -> {e}")
    results.append(False)

# Summary
sep = "=" * 60
print(f"\n{sep}")
passed = sum(results)
total = len(results)
print(f"  Result: {passed}/{total} passed")
if passed == total:
    print("  All endpoints OK! Frontend-Backend integration verified.")
else:
    print("  Some endpoints failed - check details above.")
print(sep)
