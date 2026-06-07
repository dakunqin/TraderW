from datetime import datetime, timezone


def test_end_to_end_flow(client):
    r = client.post("/api/v1/auth/register", json={"email": "a@example.com", "password": "password123"})
    assert r.status_code == 200

    r = client.post("/api/v1/auth/login", json={"email": "a@example.com", "password": "password123"})
    assert r.status_code == 200
    tokens = r.json()
    access = tokens["access_token"]

    r = client.post("/api/v1/api-keys", headers={"Authorization": f"Bearer {access}"})
    assert r.status_code == 200
    api_key = r.json()["api_key"]

    payload = {
        "mt5_account": {
            "mt5_login": "123456",
            "mt5_server": "Broker-Server",
            "mt5_company": "Broker",
            "currency": "USD",
            "balance": 1000,
            "equity": 1005,
            "margin": 10,
        },
        "orders": [
            {
                "ticket": 11,
                "symbol": "EURUSD",
                "order_type": "buy_limit",
                "volume": 0.1,
                "price_open": 1.0,
                "sl": 0,
                "tp": 0,
                "time_setup": None,
                "time_done": None,
            }
        ],
        "positions": [
            {
                "ticket": 22,
                "symbol": "GBPUSD",
                "position_type": "buy",
                "volume": 0.2,
                "price_open": 1.0,
                "sl": 0,
                "tp": 0,
                "profit": 1.0,
                "time_open": None,
            }
        ],
        "sent_at": datetime.now(timezone.utc).isoformat(),
    }
    r = client.post("/api/v1/mt5/sync", json=payload, headers={"X-API-Key": api_key})
    assert r.status_code == 200

    r = client.get("/api/v1/mt5-accounts", headers={"Authorization": f"Bearer {access}"})
    assert r.status_code == 200
    accounts = r.json()
    assert len(accounts) == 1
    acc_id = accounts[0]["id"]

    r = client.get(f"/api/v1/mt5-accounts/{acc_id}/orders", headers={"Authorization": f"Bearer {access}"})
    assert r.status_code == 200
    orders = r.json()
    assert len(orders) == 1
    order_id = orders[0]["id"]

    r = client.post(f"/api/v1/orders/{order_id}/close", headers={"Authorization": f"Bearer {access}"})
    assert r.status_code == 200
    action_id = r.json()["id"]

    r = client.get("/api/v1/mt5/actions", params={"mt5_login": "123456", "mt5_server": "Broker-Server"}, headers={"X-API-Key": api_key})
    assert r.status_code == 200
    actions = r.json()["actions"]
    assert len(actions) == 1
    assert actions[0]["id"] == action_id

    r = client.post(
        "/api/v1/mt5/action-results",
        json={"action_id": action_id, "status": "success", "error_code": None, "error_message": None, "executed_at": datetime.now(timezone.utc).isoformat()},
        headers={"X-API-Key": api_key},
    )
    assert r.status_code == 200

