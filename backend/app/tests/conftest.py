import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app import db, seed
from app.main import app


@pytest.fixture()
def client(tmp_path, monkeypatch):
    db_path = tmp_path / "app.db"
    monkeypatch.setattr(db, "DB_PATH", db_path)
    seed.init_db()
    with TestClient(app) as c:
        yield c
