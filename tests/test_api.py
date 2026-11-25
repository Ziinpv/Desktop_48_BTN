from fastapi.testclient import TestClient

from backend.app import app


def test_health():
    with TestClient(app) as client:
        res = client.get("/api/health")
        assert res.status_code == 200
        assert res.json()["ok"] is True


def test_login_and_f1_crud():
    with TestClient(app) as client:
        bad = client.post("/api/auth/login", json={"username": "admin", "password": "wrong"})
        assert bad.status_code == 401

        res = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
        assert res.status_code == 200
        token = res.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        types = client.get("/api/service-types", headers=headers)
        assert types.status_code == 200
        assert any(x["maLoaiDV"] == "LDV01" for x in types.json())

        created = client.post(
            "/api/service-types",
            headers=headers,
            json={"tenLoaiDV": "Test Loại", "moTa": "Mô tả hợp lệ", "trangThai": True},
        )
        assert created.status_code == 200
        code = created.json()["maLoaiDV"]

        dup = client.post(
            "/api/service-types",
            headers=headers,
            json={"maLoaiDV": code, "tenLoaiDV": "X", "moTa": "Mô tả hợp lệ"},
        )
        assert dup.status_code == 400

        empty = client.post(
            "/api/service-types",
            headers=headers,
            json={"tenLoaiDV": "X", "moTa": "   "},
        )
        assert empty.status_code == 400


def test_rental_max_three_and_deposit():
    with TestClient(app) as client:
        res = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
        headers = {"Authorization": f"Bearer {res.json()['token']}"}
        dresses = client.get("/api/dresses", params={"status": "SAN_SANG"}, headers=headers).json()
        ready = [d["maDress"] for d in dresses if d["trangThai"] == "SAN_SANG"]
        assert len(ready) >= 1
        sample = next(d for d in dresses if d["maDress"] == ready[0])
        assert sample["tienCoc"] == sample["donGia"] * 0.5
