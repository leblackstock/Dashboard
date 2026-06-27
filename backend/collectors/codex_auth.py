import base64
import hashlib
import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from backend.app.settings import get_settings


class CodexAuthError(RuntimeError):
    pass


@dataclass
class CodexAuth:
    access_token: str = field(repr=False)
    account_key_hash: str
    account_label: str | None
    account_name: str | None
    auth_mode: str
    last_refresh: str | None = None

    def safe_account_metadata(self) -> dict[str, str | None]:
        return {
            "provider": "openai",
            "account_key_hash": self.account_key_hash,
            "account_label": self.account_label,
            "account_name": self.account_name,
            "auth_mode": self.auth_mode,
        }


ACCESS_TOKEN_KEYS = ("access_token", "accessToken")
IDENTITY_TOKEN_KEYS = ("id_token", "idToken")
MAX_IDENTITY_LENGTH = 160


def default_codex_home() -> Path:
    settings = get_settings()
    if settings.codex_home:
        return settings.codex_home
    env_home = os.environ.get("CODEX_HOME")
    if env_home:
        return Path(env_home)
    return Path.home() / ".codex"


def auth_file_candidates(codex_home: Path | None = None) -> list[Path]:
    home = codex_home or default_codex_home()
    return [
        home / "auth.json",
        home / "auth" / "auth.json",
        home / "codex-auth.json",
    ]


def load_codex_auth(codex_home: Path | None = None) -> CodexAuth:
    for candidate in auth_file_candidates(codex_home):
        if candidate.is_file():
            return _load_auth_file(candidate)
    raise CodexAuthError("codex_auth_not_found")


def _load_auth_file(path: Path) -> CodexAuth:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CodexAuthError("codex_auth_unreadable") from exc

    access_token = _find_first(data, ACCESS_TOKEN_KEYS)
    if not isinstance(access_token, str) or not access_token:
        raise CodexAuthError("codex_access_token_not_found")

    access_claims = _decode_jwt_payload(access_token)
    identity_token = _find_first(data, IDENTITY_TOKEN_KEYS)
    identity_claims = (
        _decode_jwt_payload(identity_token)
        if isinstance(identity_token, str) and identity_token
        else access_claims
    )
    identity = (
        _identity_from_claims(identity_claims)
        or _identity_from_claims(access_claims)
        or "openai:codex:unknown"
    )
    account_key_hash = hashlib.sha256(identity.encode("utf-8")).hexdigest()
    account_name = sanitize_identity_text(identity_claims.get("name"))
    account_label = derive_account_label(
        identity_claims.get("email") or identity_claims.get("preferred_username"),
        account_name,
    )
    last_refresh = _safe_str(
        _find_first(data, ("last_refresh", "lastRefresh", "updated_at", "updatedAt"))
    )

    return CodexAuth(
        access_token=access_token,
        account_key_hash=account_key_hash,
        account_label=account_label or "Codex account",
        account_name=account_name,
        auth_mode="codex_auth",
        last_refresh=last_refresh,
    )


def _find_first(value: Any, keys: tuple[str, ...]) -> Any:
    if isinstance(value, dict):
        for key in keys:
            if key in value and value[key] is not None:
                return value[key]
        for child in value.values():
            found = _find_first(child, keys)
            if found is not None:
                return found
    elif isinstance(value, list):
        for item in value:
            found = _find_first(item, keys)
            if found is not None:
                return found
    return None


def _decode_jwt_payload(token: str) -> dict[str, Any]:
    parts = token.split(".")
    if len(parts) < 2:
        return {}
    payload = parts[1]
    padding = "=" * (-len(payload) % 4)
    try:
        decoded = base64.urlsafe_b64decode(f"{payload}{padding}")
        claims = json.loads(decoded.decode("utf-8"))
    except (ValueError, json.JSONDecodeError):
        return {}
    return claims if isinstance(claims, dict) else {}


def _identity_from_claims(claims: dict[str, Any]) -> str | None:
    for key in ("sub", "account_id", "user_id", "email", "preferred_username"):
        value = claims.get(key)
        if value:
            return f"openai:codex:{value}"
    return None


def sanitize_identity_text(value: Any) -> str | None:
    if value is None:
        return None
    text = " ".join(str(value).split())
    if not text or len(text) > MAX_IDENTITY_LENGTH:
        return None
    lowered = text.lower()
    if ":\\" in text or lowered.startswith(("/users/", "/home/", "\\\\")):
        return None
    return text


def derive_account_label(email: Any, name: Any = None) -> str | None:
    safe_email = sanitize_identity_text(email)
    if safe_email and safe_email.count("@") == 1 and not any(char.isspace() for char in safe_email):
        local_part, domain = safe_email.split("@", maxsplit=1)
        if local_part and domain:
            return local_part
    return sanitize_identity_text(name)


def _safe_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
