import os
import asyncio
import subprocess
import pyrogram
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from config import API_ID, API_HASH, BOT_TOKEN, BOT_NAME, \
    DEFAULT_FFMPEG_PRESET_1, DEFAULT_FFMPEG_PRESET_2, DEFAULT_FFMPEG_PRESET_3, DEFAULT_FFMPEG_PRESET_4, ADMIN_USER_ID

# Initialize the bot
bot = Client(
    BOT_NAME,
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="plugins")  # Enable plugins directory
)

# --- Helper Functions ---
async def run_ffmpeg(input_file, preset, output_file):
    """Runs FFmpeg with the specified preset."""
    try:
        command = f"ffmpeg -i {input_file} {preset} {output_file}"
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            error_message = stderr.decode().strip()
            print(f"FFmpeg error: {error_message}")
            return False, error_message # Return the error message
        return True, None  # Success, no error
    except Exception as e:
        print(f"Error running FFmpeg: {e}")
        return False, str(e)

# --- Bot State (In-memory, replace with database for production) ---
user_presets = {}  # User-specific preset overrides {user_id: {p1: "...", p2: ...}}
user_thumbnails = {} # User-specific thumbnails {user_id: file_id}

# --- Command Handlers ---

@bot.on_message(filters.command("start"))
async def start_command(client, message):
    """Handles the /start command."""
    await message.reply_text(
        f"Welcome to the {BOT_NAME}! Use /help to see available commands."
    )

@bot.on_message(filters.command("help"))
async def help_command(client, message):
    """Handles the /help command."""
    help_text = """
**Usage:**

1. Send a video file.
2. Reply to the video with a preset command (/p1, /p2, /p3, /p4) followed by the desired output file name (e.g., /p1 output.mp4).

**Commands:**

*   /start - Start the bot.
*   /help - Show this help message.
*   /p1, /p2, /p3, /p4 - Use a preset for encoding.  Reply to the video file with the command and desired output name.
*   /vp1, /vp2, /vp3, /vp4 - View the default preset settings.
*   /sp1, /sp2, /sp3, /sp4 - Set your custom preset. Reply to this command with the desired ffmpeg setting.
*   /dp1, /dp2, /dp3, /dp4 - Delete your custom preset, reverting to default.
*   /sthumb - Set a thumbnail by replying to a photo.
*   /vthumb - View your saved thumbnail.
    """
    await message.reply_text(help_text)

# --- Preset Commands ---

async def process_preset(client, message: Message, preset_num: int):
    """Handles preset commands (/p1, /p2, /p3, /p4)."""
    if not message.reply_to_message or not message.reply_to_message.video:
        await message.reply_text("Reply to a video file to use a preset.")
        return

    try:
        output_filename = message.text.split()[1] # Get output filename from command
    except IndexError:
        await message.reply_text("Please provide an output filename after the preset command (e.g., /p1 output.mp4)")
        return

    input_file = "input.mp4"  # Temporary file name
    output_file = output_filename  # Use filename provided by user

    try:
        # Download the video
        await message.reply_to_message.download(input_file)

        # Get the preset
        user_id = message.from_user.id
        if user_id in user_presets and f"p{preset_num}" in user_presets[user_id]:
            preset = user_presets[user_id][f"p{preset_num}"].strip() # Use the user's saved preset. Remove leading/trailing spaces.
        else:
            # Use default preset. Remove leading/trailing spaces.
            if preset_num == 1:
                preset = DEFAULT_FFMPEG_PRESET_1.strip()
            elif preset_num == 2:
                preset = DEFAULT_FFMPEG_PRESET_2.strip()
            elif preset_num == 3:
                preset = DEFAULT_FFMPEG_PRESET_3.strip()
            elif preset_num == 4:
                preset = DEFAULT_FFMPEG_PRESET_4.strip()
            else:
                await message.reply_text("Invalid preset number.")
                return

        # Run FFmpeg
        await message.reply_text(f"Encoding with preset {preset_num}...\nPlease wait, this may take a while.")
        success, error_message = await run_ffmpeg(input_file, preset, output_file)

        if success:
            # Send the compressed video back
            await message.reply_text("Encoding complete! Sending the file...")
            if os.path.exists(output_file):
                # Attach thumbnail if one exists
                thumbnail = user_thumbnails.get(user_id)
                if thumbnail:
                    await client.send_video(
                        chat_id=message.chat.id,
                        video=output_file,
                        thumb=thumbnail
                    )
                else:
                     await client.send_video(chat_id=message.chat.id, video=output_file) # Send without thumbnail
            else:
                await message.reply_text("Encoding completed, but the output file was not found!")


        else:
            await message.reply_text(f"Encoding failed: {error_message}")

    except Exception as e:
        print(f"Error processing video: {e}")
        await message.reply_text(f"An error occurred while processing the video: {e}")
    finally:
        # Clean up temporary files
        try:
            os.remove(input_file)
            os.remove(output_file)
        except OSError:
            pass # Ignore if file doesn't exist

