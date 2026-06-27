import base64
import hashlib
import json
from pathlib import Path

from backend.collectors.codex_auth import derive_account_label, load_codex_auth


def _fake_jwt(payload: dict[str, str]) -> str:
    header = base64.urlsafe_b64encode(b'{"alg":"none"}').decode().rstrip("=")
    body = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    return f"{header}.{body}.signature"


def test_auth_metadata_never_serializes_token(tmp_path):
    identity = json.loads(
        Path("backend/tests/fixtures/fake_codex_identity.json").read_text(encoding="utf-8")
    )
    access_token = _fake_jwt({"sub": "access-subject"})
    identity_token = _fake_jwt(identity)
    codex_home = tmp_path / "codex-home"
    codex_home.mkdir()
    (codex_home / "auth.json").write_text(
        json.dumps(
            {
                "tokens": {
                    "access_token": access_token,
                    "id_token": identity_token,
                },
                "last_refresh": "fake-refresh-time",
            }
        ),
        encoding="utf-8",
    )

    auth = load_codex_auth(codex_home)
    metadata = auth.safe_account_metadata()
    serialized = json.dumps(metadata, sort_keys=True)

    assert auth.access_token == access_token
    assert "access_token" not in metadata
    assert access_token not in serialized
    assert identity_token not in serialized
    expected_hash = hashlib.sha256(f"openai:codex:{identity['sub']}".encode()).hexdigest()
    assert metadata["account_key_hash"] == expected_hash
    assert metadata["account_label"] == "local"
    assert metadata["account_name"] == "Local Test"
    assert identity["email"] not in serialized
    assert all(key not in serialized for key in ("id_token", "refresh_token", "authorization"))


def test_account_label_prefers_email_local_part_and_rejects_paths():
    assert derive_account_label("leblackstock0@example.test", "Lauren") == "leblackstock0"
    assert derive_account_label(None, "Lauren") == "Lauren"
    assert derive_account_label(None, "C:\\private\\account") is None
