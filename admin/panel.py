from pyrogram import Client, filters
from pyrogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
)

import config
import database as db


def register(app: Client):

    # ─── /admin command ───────────────────────────────────────────────────────

    @app.on_message(filters.command("admin") & filters.private)
    async def admin_entry(client: Client, message: Message):
        if message.from_user.id != config.ADMIN_ID:
            return
        await message.reply("⚙️ **Admin Panel**", reply_markup=_main_menu())

    # ─── Main menu ────────────────────────────────────────────────────────────

    @app.on_callback_query(filters.regex(r"^adm:main$"))
    async def cb_main(client: Client, cb: CallbackQuery):
        if cb.from_user.id != config.ADMIN_ID:
            return await cb.answer()
        await cb.message.edit_text("⚙️ **Admin Panel**", reply_markup=_main_menu())
        await cb.answer()

    # ─── Users submenu ────────────────────────────────────────────────────────

    @app.on_callback_query(filters.regex(r"^adm:users$"))
    async def cb_users(client: Client, cb: CallbackQuery):
        if cb.from_user.id != config.ADMIN_ID:
            return await cb.answer()
        users = await db.list_users()
        lines = []
        for u in users:
            status = "🚫" if u["is_banned"] else ("✅" if u["is_active"] else "❌")
            name = u["username"] or u["display_name"] or str(u["telegram_id"])
            lines.append(f"{status} {name} (`{u['telegram_id']}`)")
        text = "👥 **Users**\n\n" + ("\n".join(lines) if lines else "_No users yet._")
        await cb.message.edit_text(text, reply_markup=_users_menu(), parse_mode="markdown")
        await cb.answer()

    @app.on_callback_query(filters.regex(r"^adm:user_add$"))
    async def cb_user_add(client: Client, cb: CallbackQuery):
        if cb.from_user.id != config.ADMIN_ID:
            return await cb.answer()
        await cb.message.edit_text(
            "➕ Send user's **Telegram ID** (numeric) or **@username**:\n\n"
            "_Reply to this message with the ID/username._",
            reply_markup=_back("adm:users"),
            parse_mode="markdown",
        )
        await cb.answer()
        # conversation state tracked via next message handler below

    @app.on_callback_query(filters.regex(r"^adm:user_remove$"))
    async def cb_user_remove(client: Client, cb: CallbackQuery):
        if cb.from_user.id != config.ADMIN_ID:
            return await cb.answer()
        await cb.message.edit_text(
            "➖ Send user's **Telegram ID** to remove:\n\n_Reply to this message._",
            reply_markup=_back("adm:users"),
            parse_mode="markdown",
        )
        await cb.answer()

    @app.on_callback_query(filters.regex(r"^adm:user_ban$"))
    async def cb_user_ban(client: Client, cb: CallbackQuery):
        if cb.from_user.id != config.ADMIN_ID:
            return await cb.answer()
        await cb.message.edit_text(
            "🚫 Send: `<user_id> <ban message>`\n\nExample: `123456789 You have been suspended.`\n\n"
            "_Reply to this message._",
            reply_markup=_back("adm:users"),
            parse_mode="markdown",
        )
        await cb.answer()

    @app.on_callback_query(filters.regex(r"^adm:user_unban$"))
    async def cb_user_unban(client: Client, cb: CallbackQuery):
        if cb.from_user.id != config.ADMIN_ID:
            return await cb.answer()
        await cb.message.edit_text(
            "✅ Send user's **Telegram ID** to unban:\n\n_Reply to this message._",
            reply_markup=_back("adm:users"),
            parse_mode="markdown",
        )
        await cb.answer()

    @app.on_callback_query(filters.regex(r"^adm:user_limits$"))
    async def cb_user_limits(client: Client, cb: CallbackQuery):
        if cb.from_user.id != config.ADMIN_ID:
            return await cb.answer()
        await cb.message.edit_text(
            "📊 Send: `<user_id> <max_file_mb> <daily_limit_mb> <queue_limit>`\n\n"
            "Example: `123456789 1024 5120 5`\n"
            "Use `0` for any value to reset to default.\n\n"
            "_Reply to this message._",
            reply_markup=_back("adm:users"),
            parse_mode="markdown",
        )
        await cb.answer()

    # ─── Stats submenu ────────────────────────────────────────────────────────

    @app.on_callback_query(filters.regex(r"^adm:stats$"))
    async def cb_stats(client: Client, cb: CallbackQuery):
        if cb.from_user.id != config.ADMIN_ID:
            return await cb.answer()
        stats = await db.get_stats()
        platforms = "\n".join(
            f"  • {p}: {c}" for p, c in stats["platforms"].items()
        ) or "  _None yet_"
        text = (
            f"📊 **Bot Statistics**\n\n"
            f"👥 Active users: `{stats['total_users']}`\n"
            f"✅ Total downloads: `{stats['total_downloads']}`\n"
            f"❌ Failed: `{stats['failed']}`\n"
            f"📅 Today: `{stats['today_downloads']}`\n"
            f"💾 Total volume: `{stats['total_volume_gb']} GB`\n\n"
            f"**By platform:**\n{platforms}"
        )
        await cb.message.edit_text(text, reply_markup=_back("adm:main"), parse_mode="markdown")
        await cb.answer()

    # ─── Platform toggles ─────────────────────────────────────────────────────

    @app.on_callback_query(filters.regex(r"^adm:platforms$"))
    async def cb_platforms(client: Client, cb: CallbackQuery):
        if cb.from_user.id != config.ADMIN_ID:
            return await cb.answer()
        settings = await db.get_platform_settings()
        await cb.message.edit_text(
            "🌐 **Platform Settings**\nToggle platforms on/off:",
            reply_markup=_platforms_menu(settings),
            parse_mode="markdown",
        )
        await cb.answer()

    @app.on_callback_query(filters.regex(r"^adm:toggle:(.+)$"))
    async def cb_toggle_platform(client: Client, cb: CallbackQuery):
        if cb.from_user.id != config.ADMIN_ID:
            return await cb.answer()
        platform = cb.data.split(":", 2)[2]
        settings = await db.get_platform_settings()
        current = settings.get(platform, True)
        await db.toggle_platform(platform, not current)
        settings[platform] = not current
        await cb.message.edit_text(
            "🌐 **Platform Settings**\nToggle platforms on/off:",
            reply_markup=_platforms_menu(settings),
            parse_mode="markdown",
        )
        await cb.answer(f"{'✅ Enabled' if not current else '❌ Disabled'}: {platform}")

    # ─── Default settings ─────────────────────────────────────────────────────

    @app.on_callback_query(filters.regex(r"^adm:settings$"))
    async def cb_settings(client: Client, cb: CallbackQuery):
        if cb.from_user.id != config.ADMIN_ID:
            return await cb.answer()
        max_file = await db.get_bot_setting("default_max_file_mb")
        daily = await db.get_bot_setting("default_daily_limit_mb")
        queue = await db.get_bot_setting("default_queue_limit")
        text = (
            f"⚙️ **Default Settings**\n\n"
            f"📁 Max file size: `{max_file} MB`\n"
            f"📅 Daily limit: `{daily} MB`\n"
            f"📋 Queue limit: `{queue}` jobs\n\n"
            "_Send a command to change:_\n"
            "`/setdefault max_file <MB>`\n"
            "`/setdefault daily <MB>`\n"
            "`/setdefault queue <N>`"
        )
        await cb.message.edit_text(text, reply_markup=_back("adm:main"), parse_mode="markdown")
        await cb.answer()

    # ─── Broadcast ────────────────────────────────────────────────────────────

    @app.on_callback_query(filters.regex(r"^adm:broadcast$"))
    async def cb_broadcast(client: Client, cb: CallbackQuery):
        if cb.from_user.id != config.ADMIN_ID:
            return await cb.answer()
        await cb.message.edit_text(
            "📢 **Broadcast**\n\nSend your message text as a reply to this message.\n"
            "_It will be sent to all active users._",
            reply_markup=_back("adm:main"),
            parse_mode="markdown",
        )
        await cb.answer()

    # ─── Text command handlers for admin actions ───────────────────────────────

    @app.on_message(filters.command("setdefault") & filters.private)
    async def set_default(client: Client, message: Message):
        if message.from_user.id != config.ADMIN_ID:
            return
        parts = message.text.split()
        if len(parts) != 3:
            await message.reply("Usage: `/setdefault max_file|daily|queue <value>`", parse_mode="markdown")
            return
        _, key, value = parts
        key_map = {
            "max_file": "default_max_file_mb",
            "daily": "default_daily_limit_mb",
            "queue": "default_queue_limit",
        }
        if key not in key_map:
            await message.reply("Unknown key. Use: max_file | daily | queue")
            return
        await db.set_bot_setting(key_map[key], value)
        await message.reply(f"✅ `{key}` set to `{value}`", parse_mode="markdown")


