import math

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app import seed
from app.engines.curtain_math import fabric_meters
from app.repositories import history, windows
from app.routers.windows import update_window
from app.schemas.window import WindowUpdate
from app.services.estimate_service import run_estimate

W1, F1 = 1, 1  # 种子：客厅落地窗 3.0x2.6 fullness2.0 clean；遮光1.4m hems 0.10/0.15


@pytest.fixture
def db(monkeypatch, tmp_path):
    # connect() 每次调用读取 app.db 模块全局 DB_PATH，patch 后所有仓储与 seed 都落临时库
    monkeypatch.setattr("app.db.DB_PATH", tmp_path / "test.db")
    seed.init_db()


def _triple(r):
    return r["finished_width"], r["panels"], r["meters"]


def test_update_width_takes_effect_and_scales_up(db):
    before = run_estimate(W1, F1, False, "")
    assert _triple(before) == (6.0, 5, 14.25)
    assert before["cut_height"] == 2.85

    updated = windows.update_width(W1, 5.0)
    assert updated["width"] == 5.0

    after = run_estimate(W1, F1, False, "")
    assert _triple(after) == (10.0, 8, 22.8)
    assert after["cut_height"] == 2.85  # 改宽不影响裁剪高
    # 响应自带的 window 行就是参与计算的同一行，宽度口径一致
    assert after["window"]["width"] == 5.0


def test_width_sequence_never_decreases(db):
    prev = None
    for width in (3.0, 3.0, 4.2, 5.0):
        windows.update_width(W1, width)
        cur = _triple(run_estimate(W1, F1, False, ""))
        if prev is not None:
            assert cur[0] >= prev[0]
            assert cur[1] >= prev[1]
            assert cur[2] >= prev[2]
        prev = cur
    assert prev == (10.0, 8, 22.8)


def test_rejects_non_positive_width_without_side_effect(db):
    for bad in (0, -1, float("inf"), float("-inf"), float("nan")):
        with pytest.raises(ValueError):
            windows.update_width(W1, bad)
        assert windows.get_window(W1)["width"] == 3.0
    # 不存在的窗户合法宽度 -> None（404），不抛 ValueError
    assert windows.update_width(999, 1.0) is None


def test_saved_run_keeps_snapshot_after_width_changes(db):
    saved = run_estimate(W1, F1, True, "")
    run_id = saved["run_id"]
    old = _triple(saved)
    assert old == (6.0, 5, 14.25)

    windows.update_width(W1, 5.0)
    live = run_estimate(W1, F1, False, "")
    assert _triple(live) == (10.0, 8, 22.8)  # live 已用新宽

    snap = history.get_run(run_id)
    assert snap["window_name"] == "客厅落地窗"
    assert (snap["result"]["finished_width"],
            snap["result"]["panels"],
            snap["result"]["meters"]) == old  # 落库值不随后续改窗变化


def test_engine_monotonic_sweep():
    # 固定其余入参，小步长扫描成品宽/幅/米数对窗宽单调不减
    params = dict(window_h=2.6, fullness=2.0, hem_top=0.10, hem_bottom=0.15,
                  fabric_width=1.4)
    prev = None
    width = 0.01
    while width <= 6.0:
        r = fabric_meters(width, **params)
        cur = _triple(r)
        if prev is not None:
            assert cur[0] >= prev[0]
            assert cur[1] >= prev[1]
            assert cur[2] >= prev[2]
        prev = cur
        width += 0.007

    # 门幅整数倍边界（成品宽 = k * 1.4，即窗宽 = k * 0.7）附近 epsilon 不造成回落
    boundary = []
    for k in range(1, 8):
        for delta in (-1e-7, 0.0, 1e-7):
            boundary.append(fabric_meters(k * 0.7 + delta, **params))
    for a, b in zip(boundary, boundary[1:]):
        assert b["panels"] >= a["panels"]


def test_window_update_schema():
    assert WindowUpdate(width=3.5).width == 3.5
    for bad in (0, -2, "x"):
        with pytest.raises(ValidationError):
            WindowUpdate(width=bad)
    # Pydantic 默认放行 Infinity，所以仓储层的 isfinite 防线不可省
    assert math.isinf(WindowUpdate(width=float("inf")).width)


def test_route_404_for_missing_window(db):
    with pytest.raises(HTTPException) as exc:
        update_window(999, WindowUpdate(width=1.0))
    assert exc.value.status_code == 404
    assert history.get_run(999) is None
