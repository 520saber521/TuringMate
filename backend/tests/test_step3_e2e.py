"""Step 3 端到端联调测试 - 拍照搜题全流程."""
import io
import sys
import httpx
import json

if sys.platform == "win32":
    import io as _io
    sys.stdout = _io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = _io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

base = "http://localhost:8000"
print("=" * 60)
print("  Step 3: Photo Search E2E Test")
print("=" * 60)

# 1. Health check
r = httpx.get(f"{base}/health", timeout=5)
assert r.status_code == 200, f"Health failed: {r.status_code}"
print(f"[PASS] Health Check: {r.json()}")

# 2. Subjects endpoint (new)
r = httpx.get(f"{base}/api/v1/question/subjects", timeout=5)
assert r.status_code == 200, f"Subjects failed: {r.status_code}"
data = r.json()
subjects = [s["name"] for s in data["subjects"]]
print(f"[PASS] Subjects: {subjects}")

# 3. Parse question with fake image (multipart upload)
fake_img = io.BytesIO(b"fake_image_data_for_test")
files = {"image": ("test_question.jpg", fake_img, "image/jpeg")}
print("\n[TEST] Calling /question/parse (LLM multimodal)...")
try:
    r = httpx.post(f"{base}/api/v1/question/parse", files=files, timeout=45)
    if r.status_code == 200:
        result = r.json()
        print(f"[PASS] Question Parse:")
        print(f"       ID:       {result['question_id']}")
        print(f"       Subject:  {result['subject']}")
        print(f"       Difficulty: {result['difficulty']}")
        print(f"       Tags:     {result['knowledge_tags']}")
        print(f"       Content:  {result['content'][:100]}...")
    else:
        print(f"[FAIL] Status: {r.status_code} | {r.text[:200]}")
except Exception as e:
    print(f"[ERR]  Parse error: {e}")

# 4. Test Chat Start with parsed question_id
try:
    if r.status_code == 200:
        qid = r.json()["question_id"]
        cr = httpx.post(
            f"{base}/api/v1/chat/start",
            json={"question_id": qid},
            timeout=15,
        )
        if cr.status_code == 200:
            chat_data = cr.json()
            print(f"\n[PASS] Chat Start (with parsed Q):")
            print(f"       Session:   {chat_data['session_id']}")
            print(f"       First msg: {chat_data['first_message'][:80]}...")
            print(f"       Stage:     {chat_data['stage']}")
        else:
            print(f"[FAIL] Chat start: {cr.status_code} | {cr.text[:150]}")
except Exception as e:
    print(f"[ERR]  Chat error: {e}")

print("\n" + "=" * 60)
print("  Step 3 E2E Test Complete!")
print("=" * 60)
