from __future__ import annotations

import json
import os
from pathlib import Path

from pydantic import BaseModel, Field, validator

ROOT = Path(__file__).resolve().parents[2]


class AuthHeaders(BaseModel):
    key: str = Field(..., description="Header name for the API key")
    signature: str = Field(..., description="Header name for the HMAC signature")
    timestamp: str = Field(..., description="Header name for the request timestamp")


class TradingConfig(BaseModel):
    api_key: str
    api_secret: str
    base_url: str = Field(
        default="https://api.mercadobitcoin.net/api/v4",
        description="Base REST endpoint for Mercado Bitcoin v4 API",
    )
    paper_trade: bool = Field(default=True, description="If true, orders are not sent to the exchange")
    telegram_target: str = Field(default="1214148381", description="Telegram id to message pre-trade briefs")
    auth_headers: AuthHeaders = Field(
        default_factory=lambda: AuthHeaders(key="X-ACCESS-KEY", signature="X-ACCESS-SIGN", timestamp="X-ACCESS-TIMESTAMP")
    )
    timezone: str = Field(default="UTC", description="Timezone used for timestamps")

    @validator("api_key", "api_secret")
    def not_empty(cls, v: str) -> str:
        if not v:
            raise ValueError("API key and secret must be provided in config")
        return v


def load_config(path: str | Path | None = None) -> TradingConfig:
    config_path = Path(path or os.environ.get("TRADING_SUPPORT_CONFIG") or ROOT / "config" / "config.json")
    if not config_path.exists():
        raise FileNotFoundError(
            f"Config file not found ({config_path}). Copy config/config.example.json and fill in your keys."
        )
    data = json.loads(config_path.read_text(encoding="utf-8"))
    return TradingConfig(**data)
