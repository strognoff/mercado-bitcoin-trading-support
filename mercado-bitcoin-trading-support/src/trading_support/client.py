from __future__ import annotations

import hashlib
import hmac
import json
import time
from typing import Any

import requests

from trading_support.config import TradingConfig


class MercadoBitcoinClient:
    def __init__(self, config: TradingConfig) -> None:
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})

    def _sign(self, method: str, path: str, body: dict | None = None) -> dict[str, str]:
        timestamp = str(int(time.time()))
        payload = (json.dumps(body, separators=(',', ':'), sort_keys=True) if body else "")
        message = f"{timestamp}{method.upper()}{path}{payload}"
        signature = hmac.new(
            self.config.api_secret.encode(), message.encode(), hashlib.sha256
        ).hexdigest()

        return {
            self.config.auth_headers.key: self.config.api_key,
            self.config.auth_headers.signature: signature,
            self.config.auth_headers.timestamp: timestamp,
        }

    def _request(self, method: str, path: str, body: dict | None = None) -> Any:
        url = f"{self.config.base_url.rstrip('/')}{path}"
        headers = self._sign(method, path, body)
        if body:
            headers["Content-Type"] = "application/json"
        response = self.session.request(method, url, json=body, headers=headers, timeout=15)
        response.raise_for_status()
        return response.json()

    def ticker(self, symbol: str) -> dict[str, Any]:
        params = {"symbols": symbol}
        resp = self.session.get(
            f"{self.config.base_url.rstrip('/')}/tickers", params=params, timeout=15
        )
        resp.raise_for_status()
        parsed = resp.json()
        if isinstance(parsed, list) and parsed:
            return parsed[0]
        return parsed

    def place_order(
        self,
        symbol: str,
        side: str,
        amount: float,
        price: float | None = None,
        order_type: str = "limit",
    ) -> dict[str, Any]:
        body = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "amount": str(amount),
        }
        if price is not None:
            body["price"] = str(price)
        return self._request("POST", "/orders", body)