# Register preset commands
for i in range(1, 5):
    @bot.on_message(filters.command(f"p{i}"))
    async def preset_command_handler(client, message, preset_num=i):
        await process_preset(client, message, preset_num)

async def view_preset(client, message: Message, preset_num: int):
    """View the default preset settings."""
    user_id = message.from_user.id
    if user_id in user_presets and f"p{preset_num}" in user_presets[user_id]:
        preset = user_presets[user_id][f"p{preset_num}"]
        source = "your custom preset"
    else:
        if preset_num == 1:
            preset = DEFAULT_FFMPEG_PRESET_1
        elif preset_num == 2:
            preset = DEFAULT_FFMPEG_PRESET_2
        elif preset_num == 3:
            preset = DEFAULT_FFMPEG_PRESET_3
        elif preset_num == 4:
            preset = DEFAULT_FFMPEG_PRESET_4
        else:
            await message.reply_text("Invalid preset number.")
            return
        source = "the default preset"

    await message.reply_text(f"Preset {preset_num} ({source}):\n`{preset}`", quote=True, parse_mode="markdown") # Use Markdown for code formatting

#Register the view preset command
for i in range(1,5):
    @bot.on_message(filters.command(f"vp{i}"))
    async def view_preset_command_handler(client, message, preset_num = i):
        await view_preset(client, message, preset_num)

async def set_preset(client, message: Message, preset_num: int):
    """Handles setting custom presets (/sp1, /sp2, /sp3, /sp4)."""
    if not message.reply_to_message or not message.reply_to_message.text:
        await message.reply_text("Reply to a message containing the ffmpeg preset you want to save.")
        return
    user_id = message.from_user.id
    preset = message.reply_to_message.text.strip() # The ENTIRE ffmpeg string. Remove leading/trailing whitespace

    if user_id not in user_presets:
        user_presets[user_id] = {}
    user_presets[user_id][f"p{preset_num}"] = preset
    await message.reply_text(f"Saved preset {preset_num} for you.")

# Register the set preset command
for i in range (1,5):
    @bot.on_message(filters.command(f"sp{i}"))
    async def set_preset_command_handler(client, message, preset_num = i):
        await set_preset(client, message, preset_num)

async def delete_preset(client, message: Message, preset_num: int):
    """Handles deleting custom presets (/dp1, /dp2, /dp3, /dp4)."""
    user_id = message.from_user.id
    if user_id in user_presets and f"p{preset_num}" in user_presets[user_id]:
        del user_presets[user_id][f"p{preset_num}"]
        await message.reply_text(f"Deleted your custom preset {preset_num}.")
    else:
        await message.reply_text(f"You don't have a custom preset saved for {preset_num}.")

# Register the delete preset command
for i in range (1,5):
    @bot.on_message(filters.command(f"dp{i}"))
    async def delete_preset_command_handler(client, message, preset_num = i):
        await delete_preset(client, message, preset_num)

# --- Thumbnail Commands ---

@bot.on_message(filters.command("sthumb") & filters.reply & filters.reply.photo)
async def set_thumbnail_command(client, message):
    """Handles setting a thumbnail."""
    user_id = message.from_user.id
    file_id = message.reply_to_message.photo.file_id
    user_thumbnails[user_id] = file_id # Store the file_id

    await message.reply_text("Thumbnail saved!")

@bot.on_message(filters.command("vthumb"))
async def view_thumbnail_command(client, message):
    """Handles viewing the saved thumbnail."""
    user_id = message.from_user.id
    if user_id in user_thumbnails:
        file_id = user_thumbnails[user_id]
        await bot.send_photo(chat_id=message.chat.id, photo=file_id, caption="Your saved thumbnail.") # Send the photo by file_id.
    else:
        await message.reply_text("No saved thumbnail. Send a photo and reply the photo with /sthumb to set one.")

# --- Admin Commands (Optional) ---
if ADMIN_USER_ID:
    @bot.on_message(filters.command("admin") & filters.user(ADMIN_USER_ID))
    async def admin_command(client, message):
        await message.reply_text("Admin commands are working.")

    # Example:  Adding a command to clear all presets for all users
    @bot.on_message(filters.command("clearallpresets") & filters.user(ADMIN_USER_ID))
    async def clear_all_presets_command(client, message):
        global user_presets
        user_presets = {}  # Clear all user presets
        await message.reply_text("All user presets have been cleared.")

print("Bot Started......🎉")

# You will run the bot using bot.run() from your main.py
