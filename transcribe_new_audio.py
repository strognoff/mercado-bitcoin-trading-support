#!/usr/bin/env python3
import json
import os
import subprocess
from pathlib import Path

HOME = Path(os.path.expanduser("~"))
WORKSPACE = HOME / ".openclaw" / "workspace"
INBOUND = HOME / ".openclaw" / "media" / "inbound"
STATE_PATH = WORKSPACE / "data" / "transcribed_audio.json"
STT_REPO = WORKSPACE / "repos" / "openclaw-local-stt"
STT_PY = STT_REPO / ".venv" / "bin" / "python"
STT_SCRIPT = STT_REPO / "transcribe_local_whisper.py"


def load_state():
    if STATE_PATH.exists():
        try:
            data = json.loads(STATE_PATH.read_text())
            return set(data.get("files", []))
        except Exception:
            return set()
    return set()


def save_state(files):
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps({"files": sorted(files)}, indent=2))


def run_transcribe(path: Path):
    if not STT_PY.exists():
        return None, f"STT venv not found at {STT_PY}"
    try:
        res = subprocess.run(
            [str(STT_PY), str(STT_SCRIPT), str(path)],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if res.returncode != 0:
            return None, res.stderr.strip() or res.stdout.strip() or "unknown error"
        data = json.loads(res.stdout.strip())
        if data.get("success"):
            return data.get("text", "").strip(), None
        return None, data.get("error") or "transcription failed"
    except Exception as e:
        return None, str(e)


def main():
    if not INBOUND.exists():
        return

    processed = load_state()
    new_lines = []

    files = sorted(INBOUND.glob("*.ogg"), key=lambda p: p.stat().st_mtime)
    for f in files:
        if f.name in processed:
            continue
        text, err = run_transcribe(f)
        if text:
            new_lines.append(f"🎙️ Transcript ({f.name}): {text}")
            processed.add(f.name)
        else:
            # leave unprocessed for retry if it fails
            if err:
                new_lines.append(f"⚠️ STT failed for {f.name}: {err}")

    if new_lines:
        print("\n".join(new_lines))

    save_state(processed)


if __name__ == "__main__":
    main()
