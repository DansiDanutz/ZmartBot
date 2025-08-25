"""
Telegram Image Watcher for personal account (MTProto via Telethon)
- Watches one or more chats/channels (e.g., @thekingfisher_liqmap_bot or its channel)
- Auto-downloads images/photos
- Optionally POSTs each image to an analysis endpoint (e.g., your n8n webhook or model API)
"""
import os
import asyncio
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from telethon import TelegramClient, events
from telethon.tl.types import Message
from dotenv import load_dotenv
import requests

load_dotenv()

API_ID = int(os.getenv("TELEGRAM_API_ID", "0"))
API_HASH = os.getenv("TELEGRAM_API_HASH", "")
WATCH_CHATS_RAW = os.getenv("WATCH_CHATS", "")
DOWNLOAD_DIR = Path(os.getenv("DOWNLOAD_DIR", "downloads"))
ANALYSIS_URL = os.getenv("ANALYSIS_URL", "")  # optional
ANALYSIS_TOKEN = os.getenv("ANALYSIS_TOKEN", "")  # optional
BACKFILL_LIMIT = int(os.getenv("BACKFILL_LIMIT", "0"))

if not API_ID or not API_HASH:
    raise SystemExit("Missing TELEGRAM_API_ID or TELEGRAM_API_HASH. Set them in environment or .env.")

WATCH_CHATS: List[str] = [c.strip() for c in WATCH_CHATS_RAW.split(",") if c.strip()]
if not WATCH_CHATS:
    print("WARNING: WATCH_CHATS is empty. You can still run and then type the chat at the prompt, or set WATCH_CHATS in .env.")

DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

SESSION_NAME = "me"  # Telethon session file name (me.session)
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

def is_image_message(msg: Message) -> bool:
    if msg.photo:
        return True
    if msg.document and msg.document.mime_type:
        mt = msg.document.mime_type.lower()
        return any(mt.startswith(mt2) for mt2 in ["image/jpeg", "image/png", "image/webp", "image/jpg", "image/gif"])
    return False

def safe_chat_dir(title_or_id: str) -> Path:
    safe = "".join(c if c.isalnum() or c in ("-", "_", "@") else "_" for c in title_or_id)
    return DOWNLOAD_DIR / safe

def analyze_image(filepath: Path, chat_id: int, message_id: int) -> Optional[dict]:
    if not ANALYSIS_URL:
        return None
    headers = {}
    if ANALYSIS_TOKEN:
        headers["Authorization"] = f"Bearer {ANALYSIS_TOKEN}"
    try:
        with open(filepath, "rb") as f:
            files = {"file": (filepath.name, f, "application/octet-stream")}
            data = {"chat_id": str(chat_id), "message_id": str(message_id), "timestamp": datetime.utcnow().isoformat()}
            r = requests.post(ANALYSIS_URL, headers=headers, files=files, data=data, timeout=60)
            r.raise_for_status()
            try:
                return r.json()
            except Exception:
                return {"status": "ok", "raw": r.text[:500]}
    except Exception as e:
        print(f"[ANALYZE][ERROR] {filepath}: {e}")
        return None

async def download_and_analyze(event_msg: Message):
    chat = await event_msg.get_chat()
    chat_label = getattr(chat, "username", None) or getattr(chat, "title", None) or str(getattr(chat, "id", "unknown"))
    chat_dir = safe_chat_dir(str(chat_label))
    chat_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.fromtimestamp(event_msg.date.timestamp())
    ts_str = ts.strftime("%Y%m%d_%H%M%S")
    base = f"{ts_str}_msg{event_msg.id}"

    try:
        filepath = await event_msg.download_media(file=str(chat_dir / base))
        if filepath:
            print(f"[DOWNLOADED] {filepath}")
            result = analyze_image(Path(filepath), chat.id, event_msg.id)
            if result is not None:
                print(f"[ANALYSIS] {result}")
    except Exception as e:
        print(f"[DOWNLOAD][ERROR] msg {event_msg.id}: {e}")

@client.on(events.NewMessage())
async def handler(event):
    msg = event.message
    if not is_image_message(msg):
        return
    if WATCH_CHATS:
        try:
            chat = await event.get_chat()
            uname = getattr(chat, "username", None)
            cid = getattr(chat, "id", None)
            title = getattr(chat, "title", None)
            labels = set([
                str(cid) if cid is not None else "",
                f"-100{abs(cid)}" if isinstance(cid, int) and cid < 0 else "",
                uname.lower() if uname else "",
                (title or "").lower(),
            ])
            match = any(
                watch.lower().lstrip("@") in labels or (uname and watch.lower().lstrip("@") == uname.lower())
                for watch in WATCH_CHATS
            ) or any(str(watch) == str(cid) for watch in WATCH_CHATS)
            if not match:
                return
        except Exception as e:
            print(f"[FILTER][WARN] Could not resolve chat for msg {msg.id}: {e}")
            return
    await download_and_analyze(msg)

async def backfill():
    if BACKFILL_LIMIT <= 0 or not WATCH_CHATS:
        return
    print(f"[BACKFILL] Fetching last {BACKFILL_LIMIT} messages for: {WATCH_CHATS}")
    for target in WATCH_CHATS:
        try:
            async for m in client.iter_messages(entity=target, limit=BACKFILL_LIMIT):
                if is_image_message(m):
                    await download_and_analyze(m)
        except Exception as e:
            print(f"[BACKFILL][ERROR] {target}: {e}")

async def main():
    await client.start()
    if BACKFILL_LIMIT > 0:
        await backfill()
    print("Watcher running. Press Ctrl+C to stop.")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
