def test_create_qr(client):
    """POST /api/qr/create → 回傳 token、short_url、qr_code_url"""
    res = client.post("/api/qr/create", json={"url": "https://google.com"})
    assert res.status_code == 200
    data = res.json()
    assert "token" in data
    assert data["original_url"] == "https://google.com"
    assert "/r/" in data["short_url"]


def test_create_qr_missing_url(client):
    """POST /api/qr/create 沒給 url → 422"""
    res = client.post("/api/qr/create", json={})
    assert res.status_code == 422


def test_create_qr_invalid_url(client):
    """POST /api/qr/create 給無效 url → 422"""
    res = client.post("/api/qr/create", json={"url": "not-a-url"})
    assert res.status_code == 422


def test_redirect(client):
    """GET /r/{token} → 302 redirect 到原始 URL"""
    res = client.post("/api/qr/create", json={"url": "https://google.com"})
    token = res.json()["token"]

    res = client.get(f"/r/{token}", follow_redirects=False)
    assert res.status_code == 302
    assert res.headers["location"] == "https://google.com"


def test_redirect_not_found(client):
    """GET /r/不存在的token → 404"""
    res = client.get("/r/xxxxxxxx")
    assert res.status_code == 404


def test_get_qr_image(client):
    """GET /api/qr/{token}/image → 302 redirect 到 blob URL"""
    res = client.post("/api/qr/create", json={"url": "https://google.com"})
    token = res.json()["token"]

    res = client.get(f"/api/qr/{token}/image", follow_redirects=False)
    assert res.status_code == 302
    assert "fake-blob" in res.headers["location"]


def test_get_qr_info(client):
    """GET /api/qr/{token} → 回傳 mapping 資訊"""
    res = client.post("/api/qr/create", json={"url": "https://google.com"})
    token = res.json()["token"]

    res = client.get(f"/api/qr/{token}")
    assert res.status_code == 200
    assert res.json()["token"] == token


def test_delete_qr(client):
    """DELETE /api/qr/{token} → 刪除後 redirect 回 404"""
    res = client.post("/api/qr/create", json={"url": "https://google.com"})
    token = res.json()["token"]

    res = client.delete(f"/api/qr/{token}")
    assert res.status_code == 200

    res = client.get(f"/r/{token}")
    assert res.status_code == 404


def test_analytics(client):
    """GET /api/qr/{token}/analytics → 回傳掃描統計"""
    res = client.post("/api/qr/create", json={"url": "https://google.com"})
    token = res.json()["token"]

    res = client.get(f"/api/qr/{token}/analytics")
    assert res.status_code == 200
    data = res.json()
    assert data["token"] == token
    assert "total_scans" in data
