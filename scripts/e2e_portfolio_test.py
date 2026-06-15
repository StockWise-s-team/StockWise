import asyncio
import json
import os
import sys
import urllib.request
import urllib.error
import http.cookiejar
import time
from datetime import datetime, timezone

# Add parent directory to sys.path to import app modules inside the container
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

async def publish_price_update(symbol, price):
    producer = RabbitMQProducer()
    await producer.connect()
    
    price_payload = {
        "symbol": symbol.upper(),
        "price": float(price),
        "source": "vnstock_price_board",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": "price.updated"
    }
    
    print(f"Publishing mock price update: {symbol} @ {price:,.0f} VND...")
    await producer.publish("market.exchange", "price.updated", price_payload)
    await producer.close()
    await asyncio.sleep(2)  # Give the listener time to process

async def main():
    print("======================================================")
    print("=== RUNNING STOCKWISE PORTFOLIO & SANDBOX E2E TEST ===")
    print("======================================================")

    # 1. Login
    print("\n[STEP 1] Logging in...")
    status, login = request(
        "POST",
        f"{GATEWAY}/auth/login",
        {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    )
    if status != 200:
        print(f"ERROR: Login failed (HTTP {status}): {login}")
        sys.exit(1)
    
    token = login["accessToken"]
    auth_headers = {"Authorization": f"Bearer {token}"}
    print("Login successful.")

    # 2. Get baseline
    print("\n[STEP 2] Fetching initial baseline snapshot...")
    status, portfolio = request("GET", f"{GATEWAY}/portfolio", headers=auth_headers)
    if status != 200:
        print(f"ERROR: Failed to fetch portfolio (HTTP {status})")
        sys.exit(1)

    initial_cash = float(portfolio["portfolio"]["virtualCash"])
    initial_fpt_holding = next((h for h in portfolio["holdings"] if h["symbol"] == "FPT"), None)
    initial_fpt_qty = int(initial_fpt_holding["quantity"]) if initial_fpt_holding else 0
    initial_fpt_avg = float(initial_fpt_holding["avgPrice"]) if initial_fpt_holding else 0.0

    print(f"Baseline virtual cash: {initial_cash:,.0f} VND")
    print(f"Baseline FPT quantity: {initial_fpt_qty}")
    print(f"Baseline FPT avg price: {initial_fpt_avg:,.2f} VND")

    # 3. Test Order Cancellation
    print("\n[STEP 3] Testing Order Placement & Cancellation...")
    cancel_order_price = 125000.00
    cancel_order_qty = 10
    buy_request = {
        "symbol": "FPT",
        "type": "BUY",
        "quantity": cancel_order_qty,
        "price": cancel_order_price
    }
    status, order_res = request("POST", f"{GATEWAY}/portfolio/order", body=buy_request, headers=auth_headers)
    if status != 201:
        print(f"ERROR: Failed to place order for cancellation (HTTP {status})")
        sys.exit(1)
        
    order_id = order_res["order_id"]
    print(f"Pending order placed. ID: {order_id}")

    # Verify cash decreased by quantity * price (10 * 125,000 = 1,250,000)
    status, portfolio = request("GET", f"{GATEWAY}/portfolio", headers=auth_headers)
    post_place_cash = float(portfolio["portfolio"]["virtualCash"])
    expected_post_place_cash = initial_cash - (cancel_order_qty * cancel_order_price)
    print(f"Cash after order: {post_place_cash:,.0f} VND (Expected: {expected_post_place_cash:,.0f} VND)")
    if abs(post_place_cash - expected_post_place_cash) > 1.0:
        print("ERROR: Cash reservation calculation is incorrect!")
        sys.exit(1)

    # Cancel the order
    print("Canceling the pending order...")
    status, cancel_res = request("DELETE", f"{GATEWAY}/portfolio/order/{order_id}", headers=auth_headers)
    if status != 200:
        print(f"ERROR: Failed to cancel order (HTTP {status})")
        sys.exit(1)

    # Verify cash restored
    status, portfolio = request("GET", f"{GATEWAY}/portfolio", headers=auth_headers)
    post_cancel_cash = float(portfolio["portfolio"]["virtualCash"])
    print(f"Cash after cancel: {post_cancel_cash:,.0f} VND (Expected: {initial_cash:,.0f} VND)")
    if abs(post_cancel_cash - initial_cash) > 1.0:
        print("ERROR: Cash refund upon cancellation is incorrect!")
        sys.exit(1)
    print("Order cancellation test PASSED.")

    # 4. E2E Buy Order with Price Improvement (Refund)
    print("\n[STEP 4] Testing BUY order with price improvement refund...")
    limit_price = 135000.00
    buy_qty = 10
    buy_request = {
        "symbol": "FPT",
        "type": "BUY",
        "quantity": buy_qty,
        "price": limit_price
    }
    status, order_res = request("POST", f"{GATEWAY}/portfolio/order", body=buy_request, headers=auth_headers)
    if status != 201:
        print(f"ERROR: Failed to place BUY order (HTTP {status})")
        sys.exit(1)
        
    buy_order_id = order_res["order_id"]
    print(f"Buy order placed. ID: {buy_order_id}")

    # Trigger matching at a lower price (130,000 VND)
    match_price = 130000.00
    await publish_price_update("FPT", match_price)

    # Fetch updated portfolio
    status, portfolio = request("GET", f"{GATEWAY}/portfolio", headers=auth_headers)
    final_cash = float(portfolio["portfolio"]["virtualCash"])
    final_fpt_holding = next((h for h in portfolio["holdings"] if h["symbol"] == "FPT"), None)
    final_fpt_qty = int(final_fpt_holding["quantity"]) if final_fpt_holding else 0
    final_fpt_avg = float(final_fpt_holding["avgPrice"]) if final_fpt_holding else 0.0

    print(f"\nResults of BUY match:")
    print(f"Available cash: {final_cash:,.0f} VND")
    print(f"FPT quantity: {final_fpt_qty}")
    print(f"FPT average price: {final_fpt_avg:,.2f} VND")

    # Verification calculations
    # Expected cash: initial_cash - (buy_qty * match_price)
    expected_final_cash = initial_cash - (buy_qty * match_price)
    # Expected FPT quantity: initial_fpt_qty + buy_qty
    expected_fpt_qty = initial_fpt_qty + buy_qty
    # Expected avg price (weighted average):
    expected_fpt_avg = ((initial_fpt_qty * initial_fpt_avg) + (buy_qty * match_price)) / expected_fpt_qty

    print(f"Expected cash: {expected_final_cash:,.0f} VND")
    print(f"Expected FPT quantity: {expected_fpt_qty}")
    print(f"Expected FPT average price: {expected_fpt_avg:,.2f} VND")

    assert abs(final_cash - expected_final_cash) < 1.0, f"Cash verification failed: {final_cash} != {expected_final_cash}"
    assert final_fpt_qty == expected_fpt_qty, f"Qty verification failed: {final_fpt_qty} != {expected_fpt_qty}"
    assert abs(final_fpt_avg - expected_fpt_avg) < 1.0, f"Avg price verification failed: {final_fpt_avg} != {expected_fpt_avg}"
    
    print("BUY order and price improvement test PASSED.")

    # 5. E2E Sell Order with Realized P/L calculation
    print("\n[STEP 5] Testing SELL order with Realized P/L check...")
    sell_qty = 10
    sell_limit_price = 135000.00
    
    # Get initial realized P&L
    status, pnl_res = request("GET", f"{GATEWAY}/portfolio/pnl", headers=auth_headers)
    initial_realized_pnl = float(pnl_res["totalPnl"]) if (status == 200 and isinstance(pnl_res, dict)) else 0.0
    print(f"Initial Realized P/L: {initial_realized_pnl:,.2f} VND")

    # Place SELL order
    sell_request = {
        "symbol": "FPT",
        "type": "SELL",
        "quantity": sell_qty,
        "price": sell_limit_price
    }
    status, order_res = request("POST", f"{GATEWAY}/portfolio/order", body=sell_request, headers=auth_headers)
    if status != 201:
        print(f"ERROR: Failed to place SELL order (HTTP {status})")
        sys.exit(1)
        
    sell_order_id = order_res["order_id"]
    print(f"Sell order placed. ID: {sell_order_id}")

    # Trigger matching at 140,000 VND
    await publish_price_update("FPT", sell_limit_price)

    # Fetch updated state
    status, portfolio = request("GET", f"{GATEWAY}/portfolio", headers=auth_headers)
    final_cash_2 = float(portfolio["portfolio"]["virtualCash"])
    final_fpt_holding_2 = next((h for h in portfolio["holdings"] if h["symbol"] == "FPT"), None)
    final_fpt_qty_2 = int(final_fpt_holding_2["quantity"]) if final_fpt_holding_2 else 0

    status, pnl_res = request("GET", f"{GATEWAY}/portfolio/pnl", headers=auth_headers)
    final_realized_pnl = float(pnl_res["totalPnl"]) if (status == 200 and isinstance(pnl_res, dict)) else 0.0

    print(f"\nResults of SELL match:")
    print(f"Available cash: {final_cash_2:,.0f} VND")
    print(f"FPT quantity: {final_fpt_qty_2}")
    print(f"Realized P/L: {final_realized_pnl:,.2f} VND")

    # Calculate expected realized P&L based on transaction history matching the backend logic
    tx_list = portfolio.get("transactions", [])
    positions = {}
    expected_realized_pnl = 0.0
    for tx in sorted(tx_list, key=lambda t: t.get("executedAt", t.get("executed_at", ""))):
        sym = tx["symbol"].upper()
        if sym == "FPT":
            if sym not in positions:
                positions[sym] = {"qty": 0, "total_cost": 0.0}
            pos = positions[sym]
            qty_tx = int(tx["quantity"])
            price_tx = float(tx["price"])
            if tx["type"] == "BUY":
                pos["qty"] += qty_tx
                pos["total_cost"] += qty_tx * price_tx
            elif tx["type"] == "SELL":
                if pos["qty"] > 0:
                    matched = min(pos["qty"], qty_tx)
                    avg_cost = pos["total_cost"] / pos["qty"]
                    expected_realized_pnl += (price_tx - avg_cost) * matched
                    pos["qty"] -= matched
                    pos["total_cost"] = avg_cost * pos["qty"]

    expected_final_cash_2 = final_cash + (sell_qty * sell_limit_price)

    print(f"Expected cash: {expected_final_cash_2:,.0f} VND")
    print(f"Expected FPT quantity: {expected_fpt_qty - sell_qty}")
    print(f"Expected Realized P/L: {expected_realized_pnl:,.2f} VND")

    assert abs(final_cash_2 - expected_final_cash_2) < 1.0, f"Cash verification failed: {final_cash_2} != {expected_final_cash_2}"
    assert final_fpt_qty_2 == expected_fpt_qty - sell_qty, f"Qty verification failed: {final_fpt_qty_2} != {expected_fpt_qty - sell_qty}"
    assert abs(final_realized_pnl - expected_realized_pnl) < 1.0, f"Realized P/L verification failed: {final_realized_pnl} != {expected_realized_pnl}"

    print("SELL order and Realized P/L test PASSED.")

    print("\n=======================================================")
    print("=== SUCCESS: ALL PORTFOLIO INTEGRATION TESTS PASSED ===")
    print("=======================================================")

if __name__ == "__main__":
    asyncio.run(main())
