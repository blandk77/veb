import os

# Telegram API credentials
API_ID = int(os.environ.get("API_ID", "27394279"))  # Replace with your API ID
API_HASH = os.environ.get("API_HASH", "90a9aa4c31afa3750da5fd686c410851")  # Replace with your API HASH
BOT_TOKEN = os.environ.get("BOT_TOKEN", "7773651775:AAEH1TN8P5700Ni7fluT9A7uE0xUWuZ0slE")  # Replace with your bot token

# Bot settings
BOT_NAME = "Alsoanencoderobot"

# FFmpeg settings (These are used in the default presets. Adapt to your needs)
DEFAULT_FFMPEG_PRESET_1 = "-c:v libx264 -crf 25 -preset veryfast"
DEFAULT_FFMPEG_PRESET_2 = "-c:v libx265 -crf 30 -preset veryfast"
DEFAULT_FFMPEG_PRESET_3 = "-c:v lib×264 -crf 26 -preset veryfast"
DEFAULT_FFMPEG_PRESET_4 = "-c:v libx264 -crf 28 -preset veryfast"

#  Admin User ID (Optional)
ADMIN_USER_ID = int(os.environ.get("ADMIN_USER_ID", 7465574522)) #  Set to your user ID if you want admin commands
