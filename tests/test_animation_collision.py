import os
from pathlib import Path
from importlib import reload

from fastapi.testclient import TestClient


def create_app(tmp_path):
    """Create a fresh FastAPI app instance using a temporary upload directory."""
    os.environ["UPLOADS_DIR"] = str(tmp_path)

    from backend import server as server_module

    reload(server_module)

    # Override authentication dependency to bypass token checks
    from backend.models import User

    async def override_get_current_user():
        return User(id="test-user", email="test@example.com", full_name="Test User")

    server_module.app.dependency_overrides[server_module.get_current_user] = override_get_current_user
    return server_module.app


def test_animation_json_collisions(tmp_path):
    app = create_app(tmp_path)

    file_content_1 = b'{"v":"5","fr":30,"ip":0,"op":10,"w":100,"h":100,"layers":[]}'
    file_content_2 = b'{"v":"5","fr":30,"ip":0,"op":20,"w":200,"h":100,"layers":[]}'

    headers = {"Authorization": "Bearer test"}

    with TestClient(app) as client:
        resp1 = client.post(
            "/api/templates/upload",
            files={"file": ("animation.json", file_content_1, "application/json")},
            data={"source": "upload"},
            headers=headers,
        )
        assert resp1.status_code == 200, resp1.text

        resp2 = client.post(
            "/api/templates/upload",
            files={"file": ("animation.json", file_content_2, "application/json")},
            data={"source": "upload"},
            headers=headers,
        )
        assert resp2.status_code == 200, resp2.text

    url1 = resp1.json()["file_url"]
    url2 = resp2.json()["file_url"]

    assert url1 != url2

    path1 = tmp_path / Path(url1).name
    path2 = tmp_path / Path(url2).name

    assert path1.read_bytes() == file_content_1
    assert path2.read_bytes() == file_content_2

