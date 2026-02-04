from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

import typer
from rich.console import Console
from rich.table import Table

from trading_support.client import MercadoBitcoinClient
from trading_support.config import load_config
from trading_support.ledger import Ledger, TradeRecord
from trading_support.messaging import send_telegram_message

app = typer.Typer()
console = Console()


def _format_summary(
    asset: str,
    direction: str,
    size: float,
    entry_price: float,
    exit_logic: str,
    reasoning: str,
    extra: str | None = None,
) -> str:
    parts = [
        f"[{datetime.now(timezone.utc).isoformat()}] Manual trade plan",
        f"Asset: {asset} / Direction: {direction.upper()}",
        f"Size: {size} • Entry price: {entry_price}",
        f"Reasoning: {reasoning}",
        f"Exit logic: {exit_logic}",
    ]
    if extra:
        parts.append(f"Notes: {extra}")
    return "\n".join(parts)


def _display_trade(trade: Ledger, trade_id: str) -> None:
    record = trade.get_trade(trade_id)
    if not record:
        console.print("[yellow]Trade not found[/yellow]")
        raise typer.Exit(1)
    table = Table(show_header=True, header_style="bold cyan")
    for field, value in record.__dict__.items():
        table.add_column(field, overflow="fold")
    table.add_row(*[str(value or "") for value in record.__dict__.values()])
    console.print(table)


@app.command()
def plan(
    asset: str = typer.Option(..., prompt=True, help="Trading symbol (ex: BTCBRL)"),
    direction: Literal["buy", "sell"] = typer.Option(
        ..., prompt=True, help="Direction of the trade"
    ),
    size: float = typer.Option(..., prompt=True, help="Position size in asset units"),
    entry_price: float = typer.Option(..., prompt=True, help="Target entry price"),
    exit_logic: str = typer.Option(..., prompt="Exit plan", help="Planned exit logic"),
    reasoning: str = typer.Option(..., prompt=True, help="Narrative for the decision"),
    order_type: str = typer.Option("limit", help="Order type (limit/market)"),
    note: str | None = typer.Option(None, help="Extra context for the telegram note"),
    paper: bool | None = typer.Option(None, help="Force paper trade irrespective of config"),
) -> None:
    config = load_config()
    ledger = Ledger()
    summary = _format_summary(asset, direction, size, entry_price, exit_logic, reasoning, note)
    console.print("Sending the pre-trade brief to Telegram...")
    try:
        send_telegram_message(summary, config.telegram_target)
    except RuntimeError as exc:
        console.print(f"[red]Failed to send Telegram message:[/red] {exc}")
        raise typer.Exit(1)

    trade_id = ledger.create_trade(
        asset=asset,
        side=direction,
        entry_price=entry_price,
        size=size,
        reasoning=reasoning,
        exit_logic=exit_logic,
        summary=summary,
    )
    console.print(f"Pre-trade briefing recorded (trade id: {trade_id}).")

    if not typer.confirm("Execute trade now?"):
        console.print("Trade left pending. You can execute later with `settle`.")
        typer.exit()

    use_paper = config.paper_trade if paper is None else paper
    if use_paper:
        ledger.mark_executed(trade_id, entry_price)
        console.print("[green]Paper trade recorded.[/green]")
        _display_trade(ledger, trade_id)
        return

    client = MercadoBitcoinClient(config)
    console.print("Placing order via Mercado Bitcoin API...")
    response = client.place_order(asset, direction, size, entry_price, order_type)
    executed_price = float(response.get("price") or entry_price)
    ledger.mark_executed(trade_id, executed_price, order_id=response.get("id"))
    console.print("[green]Trade executed.[/green]")
    _display_trade(ledger, trade_id)


@app.command()
def settle(trade_id: str, exit_price: float = typer.Option(..., prompt=True), note: str | None = typer.Option(None)) -> None:
    ledger = Ledger()
    trade = ledger.settle_trade(trade_id, exit_price, note)
    console.print(f"Trade {trade_id} closed with realized P&L: {trade.realized_pnl:.6f}")


@app.command()
def stats() -> None:
    ledger = Ledger()
    summary = ledger.stats()
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Metric")
    table.add_column("Value")
    for key, value in summary.items():
        table.add_row(key, f"{value:.2f}" if isinstance(value, float) else str(value))
    console.print(table)


@app.command()
def pending() -> None:
    ledger = Ledger()
    trades = ledger.list_trades(status="pending")
    if not trades:
        console.print("No pending trades.")
        return
    table = Table(show_header=True, header_style="bold blue")
    headers = TradeRecord.__dataclass_fields__.keys()  # type: ignore[attr-defined]
    for header in headers:
        table.add_column(header)
    for trade in trades:
        table.add_row(*[str(getattr(trade, h) or "") for h in headers])
    console.print(table)


@app.command()
def export(path: Path = typer.Option(Path("data/trades_export.csv"), help="Export destination"), fmt: Literal["csv", "json"] = "csv") -> None:
    ledger = Ledger()
    out = ledger.export(path, fmt)
    console.print(f"Exported trade history to {out}")
