#!/usr/bin/env python3
"""Download a Telegram voice file and transcribe it via Wyoming faster-whisper.

Usage: python3 transcribe_telegram_voice.py <file_id>
Reads telegram_api_token from /config/secrets.yaml.
Prints the transcript to stdout, exits 1 on failure.
"""
import asyncio
import json
import os
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request

import yaml

WYOMING_HOST = "localhost"
WYOMING_PORT = 10300


def _get_token() -> str:
    with open("/config/secrets.yaml") as f:
        return yaml.safe_load(f)["telegram_api_token"]


def _get_telegram_file_path(token: str, file_id: str) -> str:
    url = f"https://api.telegram.org/bot{token}/getFile?file_id={urllib.parse.quote(file_id)}"
    with urllib.request.urlopen(url, timeout=10) as r:
        data = json.load(r)
    if not data.get("ok"):
        raise RuntimeError(f"Telegram getFile failed: {data}")
    return data["result"]["file_path"]


def _download(token: str, file_path: str, dest: str) -> None:
    url = f"https://api.telegram.org/file/bot{token}/{file_path}"
    urllib.request.urlretrieve(url, dest)


def _to_pcm(src: str) -> bytes:
    result = subprocess.run(
        ["ffmpeg", "-y", "-i", src, "-f", "s16le", "-ar", "16000", "-ac", "1", "-"],
        capture_output=True,
        timeout=60,
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {result.stderr.decode()[:200]}")
    return result.stdout


async def _transcribe(pcm: bytes) -> str:
    from wyoming.asr import Transcribe, Transcript
    from wyoming.audio import AudioChunk, AudioStart, AudioStop
    from wyoming.client import AsyncTcpClient

    async with AsyncTcpClient(WYOMING_HOST, WYOMING_PORT) as client:
        await client.write_event(Transcribe(language="en").event())
        await client.write_event(AudioStart(rate=16000, width=2, channels=1).event())
        chunk_size = 4096
        for i in range(0, len(pcm), chunk_size):
            await client.write_event(
                AudioChunk(
                    audio=pcm[i : i + chunk_size],
                    rate=16000,
                    width=2,
                    channels=1,
                ).event()
            )
        await client.write_event(AudioStop().event())
        while True:
            event = await client.read_event()
            if event is None:
                break
            if Transcript.is_type(event.type):
                return Transcript.from_event(event).text
    return ""


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: transcribe_telegram_voice.py <file_id>", file=sys.stderr)
        sys.exit(1)

    file_id = sys.argv[1]
    token = _get_token()

    with tempfile.NamedTemporaryFile(suffix=".oga", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        tg_path = _get_telegram_file_path(token, file_id)
        _download(token, tg_path, tmp_path)
        pcm = _to_pcm(tmp_path)
        text = asyncio.run(_transcribe(pcm))
        print(text.strip())
    finally:
        os.unlink(tmp_path)


if __name__ == "__main__":
    main()
