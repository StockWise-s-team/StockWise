import json
import os
import sys
import time
import urllib.error
import urllib.request
import http.cookiejar


GATEWAY = "http://api-gateway:8080"
AI_SERVICE = "http://ai-service:8000"
DATA_PIPELINE = "http://data-pipeline:8001"
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


def wait_for(name, url, attempts=60):
    for _ in range(attempts):
        try:
            status, _ = request("GET", url, timeout=3)
            if 200 <= status < 500:
                print(f"OK wait {name}: HTTP {status}")
                return
        except Exception:
            pass
        time.sleep(2)
    raise RuntimeError(f"{name} did not become reachable: {url}")


def expect(label, method, url, expected, body=None, headers=None):
    status, payload = request(method, url, body=body, headers=headers)
    expected_set = expected if isinstance(expected, set) else {expected}
    if status not in expected_set:
        raise AssertionError(f"{label}: expected {expected_set}, got {status}, payload={payload}")
    print(f"OK {label}: HTTP {status}")
    return payload


def main():
    wait_for("gateway", f"{GATEWAY}/health")
    wait_for("ai-service", f"{AI_SERVICE}/api/v1/health")
    wait_for("data-pipeline", f"{DATA_PIPELINE}/health")

    expect("negative auth", "GET", f"{GATEWAY}/portfolio", 403)

    login = expect(
        "admin login",
        "POST",
        f"{GATEWAY}/auth/login",
        200,
        {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
    )
    token = login["accessToken"]
    if login.get("refreshToken"):
        raise AssertionError("admin login: refresh token should not be exposed in response body")
    auth_headers = {"Authorization": f"Bearer {token}"}

    refreshed = expect("refresh via cookie", "POST", f"{GATEWAY}/auth/refresh", 200)
    token = refreshed["accessToken"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    me = expect("auth me", "GET", f"{GATEWAY}/auth/me", 200, headers=auth_headers)
    if me.get("role") != "ROLE_ADMIN":
        raise AssertionError(f"auth me: expected ROLE_ADMIN, got {me.get('role')}")

    expect("market price", "GET", f"{GATEWAY}/market/price/FPT", 200, headers=auth_headers)
    expect("market ratio", "GET", f"{GATEWAY}/market/ratio/FPT", 200, headers=auth_headers)
    expect(
        "market ohlc",
        "GET",
        f"{GATEWAY}/market/ohlc/FPT?startDate=2026-01-01&endDate=2026-12-31",
        200,
        headers=auth_headers,
    )
    expect(
        "invalid market date",
        "GET",
        f"{GATEWAY}/market/ohlc/FPT?startDate=bad-date&endDate=2026-12-31",
        {400, 500},
        headers=auth_headers,
    )
    expect("portfolio", "GET", f"{GATEWAY}/portfolio", 200, headers=auth_headers)
    expect(
        "invalid portfolio order",
        "POST",
        f"{GATEWAY}/portfolio/order",
        {400, 422, 500},
        body={"symbol": "FPT", "side": "BUY", "quantity": -1, "price": 1000},
        headers=auth_headers,
    )
    expect("news sources", "GET", f"{GATEWAY}/news-sources", 200, headers=auth_headers)
    expect("tracked symbols", "GET", f"{GATEWAY}/tracked-symbols", 200, headers=auth_headers)
    expect("company wiki", "GET", f"{GATEWAY}/company-wiki/FPT", 200, headers=auth_headers)
    expect("pipeline status", "GET", f"{GATEWAY}/pipeline/status", 200, headers=auth_headers)
    expect("pipeline runs", "GET", f"{GATEWAY}/pipeline/runs/recent", 200, headers=auth_headers)
    expect("ai health via gateway", "GET", f"{GATEWAY}/api/v1/health", 200)
    expect("ai admin via gateway", "GET", f"{GATEWAY}/api/v1/admin/sources", 200, headers=auth_headers)

    print("Smoke test passed.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Smoke test failed: {exc}", file=sys.stderr)
        sys.exit(1)
