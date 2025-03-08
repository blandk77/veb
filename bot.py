
import os
import asyncio
import subprocess
import pyrogram
import time
import re
import psutil
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
    plugins=dict(root="plugins"),
    connection_retries=5,  # Adjust connection retries as needed
    connect_timeout=30,    # Increase connection timeout (seconds)
    sleep_threshold=60      # Increase the sleep threshold
)

# --- Helper Functions ---
def format_download_progress(current, total, start_time):
    """Formats the download progress bar."""
    percentage = current * 100 / total
    downloaded_size = current / (1024 * 1024)  # Size in MB
    total_size = total / (1024 * 1024)  # Total size in MB
    speed = current / (time.time() - start_time) / (1024 * 1024) if time.time() > start_time else 0  # Speed in MB/s
    remaining_time = (total - current) / (speed * 1024 * 1024) if speed > 0 else 0  # Remaining time in seconds

    bar = "⬡" * int(20 * current / total) + " " * (20 - int(20 * current / total)) # Change the progress bar design

    progress_message = f"""
⚠️ Please wait...

☃️ Dᴏᴡɴʟᴏᴀᴅ Sᴛᴀʀᴛᴇᴅ....

⬡⬡⬡⬡⬡⬡⬡⬡⬡⬡⬡⬡⬡⬡⬡⬡⬡⬡⬡⬡
╭━━━━❰ᴘʀᴏɢʀᴇss ʙᴀʀ❱━➣
┣ Sɪᴢᴇ: {downloaded_size:.1f} Mʙ | {total_size:.2f} Mʙ
┣ Dᴏɴᴇ : {percentage:.2f}%
┣ Sᴩᴇᴇᴅ: {speed:.1f} Mʙ/s
┣ Eᴛᴀ: {remaining_time:.0f}s
╰━━━━━━━━━━━━━━━➣ Join @The_TGguy
"""
    return progress_message

async def get_system_stats():
    """Gets CPU, RAM, and Disk usage statistics."""
    cpu_usage = psutil.cpu_percent(interval=0.5)
    ram_usage = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage("/").percent  # Change "/" to your root directory if needed

    return cpu_usage, ram_usage, disk_usage

async def run_ffmpeg(input_file, preset, output_file, message, client, total_size):
    """Runs FFmpeg, parses progress, and reports system stats."""
    try:
        command = f"ffmpeg -i '{input_file}' {preset} '{output_file}' -y"  # Added quotes around filenames and -y
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=os.getcwd()  # Runs ffmpeg where it can be run
        )
        start_time = time.time()
        compressed_size = 0.0

        while True:
            line = await process.stderr.readline()
            if not line:
                break  # Exit loop if ffmpeg is finished.

            line = line.decode().strip()

            try:
                compressed_size = os.path.getsize(output_file)
            except FileNotFoundError:
                compressed_size = 0

            cpu_usage, ram_usage, disk_usage = await get_system_stats()  # Get System Stats in Real-time

            progress_message = f"""
⚙️ Encoding...

╭─⌯══ sʏsᴛᴇᴍ | ʜᴛᴏᴘ ══⌯──★
├ ᴄᴘᴜ ᴜsᴀɢᴇ: {cpu_usage:.1f}%
├ ʀᴀᴍ ᴜsᴀɢᴇ: {ram_usage:.1f}%
├ ᴅɪsᴋ sᴘᴀᴄᴇ ʟᴇғᴛ: {disk_usage:.1f}%
├ ᴘʀᴏᴄᴇssɪɴɢ ᴍᴇᴅɪᴀ: {os.path.basename(input_file)}
├ ᴅᴏᴡɴʟᴏᴀᴅᴇᴅ: {total_size / (1024 * 1024):.2f} MBytes
├ ᴄᴏᴍᴘʀᴇssᴇᴅ: {compressed_size / (1024 * 1024):.2f} MBytes
╰─══ TG GUY!! ══─★
            """
            # Now, Update.
            try:
                await client.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=message.id,
                    text=progress_message
                )
            except pyrogram.errors.MessageNotModified:
                pass  # Suppress "MessageNotModified" error (no change in content)


        returncode = await process.wait()  # Awaits for process to be complete

        if returncode != 0:
            error_message = (await process.stderr.read()).decode().strip()  # Gets the error.
            print(f"FFmpeg error: {error_message}")
            return False, error_message

        return True, None  # success and no error

    except Exception as e:
        print(f"Error running FFmpeg: {e}")
        return False, str(e)

