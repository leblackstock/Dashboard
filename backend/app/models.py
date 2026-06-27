from pydantic import BaseModel, ConfigDict


class QuotaWindow(BaseModel):
    used_percent: float | None = None
    remaining_percent: float | None = None
    reset_at: str | None = None


class CodexUsageAccount(BaseModel):
    account_key_hash: str
    account_label: str | None = None
    account_name: str | None = None
    plan_type: str | None = None
    reset_credits_available: int | None = None
    quota_5h: QuotaWindow
    quota_weekly: QuotaWindow
    freshness: str
    confidence: str
    collected_at: str


class CodexUsageResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    accounts: list[CodexUsageAccount]
