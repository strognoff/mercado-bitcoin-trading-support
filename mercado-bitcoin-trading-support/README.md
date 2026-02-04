# Mercado Bitcoin Manual Trading Support

A minimal CLI to help you make manual trades on Mercado Bitcoin while keeping every decision communicated, confirmed, and recorded. Features:

- Typer-based CLI for registering trade plans, confirming execution, and closing positions.
- Telegram notifications before each trade (via `openclaw message send`).
- SQLite ledger for decisions, entry/exit prices, reasoning, and realized P&L.
- Simple stats (`win/loss`, cumulative P&L, average return) and export commands.
- Paper-trade mode for rehearsals.

## Getting started

1. `cd repos/mercado-bitcoin-trading-support`
2. Copy `config/config.example.json` to `config/config.json` and fill in your Mercado Bitcoin API key/secret plus any overrides.
3. Install dependencies: `pip install -e .`
4. Use `trading-support` commands (see below).

## Commands

```bash
trading-support plan              # register a trade plan, send summary, confirm execution
trading-support settle            # record an exit price and compute realized P&L
trading-support stats             # show cumulative P&L + performance metrics
trading-support export --format csv  # export the ledger to CSV or JSON
``` 

Every `plan` command sends a summary to Telegram (via the OpenClaw CLI) before asking for confirmation. Only after you confirm does the CLI optionally place an order against Mercado Bitcoin (unless `--paper` is used).

## Configuration

- Keep secrets out of the repo. The template in `config/config.example.json` documents the fields:
  - `base_url`: `https://api.mercadobitcoin.net/api/v4`
  - `api_key`, `api_secret`
  - `auth_headers`: allow you to define header names for the key/signature/timestamp so you can match Mercado Bitcoin’s requirements.
  - `paper_trade`: default `true` for prototyping.

## Data

Trade history persists to `data/trades.db`. Add `data/` to `.gitignore` so it never gets checked in.

## Workflow

1. Run `trading-support plan` and describe the trade you are about to take.
2. The CLI composes a summary (asset, direction, reasoning, entry/exit plan), sends it to you via Telegram, then asks for confirmation.
3. After you confirm, the CLI either executes a real `POST /orders` (when `paper_trade` is `false`) or records the plan in paper mode.
4. Later, run `trading-support settle <trade-id> --exit-price ...` to capture the exit price and update P&L.
5. Use `trading-support stats` to review your performance or `export` to build a CSV backlog.
