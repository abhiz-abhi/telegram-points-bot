import os
import json
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ------------------------------
# Environment Variables
# ------------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]
PORT = int(os.getenv("PORT", "10000"))
DB_FILE = "points_data.json"

# ------------------------------
# Setup Logging
# ------------------------------
logging.basicConfig(level=logging.INFO)

# ------------------------------
# Helper Functions
# ------------------------------
def load_data():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

def is_admin(user_id):
    return user_id in ADMIN_IDS

# ------------------------------
# Telegram Command Handlers
# ------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Points Bot is active! Use /victory, /minus, /mypoints, /besthunters.")

async def mypoints(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    data = load_data()

    if user_id not in data:
        data[user_id] = {"username": f"@{update.effective_user.username}", "points": 0}
        save_data(data)

    points = data[user_id]["points"]
    await update.message.reply_text(f"⭐ You have {points} points.")

async def victory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("🚫 You are not authorized to use this command.")
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
    user = next((uid for uid, info in data.items() if info["username"] == f"@{username}"), None)

    if not user:
        await update.message.reply_text("❌ User not found in the database.")
        return

    data[user]["points"] += points
    save_data(data)
    await update.message.reply_text(f"✅ Added {points} points to @{username}!")

async def minus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("🚫 You are not authorized to use this command.")
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
    user = next((uid for uid, info in data.items() if info["username"] == f"@{username}"), None)

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

    await update.message.reply_markdown(msg)

# ------------------------------
# Flask and Webhook Setup
# ------------------------------
app = Flask(__name__)
application = None

@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "OK", 200

@app.route("/")
def home():
    return "🤖 Telegram Points Bot is running!", 200

# ------------------------------
# Main Async Setup
# ------------------------------
async def main():
    global application
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("mypoints", mypoints))
    application.add_handler(CommandHandler("victory", victory))
    application.add_handler(CommandHandler("minus", minus))
    application.add_handler(CommandHandler("besthunters", besthunters))

    await application.bot.delete_webhook()
    webhook_url = os.getenv("RENDER_EXTERNAL_URL") + "/webhook"
    await application.bot.set_webhook(url=webhook_url)

    print(f"✅ Webhook set to {webhook_url}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
    app.run(host="0.0.0.0", port=PORT)    user = next((uid for uid, info in data.items() if info["username"] == f"@{username}"), None)

    if not user:
        await update.message.reply_text("❌ User not found in the database.")
        return

    data[user]["points"] += points
    save_data(data)
    await update.message.reply_text(f"✅ Added {points} points to @{username}!")

async def minus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("🚫 You are not authorized to use this command.")
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
    user = next((uid for uid, info in data.items() if info["username"] == f"@{username}"), None)

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

    await update.message.reply_markdown(msg)

# ------------------------------
# Flask and Webhook Setup
# ------------------------------
app = Flask(__name__)
application = None

@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "OK", 200

@app.route("/")
def home():
    return "🤖 Telegram Points Bot is running!", 200

# ------------------------------
# Main Async Setup
# ------------------------------
async def main():
    global application
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("mypoints", mypoints))
    application.add_handler(CommandHandler("victory", victory))
    application.add_handler(CommandHandler("minus", minus))
    application.add_handler(CommandHandler("besthunters", besthunters))

    await application.bot.delete_webhook()
    webhook_url = os.getenv("RENDER_EXTERNAL_URL") + "/webhook"
    await application.bot.set_webhook(url=webhook_url)

    print(f"✅ Webhook set to {webhook_url}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
    app.run(host="0.0.0.0", port=PORT)        return

    username = context.args[0].lstrip("@")
    try:
        points = int(context.args[1])
    except ValueError:
        await update.message.reply_text("⚠️ Points must be a number.")
        return

    data = load_data()
    user = next((uid for uid, info in data.items() if info["username"] == f"@{username}"), None)

    if not user:
        await update.message.reply_text("User not found in the database.")
        return

    data[user]["points"] += points
    save_data(data)
    await update.message.reply_text(f"✅ Added {points} points to @{username}!")

async def plus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await victory(update, context)

async def minus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("❌ You are not authorized to use this command.")
        return

    if len(context.args) != 2:
        await update.message.reply_text("Usage: /minus @username 50")
        return

    username = context.args[0].lstrip("@")
    try:
        points = int(context.args[1])
    except ValueError:
        await update.message.reply_text("⚠️ Points must be a number.")
        return

    data = load_data()
    user = next((uid for uid, info in data.items() if info["username"] == f"@{username}"), None)

    if not user:
        await update.message.reply_text("User not found in the database.")
        return

    data[user]["points"] -= points
    save_data(data)
    await update.message.reply_text(f"✅ Deducted {points} points from @{username}!")

async def mypoints(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    data = load_data()

    if user_id not in data:
        data[user_id] = {"username": f"@{update.effective_user.username}", "points": 0}
        save_data(data)

    points = data[user_id]["points"]
    await update.message.reply_text(f"⭐ You have {points} points.")

async def besthunters(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    if not data:
        await update.message.reply_text("No users found.")
        return

    leaderboard = sorted(data.items(), key=lambda x: x[1]["points"], reverse=True)
    top = leaderboard[:10]
    msg = "🏆 *Best Bounty Hunters* 🏆\n\n"
    for i, (uid, info) in enumerate(top, start=1):
        msg += f"{i}. {info['username']} — {info['points']} pts\n"

    await update.message.reply_markdown(msg)

# ------------------------------
# Webhook and Flask Setup
# ------------------------------
app = Flask(__name__)
application = None

@app.route("/webhook", methods=["POST"])
def webhook():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), application.bot)
        application.update_queue.put_nowait(update)
        return "OK", 200
    return "ERROR", 400

@app.route("/")
def home():
    return "🤖 Telegram Points Bot is running!", 200

# ------------------------------
# Main
# ------------------------------
async def main():
    global application
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("victory", victory))
    application.add_handler(CommandHandler("plus", plus))
    application.add_handler(CommandHandler("minus", minus))
    application.add_handler(CommandHandler("mypoints", mypoints))
    application.add_handler(CommandHandler("besthunters", besthunters))

    await application.bot.delete_webhook()
    webhook_url = os.getenv("RENDER_EXTERNAL_URL") + "/webhook"
    await application.bot.set_webhook(url=webhook_url)

    print(f"✅ Webhook set to {webhook_url}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
    app.run(host="0.0.0.0", port=PORT)    return str(update.effective_user.id)

def is_admin(user_id):
    """Check if the given user_id is in the admin list."""
    return user_id in ADMIN_IDS

def get_display_name(user):
    """Return display name with username if available."""
    if user.username:
        return f"{user.first_name} (@{user.username})"
    return user.first_name or str(user.id)

# ------------------------------------------------------------
# 🧩 Core Bot Commands
# ------------------------------------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show welcome message (only for group chats)."""
    if update.message.chat.type != "group" and update.message.chat.type != "supergroup":
        await update.message.reply_text("⚠️ This bot works only in groups.")
        return
    await update.message.reply_text("👋 Points Bot is active! Use /victory, /besthunters, /mypoints, etc.")

async def victory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add points for a victory (admin only)."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("🚫 You’re not authorized to use this command.")
        return

    if len(context.args) < 2:
        await update.message.reply_text("Usage: /victory {username/user_id} {points}")
        return

    target = context.args[0]
    try:
        points = int(context.args[1])
    except ValueError:
        await update.message.reply_text("⚠️ Points must be a number.")
        return

    data = load_data()

    # Find by username or user_id
    user_id = None
    for uid, info in data.items():
        if info["username"].lower() == target.lower() or uid == target:
            user_id = uid
            break

    if not user_id:
        await update.message.reply_text("❌ User not found in database.")
        return

    data[user_id]["points"] += points
    save_data(data)
    await update.message.reply_text(f"✅ Added {points} points to {data[user_id]['username']}!")

async def plus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manually add points (admin only)."""
    await victory(update, context)

async def minus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Deduct points (admin only)."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("🚫 You’re not authorized to use this command.")
        return

    if len(context.args) < 2:
        await update.message.reply_text("Usage: /minus {username/user_id} {points}")
        return

    target = context.args[0]
    try:
        points = int(context.args[1])
    except ValueError:
        await update.message.reply_text("⚠️ Points must be a number.")
        return

    data = load_data()
    user_id = None
    for uid, info in data.items():
        if info["username"].lower() == target.lower() or uid == target:
            user_id = uid
            break

    if not user_id:
        await update.message.reply_text("❌ User not found in database.")
        return

    data[user_id]["points"] -= points
    save_data(data)
    await update.message.reply_text(f"✅ Deducted {points} points from {data[user_id]['username']}!")

async def besthunters(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show top 10 users."""
    data = load_data()
    if not data:
        await update.message.reply_text("No data available yet.")
        return

    sorted_users = sorted(data.items(), key=lambda x: x[1]["points"], reverse=True)[:10]
    leaderboard = "🏆 *Best Bounty Hunters* 🏆\n\n"
    for i, (uid, info) in enumerate(sorted_users, start=1):
        leaderboard += f"{i}. {info['username']} — {info['points']} pts\n"

    await update.message.reply_text(leaderboard, parse_mode="Markdown")

async def mypoints(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user's points."""
    user_id = get_user_key(update)
    data = load_data()
    if user_id not in data:
        data[user_id] = {"username": f"@{update.effective_user.username}" if update.effective_user.username else update.effective_user.first_name, "points": 0}
        save_data(data)

    user_info = data[user_id]
    await update.message.reply_text(f"💰 {user_info['username']}, you have {user_info['points']} points.")

# ------------------------------------------------------------
# 🚀 Main Function
# ------------------------------------------------------------

def main():
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("victory", victory))
    app.add_handler(CommandHandler("plus", plus))
    app.add_handler(CommandHandler("minus", minus))
    app.add_handler(CommandHandler("besthunters", besthunters))
    app.add_handler(CommandHandler("mypoints", mypoints))

    print("✅ Bot is running...")
    app.run_polling()

if __name__ == "__main__":

    main()

