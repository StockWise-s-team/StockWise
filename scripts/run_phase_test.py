import urllib.request
import urllib.error
import json
import sys
import base64
import uuid
import os
import time

# Configuration
GATEWAY_URL = "http://localhost:18080"
RABBITMQ_URL = "http://localhost:15672"
TEST_SYMBOL = "SSI"
STATE_FILE = os.path.join(os.path.dirname(__file__), "session_state.json")

# Parameters
BUY_PRICE = 30000.00
BUY_MATCH_PRICE = 29500.00
BUY_QTY = 100
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
    except Exception as e:
        return 500, str(e)

def load_state():
    if not os.path.exists(STATE_FILE):
        return {}
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_state(state):
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=4)
    except Exception as e:
        print(f"[-] Warning: Failed to save session state: {e}")

def get_auth_headers(state):
    token = state.get("accessToken")
    if not token:
        print("[-] Error: Access token not found in session state. Please run Phase 1 first!")
        sys.exit(1)
    return {"Authorization": f"Bearer {token}"}

def run_phase_1():
    print("\n[PHASE 1] Registering a new unique user...")
    unique_id = str(uuid.uuid4())[:8]
    email = f"phase.test.{unique_id}@stockwise.com"
    password = "demopassword123"
    
    register_body = {
        "email": email,
        "password": password,
        "fullName": f"Phase Test User {unique_id}"
    }
    
    status, reg_res = make_request(f"{GATEWAY_URL}/auth/register", "POST", register_body)
    if status != 200:
        print(f"[-] Registration failed with HTTP {status}: {reg_res}")
        return
    
    token = reg_res["accessToken"]
    
    # Save newly registered user state
    state = {
        "email": email,
        "password": password,
        "accessToken": token,
        "initial_cash": 100000000.00
    }
    save_state(state)
    print(f"[+] Registration successful.")
    print(f"[+] Account Email: {email}")
    print(f"[+] Password     : {password}")
    print(f"[+] Access Token saved to session state.")
    print(f"[+] Run the next phase with: python scripts/run_phase_test.py 2")

def run_phase_2(state):
    print("\n[PHASE 2] Fetching initial portfolio and placing PENDING BUY order...")
    auth_headers = get_auth_headers(state)
    
    status, pf_res = make_request(f"{GATEWAY_URL}/portfolio", "GET", headers=auth_headers)
    if status != 200:
        print(f"[-] Failed to fetch portfolio: {pf_res}")
        return
        
    initial_cash = float(pf_res["portfolio"]["virtualCash"])
    state["initial_cash"] = initial_cash
    print(f"[+] Initial Virtual Cash: {initial_cash:,.2f} VND")
    
    print(f"[*] Placing a PENDING BUY order for {TEST_SYMBOL}: {BUY_QTY} @ {BUY_PRICE:,.2f} VND...")
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
    state["buy_order_id"] = buy_order_id
    save_state(state)
    
    print(f"[+] BUY Order placed successfully. Order ID: {buy_order_id}")
    print(f"[+] Status: PENDING")
    
    # Verify cash lock
    status, pf_res_2 = make_request(f"{GATEWAY_URL}/portfolio", "GET", headers=auth_headers)
    post_buy_order_cash = float(pf_res_2["portfolio"]["virtualCash"])
    expected_lock_cash = initial_cash - (BUY_PRICE * BUY_QTY)
    print(f"[+] Available Virtual Cash after lock: {post_buy_order_cash:,.2f} VND (Expected: {expected_lock_cash:,.2f} VND)")
    
    print(f"[+] Run the next phase with: python scripts/run_phase_test.py 3")

def run_phase_3(state):
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
    
    status, rmq_res = make_request(
        f"{RABBITMQ_URL}/api/exchanges/%2f/market.exchange/publish", 
        "POST", rmq_body_buy, rmq_headers
    )
    
    if status != 200:
        print(f"[-] Failed to publish BUY price event: {rmq_res}")
        return
    print(f"[+] Price update event published successfully to RabbitMQ: {rmq_res}")
    print(f"[+] Run the next phase with: python scripts/run_phase_test.py 4")

def run_phase_4(state):
    print("\n[PHASE 4] Verifying BUY order matching & asset updates...")
    auth_headers = get_auth_headers(state)
    buy_order_id = state.get("buy_order_id")
    if not buy_order_id:
        print("[-] Error: No BUY order ID found. Please run Phase 2 first!")
        return

    # Check order status
    status, orders_res = make_request(f"{GATEWAY_URL}/portfolio/orders", "GET", headers=auth_headers)
    buy_order_found = next((o for o in orders_res if o["id"] == buy_order_id), None)
    
    if not buy_order_found:
        print("[-] BUY order not found in history!")
        return
    print(f"[+] BUY Order Status: {buy_order_found['status']} (Expected: FILLED)")
    
    # Verify assets
    status, pf_res = make_request(f"{GATEWAY_URL}/portfolio", "GET", headers=auth_headers)
    current_cash = float(pf_res["portfolio"]["virtualCash"])
    expected_post_buy_cash = state["initial_cash"] - (BUY_MATCH_PRICE * BUY_QTY)
    print(f"[+] Virtual Cash after BUY match: {current_cash:,.2f} VND (Expected: {expected_post_buy_cash:,.2f} VND)")
    
    holdings = pf_res.get("holdings", [])
    holding = next((h for h in holdings if h["symbol"] == TEST_SYMBOL), None)
    if not holding:
        print(f"[-] Holdings for {TEST_SYMBOL} not found!")
        return
        
    print(f"[+] Holdings quantity: {holding['quantity']} (Expected: {BUY_QTY})")
    print(f"[+] Avg Price: {float(holding['avgPrice']):,.2f} VND (Expected: {BUY_MATCH_PRICE:,.2f} VND)")
    
    print(f"[+] Run the next phase with: python scripts/run_phase_test.py 5")

def run_phase_5(state):
    print(f"\n[PHASE 5] Placing PENDING SELL order for {TEST_SYMBOL} and checking share lock...")
    auth_headers = get_auth_headers(state)
    
    print(f"[*] Placing a PENDING SELL order for {TEST_SYMBOL}: {SELL_QTY} @ {SELL_PRICE:,.2f} VND...")
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
    state["sell_order_id"] = sell_order_id
    save_state(state)
    
    print(f"[+] SELL Order placed successfully. Order ID: {sell_order_id}")
    print(f"[+] Status: PENDING")
    
    # Check share lock
    status, pf_res = make_request(f"{GATEWAY_URL}/portfolio", "GET", headers=auth_headers)
    holdings = pf_res.get("holdings", [])
    holding = next((h for h in holdings if h["symbol"] == TEST_SYMBOL), None)
    expected_lock_qty = BUY_QTY - SELL_QTY
    print(f"[+] Available Holdings Quantity after lock: {holding['quantity'] if holding else 0} (Expected: {expected_lock_qty})")
    
    print(f"[+] Run the next phase with: python scripts/run_phase_test.py 6")

def run_phase_6(state):
    print(f"\n[PHASE 6] Simulating market price update for SELL and verifying final assets...")
    auth_headers = get_auth_headers(state)
    sell_order_id = state.get("sell_order_id")
    if not sell_order_id:
        print("[-] Error: No SELL order ID found. Please run Phase 5 first!")
        return
        
    # Simulate price update for SELL
    credentials = base64.b64encode(b"guest:guest").decode("utf-8")
    rmq_headers = {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/json"
    }
    
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
        print(f"[-] Failed to publish SELL price event: {rmq_res}")
        return
    print(f"[+] Price update event published successfully to RabbitMQ: {rmq_res}")
    
    print("[*] Waiting 2 seconds for matching to process before final check...")
    time.sleep(2)
    
    # Verify final state
    status, orders_res = make_request(f"{GATEWAY_URL}/portfolio/orders", "GET", headers=auth_headers)
    sell_order_found = next((o for o in orders_res if o["id"] == sell_order_id), None)
    if not sell_order_found:
        print("[-] SELL order not found in history!")
        return
    print(f"[+] SELL Order Status: {sell_order_found['status']} (Expected: FILLED)")
    
    status, pf_res = make_request(f"{GATEWAY_URL}/portfolio", "GET", headers=auth_headers)
    final_cash = float(pf_res["portfolio"]["virtualCash"])
    expected_final_cash = state["initial_cash"] - (BUY_MATCH_PRICE * BUY_QTY) + (SELL_MATCH_PRICE * SELL_QTY)
    print(f"[+] Final Virtual Cash: {final_cash:,.2f} VND (Expected: {expected_final_cash:,.2f} VND)")
    
    holdings = pf_res.get("holdings", [])
    holding = next((h for h in holdings if h["symbol"] == TEST_SYMBOL), None)
    expected_final_holdings = BUY_QTY - SELL_QTY
    print(f"[+] Final Holdings: {holding['quantity'] if holding else 0} shares (Expected: {expected_final_holdings} shares)")
    
    if holding and int(holding['quantity']) == expected_final_holdings and abs(final_cash - expected_final_cash) < 0.01:
        print("\n==================================================================")
        print(" [SUCCESS] PHASE-BY-PHASE TEST CYCLE COMPLETED SUCCESSFULLY!")
        print(f" Account details: {state['email']} / {state['password']}")
        print("==================================================================")
        
        # Clean up session state file
        if os.path.exists(STATE_FILE):
            os.remove(STATE_FILE)
            print("[+] Session state file cleaned up.")
    else:
        print("\n[-] Verification failed: Cash or holdings mismatch.")

def print_usage():
    print("Usage: python scripts/run_phase_test.py <phase_number>")
    print("Available phases:")
    print("  1 - Register a new unique user & save access token")
    print("  2 - Place PENDING BUY order and verify locked cash")
    print("  3 - Publish BUY match event (29.5k) to RabbitMQ")
    print("  4 - Verify BUY order matches and updates assets")
    print("  5 - Place PENDING SELL order and verify locked shares")
    print("  6 - Publish SELL match event (31.5k) to RabbitMQ & verify final assets")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
        
    phase = sys.argv[1]
    state = load_state()
    
    if phase == "1":
        run_phase_1()
    elif phase == "2":
        run_phase_2(state)
    elif phase == "3":
        run_phase_3(state)
    elif phase == "4":
        run_phase_4(state)
    elif phase == "5":
        run_phase_5(state)
    elif phase == "6":
        run_phase_6(state)
    else:
        print(f"[-] Invalid phase number: {phase}")
        print_usage()
        sys.exit(1)
