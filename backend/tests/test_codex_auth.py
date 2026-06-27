import base64
import json

from backend.collectors.codex_auth import load_codex_auth


def _fake_jwt(payload: dict[str, str]) -> str:
    header = base64.urlsafe_b64encode(b'{"alg":"none"}').decode().rstrip("=")
    body = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    return f"{header}.{body}.signature"


def test_auth_metadata_never_serializes_token(tmp_path):
    token = _fake_jwt(
        {
            "sub": "fake-subject-123",
            "email": "local@example.test",
            "name": "Local Test",
        }
    )
    codex_home = tmp_path / "codex-home"
    codex_home.mkdir()
    (codex_home / "auth.json").write_text(
        json.dumps({"tokens": {"access_token": token}, "last_refresh": "fake-refresh-time"}),
        encoding="utf-8",
    )

    auth = load_codex_auth(codex_home)
    metadata = auth.safe_account_metadata()
    serialized = json.dumps(metadata, sort_keys=True)

    assert auth.access_token == token
    assert "access_token" not in metadata
    assert token not in serialized
    assert metadata["account_key_hash"]
    assert metadata["account_label"] == "local@example.test"
