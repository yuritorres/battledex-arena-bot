import html
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional
from xml.etree import ElementTree as ET

import aiohttp

logger = logging.getLogger(__name__)

ATOM_NS = "{http://www.w3.org/2005/Atom}"
YT_NS = "{http://www.youtube.com/xml/schemas/2015}"
FEED_TEMPLATE = "https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"


def _parse_int(value: Optional[str]) -> Optional[int]:
    if not value:
        return None
    cleaned = value.strip()
    if cleaned and cleaned.lstrip("-").isdigit():
        return int(cleaned)
    return None


def _load_state(path: str) -> Dict[str, str]:
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        logger.warning("YouTube notifier: falha ao ler estado em %s", path)
        return {}


def _save_state(path: str, data: Dict[str, str]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)


async def _fetch_feed_entries(feed_url: str) -> List[Dict[str, Optional[str]]]:
    timeout = aiohttp.ClientTimeout(total=20)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(feed_url) as response:
            if response.status != 200:
                raise RuntimeError(f"HTTP {response.status} ao buscar feed YouTube")
            body = await response.text()
    root = ET.fromstring(body)
    entries: List[Dict[str, Optional[str]]] = []
    for entry in root.findall(f"{ATOM_NS}entry"):
        video_id = entry.findtext(f"{YT_NS}videoId")
        title = (entry.findtext(f"{ATOM_NS}title") or "Novo vídeo").strip()
        published_raw = entry.findtext(f"{ATOM_NS}published") or ""
        link = f"https://www.youtube.com/watch?v={video_id}" if video_id else None
        if not video_id or not link:
            continue
        entries.append(
            {
                "id": video_id,
                "title": title,
                "link": link,
                "published": _format_published(published_raw),
            }
        )
    return entries


def _format_published(raw: str) -> Optional[str]:
    if not raw:
        return None
    try:
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        return dt.strftime("%d/%m/%Y %H:%M")
    except Exception:
        return raw


async def _announce_video(context, chat_id: int, topic_id: Optional[int], entry: Dict[str, Optional[str]]):
    published = f"\n🕒 Publicado em: {entry['published']}" if entry.get("published") else ""
    text = (
        "🎬 Novo vídeo no YouTube!\n"
        f"<b>{html.escape(entry['title'] or 'Novo vídeo')}</b>\n"
        f"{entry['link']}{published}"
    )
    try:
        await context.bot.send_message(
            chat_id=chat_id,
            message_thread_id=topic_id,
            text=text,
            parse_mode="HTML",
            disable_web_page_preview=False,
        )
    except Exception as exc:
        logger.warning("YouTube notifier: falha ao anunciar vídeo %s: %s", entry.get("id"), exc)


async def _handle_poll(feed_url: str, state_path: str, chat_id: int, topic_id: Optional[int], context):
    entries = await _fetch_feed_entries(feed_url)
    if not entries:
        return
    state = _load_state(state_path)
    last_seen = state.get("last_video_id")
    newest_id = entries[0]["id"]
    if not last_seen:
        state["last_video_id"] = newest_id
        _save_state(state_path, state)
        logger.info("YouTube notifier iniciado com vídeo %s (sem envio retroativo)", newest_id)
        return

    new_entries: List[Dict[str, Optional[str]]] = []
    for entry in entries:
        if entry["id"] == last_seen:
            break
        new_entries.append(entry)

    if not new_entries:
        return

    for entry in reversed(new_entries):
        await _announce_video(context, chat_id, topic_id, entry)

    state["last_video_id"] = newest_id
    _save_state(state_path, state)


def register_youtube_notifier(app, storage_dir: str, fallback_chat_id: Optional[int] = None, fallback_topic_id: Optional[int] = None) -> None:
    channel_id = os.getenv("YOUTUBE_CHANNEL_ID")
    if not channel_id:
        logger.info("YouTube notifier desabilitado: defina YOUTUBE_CHANNEL_ID no .env")
        return

    target_chat_id = _parse_int(os.getenv("YOUTUBE_NOTIFY_CHAT_ID")) or fallback_chat_id
    if not target_chat_id:
        logger.info(
            "YouTube notifier desabilitado: defina YOUTUBE_NOTIFY_CHAT_ID ou BROADCAST_CHAT_ID no .env"
        )
        return

    target_topic_id = _parse_int(os.getenv("YOUTUBE_NOTIFY_TOPIC_ID")) or fallback_topic_id
    poll_seconds = max(60, _parse_int(os.getenv("YOUTUBE_POLL_INTERVAL_SECONDS")) or 300)

    feed_url = FEED_TEMPLATE.format(channel_id=channel_id)
    state_path = os.path.join(storage_dir, "youtube_state.json")

    async def poll_job(context):
        await _handle_poll(feed_url, state_path, target_chat_id, target_topic_id, context)

    logger.info(
        "YouTube notifier habilitado: canal=%s chat=%s tópico=%s intervalo=%ss",
        channel_id,
        target_chat_id,
        target_topic_id,
        poll_seconds,
    )

    app.job_queue.run_repeating(
        poll_job,
        interval=poll_seconds,
        first=15,
        name="youtube_video_notifier",
    )


async def send_latest_video_now(
    bot,
    storage_dir: str,
    chat_id: Optional[int] = None,
    topic_id: Optional[int] = None,
    fallback_chat_id: Optional[int] = None,
    fallback_topic_id: Optional[int] = None,
):
    channel_id = os.getenv("YOUTUBE_CHANNEL_ID")
    if not channel_id:
        raise RuntimeError("YouTube notifier desabilitado: YOUTUBE_CHANNEL_ID não configurado")

    target_chat_id = chat_id or _parse_int(os.getenv("YOUTUBE_NOTIFY_CHAT_ID")) or fallback_chat_id
    if not target_chat_id:
        raise RuntimeError(
            "YouTube notifier desabilitado: configure YOUTUBE_NOTIFY_CHAT_ID ou BROADCAST_CHAT_ID"
        )

    target_topic_id = topic_id or _parse_int(os.getenv("YOUTUBE_NOTIFY_TOPIC_ID")) or fallback_topic_id

    feed_url = FEED_TEMPLATE.format(channel_id=channel_id)
    entries = await _fetch_feed_entries(feed_url)
    if not entries:
        raise RuntimeError("Feed do YouTube sem vídeos disponíveis")

    entry = entries[0]

    class _Ctx:
        def __init__(self, bot):
            self.bot = bot

    await _announce_video(_Ctx(bot), target_chat_id, target_topic_id, entry)

    state_path = os.path.join(storage_dir, "youtube_state.json")
    state = _load_state(state_path)
    state["last_video_id"] = entry["id"]
    _save_state(state_path, state)

    return entry
