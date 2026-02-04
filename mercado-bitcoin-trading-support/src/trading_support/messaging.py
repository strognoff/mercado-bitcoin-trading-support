from __future__ import annotations

import subprocess


def send_telegram_message(message: str, target: str, channel: str = "telegram") -> None:
    cmd = [
        "openclaw",
        "message",
        "send",
        "--channel",
        channel,
        "--target",
        target,
        "--message",
        message,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            "Failed to send Telegram preview message:\n" + result.stderr.strip()
        )
