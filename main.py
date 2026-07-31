import asyncio
import os
import logging

import uvicorn
from pyrogram import Client, filters
from pyrogram.types import Message

import config
import database as db
import plugins as plugin_registry
import handlers
import admin
from logger import setup_logging
from web.server import app as web_app

setup_logging()
log = logging.getLogger(__name__)

os.makedirs(config.TEMP_DIR, exist_ok=True)

bot = Client(
    name="mediabot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN,
    in_memory=True,
)


@bot.on_message(filters.command("start") & filters.private)
async def cmd_start(client: Client, message: Message):
    if await db.is_bot_paused():
        await message.reply("🔴 Bot is currently paused. Try again later.")
        return
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


@bot.on_message(filters.command("help") & filters.private)
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
        "/retry_<job_id> — retry a failed upload",
        parse_mode="markdown",
    )


async def run_bot():
    log.info("Initializing database...")
    await db.init_db()

    log.info("Loading plugins...")
    plugin_registry.load_plugins()
    loaded = [p.PLATFORM_NAME for p in plugin_registry.list_plugins()]
    log.info(f"Plugins loaded: {loaded}")

    log.info("Registering handlers...")
    handlers.register_all(bot)
    admin.register_all(bot)

    log.info("Starting bot...")
    await bot.start()
    me = await bot.get_me()
    log.info(f"Bot started: @{me.username}")

    async def cache_cleanup_loop():
        while True:
            await asyncio.sleep(3600)
            await db.cleanup_expired_cache()
            log.info("Expired upload cache cleaned.")

    asyncio.create_task(cache_cleanup_loop())
    await asyncio.Event().wait()


async def run_web():
    port = int(os.environ.get("PORT", "8080"))
    log.info(f"Starting web panel on port {port}...")
    config_uvicorn = uvicorn.Config(
        web_app,
        host="0.0.0.0",
        port=port,
        log_level="warning",
    )
    server = uvicorn.Server(config_uvicorn)
    await server.serve()


async def main():
    await asyncio.gather(run_bot(), run_web())


if __name__ == "__main__":
    asyncio.run(main())
