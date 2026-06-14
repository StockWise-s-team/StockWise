"""
Test _run_once logic của stream_c runner với mock DB + RabbitMQ.

Chạy:
    cd data-pipeline
    python tests/test_stream_c_runner.py
"""
import asyncio
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SYMBOLS = ["VHM", "VCB", "TCB"]


class MockProducer:
    """RabbitMQ producer giả — chỉ in ra payload thay vì gửi."""
    published = []

    async def connect(self):
        print("[MockProducer] connect() called")

    async def publish(self, exchange_name, routing_key, data):
        self.published.append(data)
        print(f"[MockProducer] publish to {exchange_name}/{routing_key}")
        print(f"  symbols: {data.get('symbols')}")
        print(f"  record_count: {data.get('record_count')}")
        print(f"  source: {data.get('source')}")
        sample = (data.get("prices") or [None])[0]
        if sample:
            print(f"  sample price fields: {list(sample.keys())}")

    async def close(self):
        print("[MockProducer] close() called")


class MockPriceRepo:
    """PriceRepository giả — trả về danh sách symbols cố định."""
    def get_tracked_symbols(self):
        return SYMBOLS


class MockRunRepo:
    """PipelineRunsRepository giả."""
    def create_run(self, **kwargs):
        print(f"[MockRunRepo] create_run({kwargs})")
        return "mock-run-id"

    def add_symbol_result(self, run_id, symbol, status, error_msg=None):
        print(f"[MockRunRepo]   {symbol} → {status}")

    def finish_run(self, run_id, status, errors):
        print(f"[MockRunRepo] finish_run: status={status}, errors={errors}")


async def main():
    from app.stream_c.fetcher import PriceBoardFetcher
    from app.stream_c import runner

    price_repo = MockPriceRepo()
    fetcher = PriceBoardFetcher()
    producer = MockProducer()

    # Patch run_repo trong runner để không cần DB
    original_repo_class = runner.PipelineRunsRepository
    runner.PipelineRunsRepository = lambda: MockRunRepo()

    print("=" * 50)
    print("[Test] Running _run_once with mock dependencies...")
    print("=" * 50)

    try:
        await runner._run_once(price_repo, fetcher, producer)
    finally:
        runner.PipelineRunsRepository = original_repo_class

    print("\n[Test] PASSED ✓" if producer.published else "\n[Test] WARN: nothing published")


if __name__ == "__main__":
    asyncio.run(main())
