import os
import json
import logging
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, ApplicationBuilder, CommandHandler, ContextTypes

# ======================================================
# Configuration
# ======================================================

BOT_TOKEN = os.getenv("BOT_TOKEN")  # Set in Render environment
OWNER_ID = 123456789  # 👈 Replace with your Telegram user ID
ADMIN_IDS = [OWNER_ID]  # You can add more admin IDs if needed

DATA_FILE = "points_data.json"
PORT = int(os.getenv("PORT", 10000))

# ======================================================
# Logging setup
# ======================================================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ======================================================
# Flask setup
# ======================================================
app = Flask(__name__)

# ======================================================
# Telegram bot setup
# ======================================================
application = ApplicationBuilder().token(BOT_TOKEN).build()

# ======================================================
# Utility functions
# ======================================================
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def ensure_user(user):
    data = load_data()
    if str(user.id) not in data:
        data[str(user.id)] = {"username": f"@{user.username}" if user.username else user.first_name, "points": 0}
        save_data(data)

# ======================================================
# Commands
# ======================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ensure_user(update.effective_user)
    await update.message.reply_text("👋 Hello! You can earn and give points here.\nUse /mypoints to check your points.")

async def mypoints(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    user = str(update.effective_user.id)
    ensure_user(update.effective_user)
    points = data[user]["points"]
    await update.message.reply_text(f"⭐ You currently have {points} points.")

async def plus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("❌ Only admins can give points.")
        return

    if len(context.args) < 2:
        await update.message.reply_text("Usage: /plus <username> <points>")
        return

    username = context.args[0].lstrip("@")
    try:
        points_to_add = int(context.args[1])
    except ValueError:
        await update.message.reply_text("Points must be a number.")
        return

    data = load_data()
    user_id = next((uid for uid, info in data.items() if info["username"] == f"@{username}"), None)

    if not user_id:
        await update.message.reply_text("User not found in data.")
        return

    data[user_id]["points"] += points_to_add
    save_data(data)
    await update.message.reply_text(f"✅ Added {points_to_add} points to @{username}!")

async def minus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("❌ Only admins can remove points.")
        return

    if len(context.args) < 2:
        await update.message.reply_text("Usage: /minus <username> <points>")
        return

    username = context.args[0].lstrip("@")
    try:
        points_to_remove = int(context.args[1])
    except ValueError:
        await update.message.reply_text("Points must be a number.")
        return

    data = load_data()
    user_id = next((uid for uid, info in data.items() if info["username"] == f"@{username}"), None)

    if not user_id:
        await update.message.reply_text("User not found in data.")
        return

    data[user_id]["points"] = max(0, data[user_id]["points"] - points_to_remove)
    save_data(data)
    await update.message.reply_text(f"✅ Removed {points_to_remove} points from @{username}!")

async def besthunters(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    if not data:
        await update.message.reply_text("No data yet.")
        return

    sorted_users = sorted(data.items(), key=lambda x: x[1]["points"], reverse=True)
    msg = "🏆 *Top Hunters:*\n\n"
    for i, (uid, info) in enumerate(sorted_users[:10], start=1):
        msg += f"{i}. {info['username']}: {info['points']} pts\n"

    await update.message.reply_text(msg, parse_mode="Markdown")

async def victory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ensure_user(update.effective_user)
    data = load_data()
    user_id = str(update.effective_user.id)
    data[user_id]["points"] += 1
    save_data(data)
    await update.message.reply_text("🏅 You earned 1 point!")

# ======================================================
# Add handlers
# ======================================================
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("mypoints", mypoints))
application.add_handler(CommandHandler("plus", plus))
application.add_handler(CommandHandler("minus", minus))
application.add_handler(CommandHandler("besthunters", besthunters))
application.add_handler(CommandHandler("victory", victory))

# ======================================================
# Webhook route (Fixed async issue)
# ======================================================
@app.route("/webhook", methods=["POST"])
def webhook():
    """Receive Telegram updates via webhook."""
    update = Update.de_json(request.get_json(force=True), application.bot)
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(application.process_update(update))
    except RuntimeError:
        asyncio.run(application.process_update(update))
    return "OK", 200

# ======================================================
# Set webhook on startup
# ======================================================
async def set_webhook():
    webhook_url = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/webhook"
    await application.bot.set_webhook(webhook_url)
    logger.info(f"✅ Webhook set to {webhook_url}")

# ======================================================
# Main entry
# ======================================================
if __name__ == "__main__":
    asyncio.run(set_webhook())
    app.run(host="0.0.0.0", port=PORT)    return user_id in ADMIN_IDS

def get_user_key(update: Update) -> str:
    """Return unique user key for data dict."""
    return str(update.effective_user.id)

# ------------------------------
# 🧩 Telegram Command Handlers
# ------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Points Bot is active!\n\nUse:\n"
        "/victory @username 50\n"
        "/minus @username 30\n"
        "/mypoints\n"
        "/besthunters"
    )

