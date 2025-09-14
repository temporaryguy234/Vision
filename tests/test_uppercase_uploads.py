import io
import json
import io
import json
import zipfile
from datetime import datetime
import importlib
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("UPLOADS_DIR", str(tmp_path))
    sys.path.append(str(Path(__file__).resolve().parents[1] / "backend"))
    # Provide a minimal aiohttp stub to satisfy imports in lottie_processor
    import types
    sys.modules.setdefault("aiohttp", types.SimpleNamespace(ClientSession=object))
    # Stub modules that are heavy or have external dependencies
    from dataclasses import dataclass, field
    @dataclass
    class _User:
        id: str
        email: str
        full_name: str
        subscription_tier: str = "free"
        credits_remaining: int = 0
        subscription_expires: None = None
        created_at: datetime = field(default_factory=datetime.utcnow)
        is_active: bool = True

    sys.modules['auth'] = types.SimpleNamespace(
        AuthService=object,
        get_current_user=lambda: None,
        get_current_user_optional=lambda: None,
        User=_User,
        UserCreate=object,
        UserLogin=object,
        GoogleAuthRequest=object,
    )
    from enum import Enum
    class _SubTier(str, Enum):
        FREE = "free"
        MID = "mid"
        PRO = "pro"
    sys.modules['subscription'] = types.SimpleNamespace(SubscriptionService=object, SubscriptionTier=_SubTier)
    sys.modules['payments'] = types.SimpleNamespace(PaymentService=object, PaymentIntent=object)
    sys.modules['ai_service'] = types.SimpleNamespace(ai_service=object, AIPromptRequest=object)
    sys.modules['export_service'] = types.SimpleNamespace(ExportService=object)
    class _FSM:
        def __init__(self, *args, **kwargs):
            pass
    sys.modules['file_storage'] = types.SimpleNamespace(FileStorageManager=_FSM)
    import os
    os.makedirs("/app/exports", exist_ok=True)
    import json as _json
    from datetime import datetime as _dt
    _orig_dumps = _json.dumps
    def _dumps(obj, *args, **kwargs):
        kwargs.setdefault('default', lambda o: o.isoformat() if isinstance(o, _dt) else str(o))
        return _orig_dumps(obj, *args, **kwargs)
    _json.dumps = _dumps
    import models
    models.get_database = lambda: None
    import builtins
    builtins.get_database = lambda: None
    import server
    importlib.reload(server)
    del builtins.get_database

    async def override_user():
        return server.User(
            id="test-user",
            email="test@example.com",
            full_name="Test User",
            subscription_tier="free",
            credits_remaining=0,
            subscription_expires=None,
            created_at=datetime.utcnow(),
            is_active=True,
        )

    server.app.dependency_overrides[server.get_current_user] = override_user

    with TestClient(server.app) as c:
        yield c

    server.app.dependency_overrides.clear()


def _basic_lottie_dict():
    return {"v": "5.7.4", "fr": 30, "ip": 0, "op": 1, "w": 100, "h": 100, "layers": []}


def test_upload_uppercase_json(client):
    data = json.dumps(_basic_lottie_dict()).encode("utf-8")
    file_obj = io.BytesIO(data)
    response = client.post(
        "/api/templates/upload",
        files={"file": ("sample.JSON", file_obj, "application/json")},
        data={"source": "upload"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "sample"


def test_upload_uppercase_lottie(client):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        zf.writestr("data.json", json.dumps(_basic_lottie_dict()))
    buffer.seek(0)
    response = client.post(
        "/api/templates/upload",
        files={"file": ("anim.LOTTIE", buffer, "application/octet-stream")},
        data={"source": "upload"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "anim"
