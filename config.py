import os

# Telegram API credentials
API_ID = int(os.environ.get("API_ID", "YOUR_API_ID"))  # Replace with your API ID
API_HASH = os.environ.get("API_HASH", "YOUR_API_HASH")  # Replace with your API HASH
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN")  # Replace with your bot token

# Bot settings
BOT_NAME = "VideoEncoderBot"

# FFmpeg settings (These are used in the default presets. Adapt to your needs)
DEFAULT_FFMPEG_PRESET_1 = "-c:v libx264 -crf 23"
DEFAULT_FFMPEG_PRESET_2 = "-c:v libx265 -crf 28"
DEFAULT_FFMPEG_PRESET_3 = "-c:v lib×264 -crf 30"
DEFAULT_FFMPEG_PRESET_4 = "-c:v libx264 -preset veryfast"

#  Admin User ID (Optional)
ADMIN_USER_ID = int(os.environ.get("ADMIN_USER_ID", 0)) #  Set to your user ID if you want admin commands