# ─── Keyboard builders ────────────────────────────────────────────────────────

def _main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("👥 Users",     callback_data="adm:users"),
            InlineKeyboardButton("📊 Stats",     callback_data="adm:stats"),
        ],
        [
            InlineKeyboardButton("🌐 Platforms", callback_data="adm:platforms"),
            InlineKeyboardButton("⚙️ Settings",  callback_data="adm:settings"),
        ],
        [
            InlineKeyboardButton("📢 Broadcast", callback_data="adm:broadcast"),
        ],
    ])


def _users_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➕ Add",       callback_data="adm:user_add"),
            InlineKeyboardButton("➖ Remove",    callback_data="adm:user_remove"),
        ],
        [
            InlineKeyboardButton("🚫 Ban",       callback_data="adm:user_ban"),
            InlineKeyboardButton("✅ Unban",     callback_data="adm:user_unban"),
        ],
        [
            InlineKeyboardButton("📊 Set Limits", callback_data="adm:user_limits"),
        ],
        [InlineKeyboardButton("⬅️ Back", callback_data="adm:main")],
    ])


def _platforms_menu(settings: dict) -> InlineKeyboardMarkup:
    buttons = []
    for platform, enabled in settings.items():
        label = f"{'✅' if enabled else '❌'} {platform.title()}"
        buttons.append([InlineKeyboardButton(label, callback_data=f"adm:toggle:{platform}")])
    buttons.append([InlineKeyboardButton("⬅️ Back", callback_data="adm:main")])
    return InlineKeyboardMarkup(buttons)


def _back(target: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data=target)]])
