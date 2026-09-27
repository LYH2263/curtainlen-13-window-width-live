import json


def estimate(client, wid=1, fid=1, save=False):
    return client.get(
        "/api/estimate",
        params={"window_id": wid, "fabric_id": fid, "save": str(save).lower()},
    )


def test_wider_window_raises_or_holds(client):
    # 基线：客厅落地窗 3.0m 宽，遮光1.4m 门幅
    before = estimate(client).json()
    assert before["finished_width"] == 6.0
    assert before["panels"] == 5
    assert before["meters"] == 14.25

    # 详情页保存更大窗宽（3.0 -> 4.0）
    r = client.put("/api/windows/1", json={"width": 4.0})
    assert r.status_code == 200
    assert r.json()["width"] == 4.0

    after = estimate(client).json()
    assert after["finished_width"] > before["finished_width"]
    assert after["panels"] >= before["panels"]
    assert after["meters"] >= before["meters"]
    assert after["finished_width"] == 8.0
    assert after["panels"] == 6
    assert after["meters"] == 17.1


def test_same_or_panel_boundary_width_never_drops(client):
    # 加大但没跨过下一幅门槛：成品宽上升、幅数不变；
    # meters = panels * cut_h 只随幅数走，因此此档持平而非上升，但绝不降
    before = estimate(client).json()
    client.put("/api/windows/1", json={"width": 3.05})
    after = estimate(client).json()
    assert after["finished_width"] > before["finished_width"]
    assert after["panels"] == before["panels"]
    assert after["meters"] == before["meters"] == 14.25


def test_non_positive_width_rejected(client):
    for bad in (0, -1.2):
        r = client.put("/api/windows/1", json={"width": bad})
        assert r.status_code == 422
    # 落库值未被污染
    assert client.get("/api/windows/1").json()["width"] == 3.0


def test_nan_width_rejected(client):
    r = client.put("/api/windows/1", content=json.dumps({"width": float("nan")}),
                   headers={"Content-Type": "application/json"})
    assert r.status_code == 422
    assert client.get("/api/windows/1").json()["width"] == 3.0


def test_update_missing_window_404(client):
    r = client.put("/api/windows/999", json={"width": 1.0})
    assert r.status_code == 404


def test_saved_run_keeps_snapshot_after_widen(client):
    # 保存一次 run（3.0m 宽）
    saved = estimate(client, save=True).json()
    run_id = saved["run_id"]
    assert saved["finished_width"] == 6.0

    # 事后把窗改宽
    client.put("/api/windows/1", json={"width": 4.0})

    # 重新试算反映新宽，但已保存 run 打开仍是落库值
    runs = client.get("/api/runs").json()["items"]
    row = next(r for r in runs if r["id"] == run_id)
    assert row["result"]["finished_width"] == 6.0
    assert row["result"]["panels"] == saved["panels"]
    assert row["result"]["meters"] == saved["meters"]


def test_list_width_matches_estimate_window_width(client):
    client.put("/api/windows/1", json={"width": 4.2})
    listed = next(x for x in client.get("/api/windows").json()["items"] if x["id"] == 1)
    detail = client.get("/api/windows/1").json()
    calc = estimate(client).json()["window"]
    # 列表、详情、测算读窗三处必须同一口径
    assert listed["width"] == detail["width"] == calc["width"] == 4.2
