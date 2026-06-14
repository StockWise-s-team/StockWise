import asyncio
import json
import os
import sys
import urllib.request
import urllib.error
import http.cookiejar
from datetime import datetime, timezone

# Add parent directory to sys.path to import app modules
sys.path.append("/app")

from app.rabbitmq.producer import RabbitMQProducer

GATEWAY = "http://api-gateway:8080"
ADMIN_EMAIL = os.getenv("DEV_ADMIN_EMAIL", "admin@stockwise.local")
ADMIN_PASSWORD = os.getenv("DEV_ADMIN_PASSWORD", "password123")
COOKIE_JAR = http.cookiejar.CookieJar()
OPENER = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(COOKIE_JAR))

def request(method, url, body=None, headers=None, timeout=10):
    data = None
    req_headers = dict(headers or {})
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        req_headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=data, headers=req_headers, method=method)
    try:
        with OPENER.open(req, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
            try:
                parsed = json.loads(raw) if raw else None
            except json.JSONDecodeError:
                parsed = raw
            return response.status, parsed
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8")
        try:
            parsed = json.loads(raw) if raw else None
        except json.JSONDecodeError:
            parsed = raw
        return exc.code, parsed

async def main():
    print("=== STARTING PORTFOLIO & SANDBOX INTEGRATION TEST ===")

    # 1. Login to get token
    print("Logging in...")
    status, login = request(
        "POST",
        f"{GATEWAY}/auth/login",
        {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    )
    if status != 200:
        print(f"Login failed: HTTP {status}, {login}")
        sys.exit(1)

    token = login["accessToken"]
    auth_headers = {"Authorization": f"Bearer {token}"}
    print("Login successful.")

    # 2. Get initial portfolio snapshot
    print("\nFetching initial portfolio snapshot...")
    status, portfolio = request("GET", f"{GATEWAY}/portfolio", headers=auth_headers)
    if status != 200:
        print(f"Failed to fetch portfolio: HTTP {status}, {portfolio}")
        sys.exit(1)

    initial_cash = float(portfolio["portfolio"]["virtualCash"])
    initial_fpt_qty = next((h["quantity"] for h in portfolio["holdings"] if h["symbol"] == "FPT"), 0)
    print(f"Initial cash: {initial_cash:,.0f} VND")
    print(f"Initial FPT holding quantity: {initial_fpt_qty}")

    # 3. Place a BUY order for 10 FPT shares without specifying price (market price)
    print("\nPlacing BUY order for 10 FPT (market price)...")
    buy_request = {
        "symbol": "FPT",
        "type": "BUY",
        "quantity": 10
    }
    status, buy_result = request("POST", f"{GATEWAY}/portfolio/order", body=buy_request, headers=auth_headers)
    if status != 201:
        print(f"Failed to place BUY order: HTTP {status}, {buy_result}")
        sys.exit(1)

    order_id = buy_result["order_id"]
    print(f"Order placed successfully. Order ID: {order_id}, Status: {buy_result['status']}")

    # Check cash after placing order (should freeze cash based on fallback FPT price 73,500.00)
    status, portfolio = request("GET", f"{GATEWAY}/portfolio", headers=auth_headers)
    post_buy_cash = float(portfolio["portfolio"]["virtualCash"])
    expected_frozen = 10 * 73500.00
    print(f"Cash after order: {post_buy_cash:,.0f} VND (Frozen amount: {initial_cash - post_buy_cash:,.0f} VND, expected: {expected_frozen:,.0f} VND)")
    if abs((initial_cash - post_buy_cash) - expected_frozen) > 1.0:
        print(f"Warning: Frozen cash does not match expected market price of FPT (73,500)! actual frozen={initial_cash - post_buy_cash}")

    # 4. Publish mock price update to RabbitMQ
    print("\nConnecting to RabbitMQ and publishing price update event for FPT...")
    producer = RabbitMQProducer()
    await producer.connect()

    price_payload = {
        "symbols": ["FPT"],
        "prices": [{"symbol": "FPT", "close": 73500.00, "price": 73500.00}],
        "source": "vnstock_price_board",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "record_count": 1,
        "action": "price.updated"
    }

    await producer.publish("market.exchange", "price.updated", price_payload)
    await producer.close()
    print("Price update published to RabbitMQ. Waiting for matching processor to run...")

    # Wait for portfolio-service to consume RabbitMQ event and process match
    await asyncio.sleep(2)

    # 5. Verify order is FILLED and holdings updated
    print("\nFetching updated portfolio snapshot...")
    status, portfolio = request("GET", f"{GATEWAY}/portfolio", headers=auth_headers)

    final_fpt_qty = next((h["quantity"] for h in portfolio["holdings"] if h["symbol"] == "FPT"), 0)
    print(f"Final FPT holding quantity: {final_fpt_qty} (Expected: {initial_fpt_qty + 10})")

    if final_fpt_qty != initial_fpt_qty + 10:
        print("ERROR: Holdings did not update correctly after match!")
        sys.exit(1)

    print("SUCCESS: Order was matched and holdings updated successfully!")
    print("=== PORTFOLIO & SANDBOX INTEGRATION TEST PASSED ===")

if __name__ == "__main__":
    asyncio.run(main())