# --- Bot State (In-memory, replace with database for production) ---
user_presets = {}  # User-specific preset overrides {user_id: {p1: "...", p2: ...}}
user_thumbnails = {}  # User-specific thumbnails {user_id: file_id}

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

1. Send a video or document file (.mp4, .mkv).
2. Reply to the file with a preset command (/p1, /p2, /p3, /p4) followed by the desired output file name (e.g., /p1 output.mp4).

**Commands:**

*   /start - Start the bot.
*   /help - Show this help message.
*   /p1, /p2, /p3, /p4 - Use a preset for encoding.  Reply to the file with the command and desired output name.
*   /vp1, /vp2, /vp3, /vp4 - View the default preset settings.
*   /sp1, /sp2, /sp3, /sp4 - Set your custom preset. Reply to this command with the desired ffmpeg setting.
*   /dp1, /dp2, /dp3, /dp4 - Delete your custom preset, reverting to default.
*   /sthumb - Set a thumbnail by replying to a photo.
*   /vthumb - View your saved thumbnail.
    """
    await message.reply_text(help_text, parse_mode="Markdown")

# --- Preset Commands ---
async def process_preset(client, message: Message, preset_num: int):
    """Handles preset commands (/p1, /p2, /p3, /p4)."""
    if not message.reply_to_message or not (message.reply_to_message.video or message.reply_to_message.document):  # Accept videos and documents
        await message.reply_text("Reply to a video or document file to use a preset.")
        return

    try:
        output_filename = message.text.split()[1]  # Get output filename from command
    except IndexError:
        await message.reply_text("Please provide an output filename after the preset command (e.g., /p1 output.mp4)")
        return

    is_video = message.reply_to_message.video is not None

    if is_video:
        media = message.reply_to_message.video
    else:
        media = message.reply_to_message.document

    # Extract the file extension from the filename or use .mp4 as a default
    input_file_extension = os.path.splitext(media.file_name)[1] if media.file_name else ".mp4"
    input_file = f"input{input_file_extension}"  # Use a dynamic filename
    output_file = output_filename  # Filename provided by user
    start_time = time.time()  # Capture start time for accurate eta calculation

    try:
        # Send an initial message
        main_message = await message.reply_text("⚠️Please wait...\nTʀyɪɴɢ Tᴏ DᴏᴡɴLᴏᴀᴅɪɴɢ....")

        # Download the video or document with progress tracking
        total_size = media.file_size # Grab File size before download

        await client.download_media(
            media,
            file_name=input_file,
            progress=lambda current, total: asyncio.get_event_loop().create_task(
                client.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=main_message.id,
                    text=format_download_progress(current, total, start_time)
                )
            )
        )

        # Get the preset
        user_id = message.from_user.id
        if user_id in user_presets and f"p{preset_num}" in user_presets[user_id]:
            preset = user_presets[user_id][f"p{preset_num}"].strip()  # User's saved preset
        else:
            # Use default preset
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

        # Send an initial message and run FFmpeg
        success, error_message = await run_ffmpeg(input_file, preset, output_file, main_message, client, total_size)

        if success:
             # UPLOAD now
            await client.edit_message_text(
                chat_id=message.chat.id,
                message_id=main_message.id,
                text="📤 Uploading"
            )
            if os.path.exists(output_file):
                # Attach thumbnail if one exists
                thumbnail = user_thumbnails.get(user_id)
                if thumbnail:
                    try:
                        if is_video:
                            await client.send_video(
                                chat_id=message.chat.id,
                                video=output_file,
                                thumb=thumbnail,
                                progress=lambda current, total: asyncio.get_event_loop().create_task(
                                client.edit_message_text(
                                    chat_id=message.chat.id,
                                    message_id=main_message.id,
                                    text=f"Uploading {current * 100 / total:.1f}%"
                                )
                            ))
                        else:
                            await client.send_document(
                                chat_id=message.chat.id,
                                document=output_file,
                                thumb=thumbnail,
                                progress=lambda current, total: asyncio.get_event_loop().create_task(
                                client.edit_message_text(
                                    chat_id=message.chat.id,
                                    message_id=main_message.id,
                                    text=f"Uploading {current * 100 / total:.1f}%"
                                )
                            ))
                    except:
                         await client.edit_message_text(
                                chat_id=message.chat.id,
                                message_id=main_message.id,
                                text="Uploaded, however, cannot be thumbnailed."
                           )
                else:
                   try:
                       if is_video:
                           await client.send_video(
                               chat_id=message.chat.id, video=output_file,
                                progress=lambda current, total: asyncio.get_event_loop().create_task(
                                client.edit_message_text(
                                    chat_id=message.chat.id,
                                    message_id=main_message.id,
                                    text=f"Uploading {current * 100 / total:.1f}%"
                                )
                           ))

                       else:
                            await client.send_document(
                                chat_id=message.chat.id, document=output_file,
                                progress=lambda current, total: asyncio.get_event_loop().create_task(
                                client.edit_message_text(
                                    chat_id=message.chat.id,
                                    message_id=main_message.id,
                                    text=f"Uploading {current * 100 / total:.1f}%"
                                )
                            ))
                   except:
                        await client.edit_message_text(
                                chat_id=message.chat.id,
                                message_id=main_message.id,
                                text="Uploaded however, unable to upload."
                           )
            else:
                 await client.edit_message_text(
                        chat_id=message.chat.id,
                        message_id=main_message.id,
                        text="Encoding completed, but the output file was not found!"
                   )

        else:
             await client.edit_message_text(
                chat_id=message.chat.id,
                message_id=main_message.id,
                text=f"Encoding failed: {error_message}"
             )

    except Exception as e:
        print(f"Error processing video: {e}")
        await message.reply_text(f"An error occurred while processing the video: {e}")
    finally:
        # Clean up temporary files
        try:
            os.remove(input_file)
            os.remove(output_file)
        except OSError:
            pass  # Ignore if file doesn't exist

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

    await message.reply_text(f"Preset {preset_num} ({source}):\n`{preset}`", quote=True)  # Use Markdown for code formatting

# Register the view preset command
for i in range(1, 5):
    @bot.on_message(filters.command(f"vp{i}"))
    async def view_preset_command_handler(client, message, preset_num=i):
        await view_preset(client, message, preset_num)

async def set_preset(client, message: Message, preset_num: int):
    """Handles setting custom presets (/sp1, /sp2, /sp3, /sp4)."""
    if not message.reply_to_message or not message.reply_to_message.text:
        await message.reply_text("Reply to a message containing the ffmpeg preset you want to save.")
        return
    user_id = message.from_user.id
    preset = message.reply_to_message.text.strip()  # The ENTIRE ffmpeg string. Remove leading/trailing whitespace

    if user_id not in user_presets:
        user_presets[user_id] = {}
    user_presets[user_id][f"p{preset_num}"] = preset
    await message.reply_text(f"Saved preset {preset_num} for you.")

# Register the set preset command
for i in range(1, 5):
    @bot.on_message(filters.command(f"sp{i}"))
    async def set_preset_command_handler(client, message, preset_num=i):
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
for i in range(1, 5):
    @bot.on_message(filters.command(f"dp{i}"))
    async def delete_preset_command_handler(client, message, preset_num=i):
        await delete_preset(client, message, preset_num)

# --- Thumbnail Commands ---
@bot.on_message(filters.command("sthumb") & filters.reply & filters.photo)
async def set_thumbnail_command(client, message):
    """Handles setting a thumbnail."""
    if not message.reply_to_message:
        await message.reply_text("Reply to the photo with /sthumb to set it as the thumbnail.")
        return

    user_id = message.from_user.id
    file_id = message.photo.file_id  # Access directly from message.photo
    user_thumbnails[user_id] = file_id

    await message.reply_text("Thumbnail saved!")

@bot.on_message(filters.command("vthumb"))
async def view_thumbnail_command(client, message):
    """Handles viewing the saved thumbnail."""
    user_id = message.from_user.id
    if user_id in user_thumbnails:
        file_id = user_thumbnails[user_id]
        await bot.send_photo(chat_id=message.chat.id, photo=file_id, caption="Your saved thumbnail.")
    else:
        await message.reply_text("No saved thumbnail. Send a photo and reply the photo with /sthumb to set one.")

# --- Admin Commands (Optional) ---
if ADMIN_USER_ID:
    @bot.on_message(filters.command("admin") & filters.user(ADMIN_USER_ID))
    async def admin_command(client, message):
        await message.reply_text("Admin commands are working.")

    # Example: Adding a command to clear all presets for all users
    @bot.on_message(filters.command("clearallpresets") & filters.user(ADMIN_USER_ID))
    async def clear_all_presets_command(client, message):
        global user_presets
        user_presets = {}  # Clear all user presets
        await message.reply_text("All user presets have been cleared.")

print("Bot is ready!")
