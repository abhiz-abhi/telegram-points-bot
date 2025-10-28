import logging
import os
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from pathlib import Path

# ------------------------------------------------------------
# 🔧 Configuration Section
# ------------------------------------------------------------

# Get bot token and admin IDs from environment variables (safe for Render)
BOT_TOKEN = os.getenv("BOT_TOKEN")  # You will set this in Render’s dashboard
ADMIN_IDS = os.getenv("ADMIN_IDS", "")  # Comma-separated list of admin user IDs
ADMIN_IDS = [int(x) for x in ADMIN_IDS.split(",") if x.strip().isdigit()]

DATA_FILE = Path("points_data.json")

# ------------------------------------------------------------
# 🧠 Helper Functions
# ------------------------------------------------------------

def load_data():
    """Load user data from JSON file, or create an empty one if not found."""
    if DATA_FILE.exists():
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    """Save user data to JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_user_key(update: Update):
    """Get a unique key for a user (user_id as string)."""
    return str(update.effective_user.id)

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