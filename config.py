import os
from dotenv import load_dotenv

load_dotenv()

# --- Telegram ---
API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
BOT_TOKEN = os.environ["BOT_TOKEN"]
ADMIN_ID = int(os.environ["ADMIN_ID"])  # your telegram numeric ID

# --- Database ---
DATABASE_URL = os.environ["DATABASE_URL"]  # set by Railway PostgreSQL addon

# --- Download limits (overridable per-user in DB) ---
DEFAULT_MAX_FILE_SIZE_MB = int(os.getenv("DEFAULT_MAX_FILE_SIZE_MB", "500"))
DEFAULT_DAILY_LIMIT_MB = int(os.getenv("DEFAULT_DAILY_LIMIT_MB", "2048"))
DEFAULT_QUEUE_LIMIT = int(os.getenv("DEFAULT_QUEUE_LIMIT", "3"))

# --- Queue ---
MAX_CONCURRENT_DOWNLOADS = int(os.getenv("MAX_CONCURRENT_DOWNLOADS", "3"))

# --- Retry / Cache ---
UPLOAD_MAX_RETRIES = 3
UPLOAD_RETRY_DELAY = 5  # seconds between retries
CACHE_TTL_HOURS = 24    # how long to keep failed-upload cache entries

# --- Temp storage ---
TEMP_DIR = "/tmp/mediabot"

# --- Platforms enabled by default ---
DEFAULT_PLATFORMS = {
    "youtube": True,
    "instagram": True,
    "twitter": True,
    "tiktok": True,
    "direct_url": True,
}

# --- Bot messages ---
MSG_NO_ACCESS = "⛔ You don't have access to this bot."
MSG_BANNED = "🚫 Your access has been suspended."
MSG_QUEUE_FULL = "⏳ Your download queue is full ({limit} max). Wait for current downloads to finish."
MSG_FILE_TOO_LARGE = "❌ File exceeds your size limit ({size}MB / {limit}MB)."
MSG_DAILY_LIMIT = "📊 You've reached your daily download limit ({used}MB / {limit}MB)."
MSG_PLATFORM_DISABLED = "❌ This platform is currently disabled."
MSG_DOWNLOAD_START = "⬇️ Download started..."
MSG_UPLOAD_START = "📤 Uploading to Telegram..."
MSG_DONE = "✅ Done!"
MSG_FAILED = "❌ Download failed. Please try again."
MSG_RETRY = "🔄 Upload failed. Retrying ({attempt}/{max})..."
MSG_UPLOAD_FAILED_CACHE = "❌ Upload failed after {max} retries. Your file is cached — send /retry_{job_id} to try again."
