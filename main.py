import asyncio
import os
import logging

from pyrogram import Client, filters
from pyrogram.types import Message

import config
import database as db
import plugins as plugin_registry
import handlers
import admin

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger(__name__)

os.makedirs(config.TEMP_DIR, exist_ok=True)

app = Client(
    name="mediabot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN,
    in_memory=True,          # no session file on disk — Railway-safe
)


@app.on_message(filters.command("start") & filters.private)
async def cmd_start(client: Client, message: Message):
    authorized, reason = await db.is_authorized(message.from_user.id)
    if not authorized:
        await message.reply(config.MSG_NO_ACCESS)
        return
    await message.reply(
        "👋 **Media Downloader Bot**\n\n"
        "Send me any link to download:\n"
        "• YouTube videos\n"
        "• Instagram posts & stories\n"
        "• TikTok videos\n"
        "• X/Twitter videos\n"
        "• Direct media URLs\n\n"
        "Select quality after sending the link.",
        parse_mode="markdown",
    )


@app.on_message(filters.command("help") & filters.private)
async def cmd_help(client: Client, message: Message):
    authorized, _ = await db.is_authorized(message.from_user.id)
    if not authorized:
        return
    await message.reply(
        "**How to use:**\n"
        "1. Send a link\n"
        "2. Select quality from the buttons\n"
        "3. Wait for upload\n\n"
        "**Commands:**\n"
        "/start — welcome\n"
        "/help — this message\n"
        "/retry\_<job\_id> — retry a failed upload\n\n"
        "**Admin only:**\n"
        "/admin — admin panel\n"
        "/adduser @username\n"
        "/removeuser user\_id\n"
        "/banuser user\_id message\n"
        "/unbanuser user\_id\n"
        "/setlimit user\_id file\_mb daily\_mb queue\n"
        "/broadcast message\n"
        "/setdefault max\_file|daily|queue value",
        parse_mode="markdown",
    )


async def main():
    log.info("Initializing database...")
    await db.init_db()

    log.info("Loading plugins...")
    plugin_registry.load_plugins()
    loaded = [p.PLATFORM_NAME for p in plugin_registry.list_plugins()]
    log.info(f"Plugins loaded: {loaded}")

    log.info("Registering handlers...")
    handlers.register_all(app)
    admin.register_all(app)

    log.info("Starting bot...")
    await app.start()
    me = await app.get_me()
    log.info(f"Bot started: @{me.username}")

    # periodic cache cleanup — runs every hour
    async def cache_cleanup_loop():
        while True:
            await asyncio.sleep(3600)
            await db.cleanup_expired_cache()
            log.info("Expired upload cache cleaned.")

    asyncio.create_task(cache_cleanup_loop())

    await asyncio.Event().wait()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
