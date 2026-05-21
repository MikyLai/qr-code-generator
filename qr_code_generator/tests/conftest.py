"""
pytest fixtures：
- blob storage 全部 mock（不需要啟動 Azurite）
- 使用 SQLite in-memory DB（每次測試都是乾淨的）
- 提供 FastAPI TestClient
"""
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

# SQLite in-memory，每次測試結束自動清空
TEST_DATABASE_URL = "sqlite://"


@pytest.fixture()
def client():
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    # Mock 所有 blob storage 呼叫，不需要 Azurite
    with patch("app.routes.upload_qr_png", return_value=None), \
         patch("app.blob_storage.ensure_container", return_value=None):
        with TestClient(app) as c:
            yield c

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
