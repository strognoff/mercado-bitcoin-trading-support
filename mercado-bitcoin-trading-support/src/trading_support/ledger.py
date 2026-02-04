from __future__ import annotations

import csv
import json
import sqlite3
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]


@dataclass
class TradeRecord:
    id: str
    timestamp: str
    asset: str
    side: str
    entry_price: float
    size: float
    reasoning: str
    exit_logic: str
    status: str
    pre_trade_message: str
    order_id: str | None = None
    exit_price: float | None = None
    exit_time: str | None = None
    realized_pnl: float | None = None
    exit_note: str | None = None


class Ledger:
    def __init__(self, path: str | Path | None = None) -> None:
        self.db_path = Path(path or ROOT / "data" / "trades.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._ensure_table()

    def _ensure_table(self) -> None:
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS trades (
                id TEXT PRIMARY KEY,
                timestamp TEXT,
                asset TEXT,
                side TEXT,
                entry_price REAL,
                size REAL,
                reasoning TEXT,
                exit_logic TEXT,
                status TEXT,
                pre_trade_message TEXT,
                order_id TEXT,
                exit_price REAL,
                exit_time TEXT,
                realized_pnl REAL,
                exit_note TEXT
            )
            """
        )
        self.conn.commit()

    def create_trade(
        self,
        asset: str,
        side: str,
        entry_price: float,
        size: float,
        reasoning: str,
        exit_logic: str,
        summary: str,
        status: str = "pending",
    ) -> str:
        trade_id = str(uuid.uuid4())
        ts = datetime.now(timezone.utc).isoformat()
        self.conn.execute(
            "INSERT INTO trades (id, timestamp, asset, side, entry_price, size, reasoning, exit_logic, status, pre_trade_message) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (trade_id, ts, asset, side, entry_price, size, reasoning, exit_logic, status, summary),
        )
        self.conn.commit()
        return trade_id

    def mark_executed(self, trade_id: str, entry_price: float, order_id: str | None = None) -> None:
        self.conn.execute(
            "UPDATE trades SET entry_price = ?, status = 'executed', order_id = ? WHERE id = ?",
            (entry_price, order_id, trade_id),
        )
        self.conn.commit()

    def settle_trade(self, trade_id: str, exit_price: float, note: str | None = None) -> TradeRecord:
        row = self.conn.execute("SELECT * FROM trades WHERE id = ?", (trade_id,)).fetchone()
        if not row:
            raise ValueError(f"Trade {trade_id} not found")
        entry_price = row["entry_price"]
        if entry_price is None:
            raise ValueError("Entry price not recorded yet")
        size = row["size"]
        side = row["side"]
        pnl = (exit_price - entry_price) * size if side.lower() == "buy" else (entry_price - exit_price) * size
        exit_time = datetime.now(timezone.utc).isoformat()
        self.conn.execute(
            "UPDATE trades SET exit_price = ?, exit_time = ?, realized_pnl = ?, status = 'closed', exit_note = ? WHERE id = ?",
            (exit_price, exit_time, pnl, note, trade_id),
        )
        self.conn.commit()
        return self._row_to_record(self.conn.execute("SELECT * FROM trades WHERE id = ?", (trade_id,)).fetchone())

    def get_trade(self, trade_id: str) -> TradeRecord | None:
        row = self.conn.execute("SELECT * FROM trades WHERE id = ?", (trade_id,)).fetchone()
        if not row:
            return None
        return self._row_to_record(row)

    def list_trades(self, status: str | None = None) -> list[TradeRecord]:
        if status:
            rows = self.conn.execute("SELECT * FROM trades WHERE status = ? ORDER BY timestamp DESC", (status,)).fetchall()
        else:
            rows = self.conn.execute("SELECT * FROM trades ORDER BY timestamp DESC").fetchall()
        return [self._row_to_record(row) for row in rows]

    def stats(self) -> dict[str, Any]:
        rows = self.conn.execute("SELECT * FROM trades WHERE realized_pnl IS NOT NULL").fetchall()
        realized = [row["realized_pnl"] for row in rows if row["realized_pnl"] is not None]
        wins = [p for p in realized if p > 0]
        losses = [p for p in realized if p < 0]
        total = sum(realized)
        avg = sum(realized) / len(realized) if realized else 0.0
        return {
            "trades": len(realized),
            "total_pnl": total,
            "average_pnl": avg,
            "wins": len(wins),
            "losses": len(losses),
            "win_rate": (len(wins) / len(realized) * 100) if realized else 0.0,
        }

    def export(self, path: Path, fmt: str = "csv") -> Path:
        trades = self.list_trades()
        path.parent.mkdir(parents=True, exist_ok=True)
        if fmt == "json":
            with open(path, "w", encoding="utf-8") as fh:
                json.dump([asdict(trade) for trade in trades], fh, ensure_ascii=False, indent=2)
        else:
            with open(path, "w", encoding="utf-8", newline="") as fh:
                writer = csv.writer(fh)
                if trades:
                    writer.writerow(asdict(trades[0]).keys())
                    for trade in trades:
                        writer.writerow(asdict(trade).values())
        return path

    @staticmethod
    def _row_to_record(row: sqlite3.Row) -> TradeRecord:
        return TradeRecord(**{k: row[k] for k in row.keys()})
