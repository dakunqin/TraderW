import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import settings
from app.db.session import get_engine
from app.main import create_app


@pytest.fixture()
def client():
    settings.database_url = "sqlite:///:memory:"
    get_engine.cache_clear()
    app = create_app()
    with TestClient(app) as c:
        yield c
