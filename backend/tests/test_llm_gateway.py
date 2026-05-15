"""LLM Gateway 多模型连通测试脚本.

使用方式：
    cd backend
    .venv/Scripts/python.exe -m tests.test_llm_gateway

或单独测试某个模型：
    .venv/Scripts/python.exe -m tests.test_llm_gateway --model deepseek
    .venv/Scripts/python.exe -m tests.test_llm_gateway --model gpt-4o
    .venv/Scripts/python.exe -m tests.test_llm_gateway --model qwen

测试内容：
    1. 模型实例化（API Key 校验）
    2. 同步对话 chat()
    3. 流式对话 stream_chat()
"""

import asyncio
import sys
import os
import time
import io

# 修复 Windows GBK 编码问题
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# 确保项目根目录在 path 中
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.llm_gateway import llm_gateway


# 测试用 prompt（数学引导教学场景）
TEST_MESSAGES = [
    {
        "role": "system",
        "content": "你是 TuringMate 的苏格拉底式 AI 导师，擅长引导学生自主思考。请用中文回复，保持简洁。",
    },
    {"role": "user", "content": "你好！请用一句话介绍你自己。"},
]

STREAM_TEST_MESSAGES = [{"role": "user", "content": "请用3个关键词描述你的教学风格。"}]


def separator(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


async def test_model(model_name: str) -> dict:
    """单个模型的完整测试."""
    result = {
        "model": model_name,
        "chat_ok": False,
        "stream_ok": False,
        "chat_response": None,
        "chat_latency_ms": None,
        "error": None,
    }

    separator(f"Testing: {model_name}")

    # === Test 1: 同步对话 ===
    print(f"\n[1/2] Testing chat() ...")
    try:
        start = time.perf_counter()
        response = await llm_gateway.chat(TEST_MESSAGES, model=model_name)
        latency = (time.perf_counter() - start) * 1000

        result["chat_ok"] = True
        result["chat_response"] = response[:200] + ("..." if len(response) > 200 else "")
        result["chat_latency_ms"] = round(latency, 1)

        print(f"  OK! Latency: {latency:.0f}ms")
        print(f"  Response: {result['chat_response']}")
    except Exception as e:
        result["error"] = str(e)
        print(f"  FAILED: {e}")

    # === Test 2: 流式对话 ===
    print(f"\n[2/2] Testing stream_chat() ...")
    try:
        chunks = []
        start = time.perf_counter()
        async for chunk in llm_gateway.stream_chat(
            STREAM_TEST_MESSAGES, model=model_name
        ):
            chunks.append(chunk)
            print(chunk, end="", flush=True)
        latency = (time.perf_counter() - start) * 1000
        print()

        full_text = "".join(chunks)
        result["stream_ok"] = len(chunks) > 0
        print(
            f"\n  OK! Received {len(chunks)} chunks, total {len(full_text)} chars, {latency:.0f}ms"
        )
    except Exception as e:
        err_msg = str(e)
        if not result["error"]:
            result["error"] = err_msg
        print(f"  FAILED: {e}")

    return result


async def main():
    """运行所有模型测试."""
    args = sys.argv[1:]
    target_model = None
    for i, arg in enumerate(args):
        if arg in ("--model", "-m") and i + 1 < len(args):
            target_model = args[i + 1]

    models_to_test = [target_model] if target_model else ["deepseek", "gpt-4o", "qwen"]

    print("=" * 60)
    print("  TuringMate - LLM Gateway Connectivity Test")
    print("=" * 60)
    print(f"  Default model: {llm_gateway.default_model}")
    print(f"  Models to test: {models_to_test}")

    results = []
    for model_name in models_to_test:
        r = await test_model(model_name)
        results.append(r)

    # === Summary ===
    separator("Test Summary")
    for r in results:
        status = (
            "PASS"
            if (r["chat_ok"] and r["stream_ok"])
            else "PARTIAL"
            if (r["chat_ok"] or r["stream_ok"])
            else "FAIL"
        )
        chat_mark = "+" if r["chat_ok"] else "-"
        stream_mark = "+" if r["stream_ok"] else "-"
        latency_str = f"{r['chat_latency_ms']}ms" if r["chat_latency_ms"] else "N/A"
        print(
            f"  [{status}] {r['model']:12s} | chat={chat_mark} ({latency_str:>8s}) | "
            f"stream={stream_mark}"
        )
        if r["error"]:
            print(f"         Error: {r['error']}")

    all_pass = all(r["chat_ok"] for r in results)
    print("\n" + "=" * 60)
    if all_pass:
        print("  All models connected successfully!")
    else:
        print("  Some tests failed - check .env configuration")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
