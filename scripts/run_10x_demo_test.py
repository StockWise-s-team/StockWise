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
    print("    STOCKWISE 10X E2E INTEGRATION TEST (SINGLE ACCOUNT)           ")
    print("==================================================================")

    # 1. Register unique user
    print("\n[STEP 1] Registering a new unique user...")
    unique_id = str(uuid.uuid4())[:8]
    email = f"demo.10x.{unique_id}@stockwise.com"
    register_body = {
        "email": email,
        "password": "demopassword123",
        "fullName": f"10x Test User {unique_id}"
    }
    
    status, reg_res = make_request(f"{GATEWAY_URL}/auth/register", "POST", register_body)
    if status != 200:
        print(f"[-] Registration failed with HTTP {status}: {reg_res}")
        return
    
    token = reg_res["accessToken"]
    auth_headers = {"Authorization": f"Bearer {token}"}
    print(f"[+] Registration successful for: {email}")
    print(f"[+] Credentials: {email} / demopassword123")

    # Fetch baseline portfolio
    status, pf_res = make_request(f"{GATEWAY_URL}/portfolio", "GET", headers=auth_headers)
    initial_cash = float(pf_res["portfolio"]["virtualCash"])
    print(f"[+] Initial Virtual Cash: {initial_cash:,.2f} VND")

    # RabbitMQ Auth Header & Payloads
    credentials = base64.b64encode(b"guest:guest").decode("utf-8")
    rmq_headers = {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/json"
    }

    current_expected_cash = initial_cash
    current_expected_holdings = 0

    # 10 iterations loop
    for i in range(1, 11):
        print(f"\n------------------------------------------------------------")
        print(f" ITERATION {i} / 10")
        print(f"------------------------------------------------------------")

        # --- BUY ORDER ---
        print(f"[*] Placing BUY order: {BUY_QTY} {TEST_SYMBOL} @ {BUY_PRICE:,.2f} VND...")
        buy_order_body = {
            "symbol": TEST_SYMBOL,
            "type": "BUY",
            "quantity": BUY_QTY,
            "price": BUY_PRICE
        }
        status, buy_order_res = make_request(f"{GATEWAY_URL}/portfolio/order", "POST", buy_order_body, auth_headers)
        if status != 201:
            print(f"[-] Failed to place BUY order in iteration {i}: {buy_order_res}")
            return
        
        buy_order_id = buy_order_res["order_id"]
        print(f"[+] BUY Order placed. ID: {buy_order_id}")

        # Simulate BUY match price update
        print(f"[*] Publishing BUY price update to RabbitMQ: {TEST_SYMBOL} @ {BUY_MATCH_PRICE:,.2f} VND...")
        rmq_body_buy = {
            "properties": {},
            "routing_key": "price.updated",
            "payload": json.dumps({"symbol": TEST_SYMBOL, "price": BUY_MATCH_PRICE}),
            "payload_encoding": "string"
        }
        status, rmq_res = make_request(
            f"{RABBITMQ_URL}/api/exchanges/%2f/market.exchange/publish", 
            "POST", rmq_body_buy, rmq_headers
        )
        if status != 200:
            print(f"[-] RabbitMQ publish failed: {rmq_res}")
            return
        
        print("[*] Waiting 2 seconds for BUY order match to process...")
        time.sleep(2)

        # Verify BUY result
        status, pf_res = make_request(f"{GATEWAY_URL}/portfolio", "GET", headers=auth_headers)
        current_cash = float(pf_res["portfolio"]["virtualCash"])
        holdings = pf_res.get("holdings", [])
        current_holding = next((h for h in holdings if h["symbol"] == TEST_SYMBOL), None)
        current_holding_qty = int(current_holding["quantity"]) if current_holding else 0

        current_expected_cash -= (BUY_MATCH_PRICE * BUY_QTY)
        current_expected_holdings += BUY_QTY

        print(f"[+] BUY verification:")
        print(f"    - Cash: {current_cash:,.2f} VND (Expected: {current_expected_cash:,.2f} VND)")
        print(f"    - Holdings: {current_holding_qty} shares (Expected: {current_expected_holdings} shares)")
        
        if abs(current_cash - current_expected_cash) > 0.01 or current_holding_qty != current_expected_holdings:
            print("[-] Verification failed after BUY match!")
            return

        # --- SELL ORDER ---
        print(f"[*] Placing SELL order: {SELL_QTY} {TEST_SYMBOL} @ {SELL_PRICE:,.2f} VND...")
        sell_order_body = {
            "symbol": TEST_SYMBOL,
            "type": "SELL",
            "quantity": SELL_QTY,
            "price": SELL_PRICE
        }
        status, sell_order_res = make_request(f"{GATEWAY_URL}/portfolio/order", "POST", sell_order_body, auth_headers)
        if status != 201:
            print(f"[-] Failed to place SELL order in iteration {i}: {sell_order_res}")
            return
        
        sell_order_id = sell_order_res["order_id"]
        print(f"[+] SELL Order placed. ID: {sell_order_id}")

        # Simulate SELL match price update
        print(f"[*] Publishing SELL price update to RabbitMQ: {TEST_SYMBOL} @ {SELL_MATCH_PRICE:,.2f} VND...")
        rmq_body_sell = {
            "properties": {},
            "routing_key": "price.updated",
            "payload": json.dumps({"symbol": TEST_SYMBOL, "price": SELL_MATCH_PRICE}),
            "payload_encoding": "string"
        }
        status, rmq_res = make_request(
            f"{RABBITMQ_URL}/api/exchanges/%2f/market.exchange/publish", 
            "POST", rmq_body_sell, rmq_headers
        )
        if status != 200:
            print(f"[-] RabbitMQ publish failed: {rmq_res}")
            return
        
        print("[*] Waiting 2 seconds for SELL order match to process...")
        time.sleep(2)

        # Verify SELL result
        status, pf_res = make_request(f"{GATEWAY_URL}/portfolio", "GET", headers=auth_headers)
        current_cash = float(pf_res["portfolio"]["virtualCash"])
        holdings = pf_res.get("holdings", [])
        current_holding = next((h for h in holdings if h["symbol"] == TEST_SYMBOL), None)
        current_holding_qty = int(current_holding["quantity"]) if current_holding else 0

        current_expected_cash += (SELL_MATCH_PRICE * SELL_QTY)
        current_expected_holdings -= SELL_QTY

        print(f"[+] SELL verification:")
        print(f"    - Cash: {current_cash:,.2f} VND (Expected: {current_expected_cash:,.2f} VND)")
        print(f"    - Holdings: {current_holding_qty} shares (Expected: {current_expected_holdings} shares)")
        
        if abs(current_cash - current_expected_cash) > 0.01 or current_holding_qty != current_expected_holdings:
            print("[-] Verification failed after SELL match!")
            return

    print("\n==================================================================")
    print(" [SUCCESS] 10 ITERATIONS COMPLETED AND VERIFIED SUCCESSFULLY!")
    print(f" Account details: {email} / demopassword123")
    print(f" Final Cash: {current_cash:,.2f} VND (Expected: 86,250,000.00 VND)")
    print(f" Final Holdings: {current_holding_qty} {TEST_SYMBOL} (Expected: 500 shares)")
    print("==================================================================")

if __name__ == "__main__":
    main()