async def mypoints(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = get_user_key(update)
    data = load_data()

    if user_id not in data:
        username = (
            f"@{update.effective_user.username}"
            if update.effective_user.username
            else update.effective_user.first_name
        )
        data[user_id] = {"username": username, "points": 0}
        save_data(data)

    points = data[user_id]["points"]
    await update.message.reply_text(f"⭐ You have {points} points.")

async def victory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("🚫 You’re not authorized to use this command.")
        return

    if len(context.args) < 2:
        await update.message.reply_text("Usage: /victory @username 50")
        return

    username = context.args[0].lstrip("@")
    try:
        points = int(context.args[1])
    except ValueError:
        await update.message.reply_text("⚠️ Points must be a number.")
        return

    data = load_data()
    user = next(
        (uid for uid, info in data.items() if info["username"].lstrip("@") == username),
        None,
    )

    if not user:
        await update.message.reply_text("❌ User not found in the database.")
        return

    data[user]["points"] += points
    save_data(data)
    await update.message.reply_text(f"✅ Added {points} points to @{username}!")

async def minus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("🚫 You’re not authorized to use this command.")
        return

    if len(context.args) < 2:
        await update.message.reply_text("Usage: /minus @username 50")
        return

    username = context.args[0].lstrip("@")
    try:
        points = int(context.args[1])
    except ValueError:
        await update.message.reply_text("⚠️ Points must be a number.")
        return

    data = load_data()
    user = next(
        (uid for uid, info in data.items() if info["username"].lstrip("@") == username),
        None,
    )

    if not user:
        await update.message.reply_text("❌ User not found in the database.")
        return

    data[user]["points"] -= points
    save_data(data)
    await update.message.reply_text(f"✅ Deducted {points} points from @{username}!")

async def besthunters(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    if not data:
        await update.message.reply_text("No users found.")
        return

    leaderboard = sorted(data.items(), key=lambda x: x[1]["points"], reverse=True)
    msg = "🏆 *Best Bounty Hunters* 🏆\n\n"
    for i, (uid, info) in enumerate(leaderboard[:10], start=1):
        msg += f"{i}. {info['username']} — {info['points']} pts\n"

    await update.message.reply_text(msg, parse_mode="Markdown")

# ------------------------------
# 🌐 Flask + Webhook Setup
# ------------------------------
app = Flask(__name__)
application = None  # Global Telegram app

@app.route("/webhook", methods=["POST"])
def webhook():
    """Receive Telegram updates via webhook."""
    update = Update.de_json(request.get_json(force=True), application.bot)
    asyncio.create_task(application.process_update(update))
    return "OK", 200

@app.route("/")
def home():
    return "🤖 Telegram Points Bot is running!", 200

# ------------------------------
# 🚀 Main Setup
# ------------------------------
async def main():
    global application
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Register commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("mypoints", mypoints))
    application.add_handler(CommandHandler("victory", victory))
    application.add_handler(CommandHandler("minus", minus))
    application.add_handler(CommandHandler("besthunters", besthunters))

    # Setup webhook
    await application.bot.delete_webhook()
    webhook_url = os.getenv("RENDER_EXTERNAL_URL") + "/webhook"
    await application.bot.set_webhook(url=webhook_url)
    print(f"✅ Webhook set to {webhook_url}")

if __name__ == "__main__":
    asyncio.run(main())
    app.run(host="0.0.0.0", port=PORT)

