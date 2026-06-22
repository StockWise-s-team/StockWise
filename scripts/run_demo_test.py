import urllib.request
import urllib.error
import json
import time
import base64
import uuid

# Configuration
GATEWAY_URL = "http://localhost:18080"
RABBITMQ_URL = "http://localhost:15672"
TEST_SYMBOL = "SSI"

# Buy Order parameters
BUY_PRICE = 30000.00
BUY_MATCH_PRICE = 29500.00
BUY_QTY = 100

# Sell Order parameters
SELL_PRICE = 31000.00
SELL_MATCH_PRICE = 31500.00
SELL_QTY = 50

def make_request(url, method="GET", body=None, headers=None):
    req_headers = dict(headers or {})
    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        req_headers["Content-Type"] = "application/json"
    
    req = urllib.request.Request(url, data=data, headers=req_headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            res_body = response.read().decode("utf-8")
            return response.status, json.loads(res_body) if res_body else None
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        try:
            parsed_err = json.loads(err_body)
        except Exception:
            parsed_err = err_body
        return e.code, parsed_err

def main():
    print("==================================================================")
    print("    STOCKWISE AUTOMATED DEMO TEST (BUY & SELL E2E MATCH FLOW)     ")
    print("==================================================================")

    # ----------------------------------------------------------------
    # PHASE 1: Register unique user and obtain JWT token
    # ----------------------------------------------------------------
    print("\n[PHASE 1] Registering a new unique user...")
    unique_id = str(uuid.uuid4())[:8]
    email = f"demo.e2e.{unique_id}@stockwise.com"
    register_body = {
        "email": email,
        "password": "demopassword123",
        "fullName": f"Demo User {unique_id}"
    }
    
    status, reg_res = make_request(f"{GATEWAY_URL}/auth/register", "POST", register_body)
    if status != 200:
        print(f"[-] Registration failed with HTTP {status}: {reg_res}")
        return
    
    token = reg_res["accessToken"]
    auth_headers = {"Authorization": f"Bearer {token}"}
    print(f"[+] Registration successful for: {email}")
    print(f"[+] JWT Access Token obtained.")

    # ----------------------------------------------------------------
    # PHASE 2: Check initial portfolio and place PENDING buy order
    # ----------------------------------------------------------------
    print("\n[PHASE 2] Fetching initial portfolio baseline...")
    status, pf_res = make_request(f"{GATEWAY_URL}/portfolio", "GET", headers=auth_headers)
    if status != 200:
        print(f"[-] Failed to fetch portfolio: {pf_res}")
        return
        
    initial_cash = float(pf_res["portfolio"]["virtualCash"])
    print(f"[+] Initial Virtual Cash: {initial_cash:,.2f} VND")
    print(f"[+] Initial Holdings Count: {len(pf_res.get('holdings', []))}")

    print(f"\n[PHASE 2] Placing a PENDING BUY order for {TEST_SYMBOL} at {BUY_PRICE:,.2f} VND...")
    buy_order_body = {
        "symbol": TEST_SYMBOL,
        "type": "BUY",
        "quantity": BUY_QTY,
        "price": BUY_PRICE
    }
    
    status, buy_order_res = make_request(f"{GATEWAY_URL}/portfolio/order", "POST", buy_order_body, auth_headers)
    if status != 201:
        print(f"[-] Failed to place BUY order: {buy_order_res}")
        return
        
    buy_order_id = buy_order_res["order_id"]
    print(f"[+] BUY Order placed successfully. Order ID: {buy_order_id}")
    print(f"[+] Order Status: {buy_order_res['status']} (Expected: PENDING)")

    # Verify cash decreased due to lock
    status, pf_res_2 = make_request(f"{GATEWAY_URL}/portfolio", "GET", headers=auth_headers)
    post_buy_order_cash = float(pf_res_2["portfolio"]["virtualCash"])
    expected_lock_cash = initial_cash - (BUY_PRICE * BUY_QTY)
    print(f"[+] Available Virtual Cash after lock: {post_buy_order_cash:,.2f} VND (Expected: {expected_lock_cash:,.2f} VND)")

    # ----------------------------------------------------------------
    # PHASE 3: Simulating market price update for BUY match
    # ----------------------------------------------------------------
    print(f"\n[PHASE 3] Simulating market price update for {TEST_SYMBOL} @ {BUY_MATCH_PRICE:,.2f} VND...")
    
    credentials = base64.b64encode(b"guest:guest").decode("utf-8")
    rmq_headers = {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/json"
    }
    
    rmq_body_buy = {
        "properties": {},
        "routing_key": "price.updated",
        "payload": json.dumps({"symbol": TEST_SYMBOL, "price": BUY_MATCH_PRICE}),
        "payload_encoding": "string"
    }
    
    status, rmq_res_buy = make_request(
        f"{RABBITMQ_URL}/api/exchanges/%2f/market.exchange/publish", 
        "POST", 
        rmq_body_buy, 
        rmq_headers
    )
    
    if status != 200:
        print(f"[-] Failed to publish BUY price event to RabbitMQ: {rmq_res_buy}")
        return
    print(f"[+] Event published to RabbitMQ. Response: {rmq_res_buy}")
    
    print("[+] Waiting 3 seconds for async BUY order matching to complete...")
    time.sleep(3)

    # Verify BUY order was filled and cash refunded
    status, pf_res_3 = make_request(f"{GATEWAY_URL}/portfolio", "GET", headers=auth_headers)
    post_buy_match_cash = float(pf_res_3["portfolio"]["virtualCash"])
    expected_post_buy_cash = initial_cash - (BUY_MATCH_PRICE * BUY_QTY)
    print(f"[+] Virtual Cash after BUY match: {post_buy_match_cash:,.2f} VND (Expected: {expected_post_buy_cash:,.2f} VND)")
    
    holdings = pf_res_3.get("holdings", [])
    buy_holding = next((h for h in holdings if h["symbol"] == TEST_SYMBOL), None)
    if not buy_holding or buy_holding["quantity"] != BUY_QTY:
        print("[-] BUY order matching failed: Holdings quantity incorrect.")
        return
    print(f"[+] Holdings quantity: {buy_holding['quantity']} (Expected: {BUY_QTY})")
    print(f"[+] Holdings average price: {float(buy_holding['avgPrice']):,.2f} VND (Expected: {BUY_MATCH_PRICE:,.2f} VND)")

    # ----------------------------------------------------------------
    # PHASE 5: Place PENDING SELL order and check share reservation
    # ----------------------------------------------------------------
    print(f"\n[PHASE 5] Placing a PENDING SELL order for {TEST_SYMBOL} at {SELL_PRICE:,.2f} VND...")
    sell_order_body = {
        "symbol": TEST_SYMBOL,
        "type": "SELL",
        "quantity": SELL_QTY,
        "price": SELL_PRICE
    }
    
    status, sell_order_res = make_request(f"{GATEWAY_URL}/portfolio/order", "POST", sell_order_body, auth_headers)
    if status != 201:
        print(f"[-] Failed to place SELL order: {sell_order_res}")
        return
        
    sell_order_id = sell_order_res["order_id"]
    print(f"[+] SELL Order placed successfully. Order ID: {sell_order_id}")
    print(f"[+] Order Status: {sell_order_res['status']} (Expected: PENDING)")

    # Verify holdings quantity decreased (shares are reserved/locked)
    status, pf_res_4 = make_request(f"{GATEWAY_URL}/portfolio", "GET", headers=auth_headers)
    sell_holdings = pf_res_4.get("holdings", [])
    sell_holding = next((h for h in sell_holdings if h["symbol"] == TEST_SYMBOL), None)
    expected_lock_qty = BUY_QTY - SELL_QTY
    
    if not sell_holding:
         print(f"[-] Error: Holdings for {TEST_SYMBOL} vanished completely!")
         return
         
    print(f"[+] Available Holdings Quantity after lock: {sell_holding['quantity']} (Expected: {expected_lock_qty})")
    if sell_holding['quantity'] != expected_lock_qty:
         print("[-] Test failed: Holdings were not correctly locked/reserved.")
         return

    # ----------------------------------------------------------------
    # PHASE 6: Simulating market price update for SELL match & verification
    # ----------------------------------------------------------------
    print(f"\n[PHASE 6] Simulating market price update for {TEST_SYMBOL} @ {SELL_MATCH_PRICE:,.2f} VND...")
    rmq_body_sell = {
        "properties": {},
        "routing_key": "price.updated",
        "payload": json.dumps({"symbol": TEST_SYMBOL, "price": SELL_MATCH_PRICE}),
        "payload_encoding": "string"
    }
    
    status, rmq_res_sell = make_request(
        f"{RABBITMQ_URL}/api/exchanges/%2f/market.exchange/publish", 
        "POST", 
        rmq_body_sell, 
        rmq_headers
    )
    
    if status != 200:
        print(f"[-] Failed to publish SELL price event to RabbitMQ: {rmq_res_sell}")
        return
    print(f"[+] Event published to RabbitMQ. Response: {rmq_res_sell}")
    
    print("[+] Waiting 3 seconds for async SELL order matching to complete...")
    time.sleep(3)

    # Verify SELL order is FILLED
    status, orders_res = make_request(f"{GATEWAY_URL}/portfolio/orders", "GET", headers=auth_headers)
    sell_order_found = next((o for o in orders_res if o["id"] == sell_order_id), None)
    if not sell_order_found:
        print("[-] Placed SELL order not found in history!")
        return
    print(f"[+] Final SELL Order Status: {sell_order_found['status']} (Expected: FILLED)")
    if sell_order_found["status"] != "FILLED":
         print("[-] Test failed: SELL order was not filled.")
         return

    # Verify cash credited
    status, pf_res_5 = make_request(f"{GATEWAY_URL}/portfolio", "GET", headers=auth_headers)
    final_cash = float(pf_res_5["portfolio"]["virtualCash"])
    expected_final_cash = expected_post_buy_cash + (SELL_MATCH_PRICE * SELL_QTY)
    print(f"[+] Final Virtual Cash after SELL match: {final_cash:,.2f} VND (Expected: {expected_final_cash:,.2f} VND)")

    # Verify final holdings
    final_holdings = pf_res_5.get("holdings", [])
    final_holding = next((h for h in final_holdings if h["symbol"] == TEST_SYMBOL), None)
    
    if final_holding:
        final_holding_qty = int(final_holding["quantity"])
        print(f"[+] Final Holdings Quantity: {final_holding_qty} (Expected: {expected_lock_qty})")
        
        if final_holding_qty == expected_lock_qty and abs(final_cash - expected_final_cash) < 0.01:
            print("\n[SUCCESS] BOTH BUY & SELL E2E INTEGRATION TESTS PASSED SUCCESSFULLY!")
        else:
            print("\n[-] Verification failed: Final cash or holdings mismatch.")
    else:
        print("\n[-] Verification failed: Final holdings vanished.")

if __name__ == "__main__":
    main()
