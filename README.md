# Video Encoder Bot

This is a Telegram bot that allows users to encode videos using FFmpeg presets.

## Setup

1.  **Create a Koyeb account** and deploy a basic web app.

2.  **Set Environment Variables:**  Create the following environment variables in your Koyeb environment:

    •   `API_ID`: Your Telegram API ID.
    •   `API_HASH`: Your Telegram API Hash.
    •   `BOT_TOKEN`: Your Telegram Bot Token.
    •   `ADMIN_USER_ID`: (Optional) Your Telegram user ID if you want admin commands.

3.  **Upload Files:** Upload the `bot.py`, `config.py`, `requirements.txt`, and `plugins/` directory to your Koyeb app.

4.  **Install Dependencies:**  Make sure Koyeb installs the dependencies listed in `requirements.txt`.

5.  **Install FFmpeg:**  You need to ensure FFmpeg is installed and accessible in your Koyeb environment.  This might involve using a custom Dockerfile.
    •   Example Dockerfile:
