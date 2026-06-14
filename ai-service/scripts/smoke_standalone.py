import asyncio
import json
import sys
from typing import Any

import httpx


async def post_stream(client: httpx.AsyncClient, message: str) -> dict[str, Any]:
    response = await client.post("/api/v1/advisor/chat", json={"message": message})
    response.raise_for_status()
    envelopes = [
        json.loads(line.removeprefix("data: "))
        for line in response.text.splitlines()
        if line.startswith("data: ")
    ]
    final = next((event for event in envelopes if event["type"] == "final"), None)
    if not final:
        raise RuntimeError(f"Advisor stream has no final event for: {message}")
    return final["data"]


async def smoke(base_url: str) -> None:
    headers = {
        "X-Dev-User-Id": "00000000-0000-0000-0000-000000000001",
        "Accept": "text/event-stream",
    }
    async with httpx.AsyncClient(base_url=base_url, headers=headers, timeout=30) as client:
        readiness = (await client.get("/api/v1/health/ready")).json()
        assert readiness["required"]["postgres"] == "ok"
        for symbol in ("FPT", "HPG", "VNM"):
            final = await post_stream(client, f"Phan tich {symbol} hom nay")
            assert final["symbols"] == [symbol]
            assert final["data_mode"] == "demo"
        missing = await post_stream(client, "Phan tich ABC hom nay")
        assert "INSUFFICIENT_DATA" in missing["risk_flags"]
        assert missing["citations"] == []
    print("Standalone smoke passed for FPT, HPG, VNM, and missing-data behavior.")


if __name__ == "__main__":
    asyncio.run(smoke(sys.argv[1] if len(sys.argv) > 1 else "http://localhost:18000"))
