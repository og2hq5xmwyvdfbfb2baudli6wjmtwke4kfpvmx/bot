import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)
import asyncio

# =========================
# CONFIG
# =========================
BOT_TOKEN = "8247238867:AAFegzRzyLUkK5CHVK535L4ZshwHxXsCHVo"
ADMIN_ID = 6541825979
USDT_ADDRESS = "TUmPVgYgFSw2cSigkCS276Rxxomm9mvdAh"

MIN_DEPOSIT = 50.0
RATE = 0.40  # $0.40 = 1 Credit

# =========================
# TEMP USER DATABASE
# =========================
users = {}  # user_id: {username, balance, active}

# =========================
# LOGGING
# =========================
logging.basicConfig(level=logging.INFO)

# =========================
# /start
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid = user.id

    if uid not in users:
        users[uid] = {
            "username": user.username,
            "balance": 0.0,
            "active": False
        }

    text = f"""
👋 Hello **{user.first_name}!**

💠 Virtual Credit Service  
💠 Rate: **$0.40 = 1 Credit**  
💠 Minimum Deposit: **${MIN_DEPOSIT}**

Choose an option below:
"""

    keyboard = [
        [InlineKeyboardButton("💳 Deposit", callback_data="deposit")],
        [InlineKeyboardButton("📊 My Balance", callback_data="balance")],
        [InlineKeyboardButton("ℹ️ Rate Info", callback_data="rate")]
    ]

    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# =========================
# BUTTON HANDLER
# =========================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = query.from_user
    uid = user.id

    if uid not in users:
        users[uid] = {
            "username": user.username,
            "balance": 0.0,
            "active": False
        }

    if query.data == "deposit":
        await query.edit_message_text(
            f"""
💳 **Deposit Instructions**

Minimum deposit: **${MIN_DEPOSIT}**

Send **USDT (TRC20)** to:
`{USDT_ADDRESS}`

After payment, send screenshot to admin.

👨‍💼 Admin:
tg://user?id={ADMIN_ID}
            """,
            parse_mode="Markdown"
        )

    elif query.data == "balance":
        u = users[uid]
        status = "Active ✅" if u["active"] else "Not Active ❌"
        credits = u["balance"] / RATE if u["balance"] > 0 else 0

        await query.edit_message_text(
            f"""
📊 **Your Account**

Status: **{status}**
Balance: **${u['balance']:.2f}**
Credits: **{credits:.2f}**
            """,
            parse_mode="Markdown"
        )

    elif query.data == "rate":
        await query.edit_message_text(
            """
💱 **Credit Rate**

$1 = 2.5 Credits  
1 Credit = $0.40

Example:
$10 → 25 Credits  
$50 → 125 Credits
            """,
            parse_mode="Markdown"
        )

# =========================
# ADMIN COMMAND
# =========================
async def add_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if len(context.args) != 2:
        await update.message.reply_text("Usage: /addbalance user_id amount")
        return

    try:
        user_id = int(context.args[0])
        amount = float(context.args[1])
        if amount <= 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text("Invalid input.")
        return

    if user_id not in users:
        users[user_id] = {
            "username": None,
            "balance": 0.0,
            "active": False
        }

    users[user_id]["balance"] += amount

    if users[user_id]["balance"] >= MIN_DEPOSIT:
        users[user_id]["active"] = True

    await update.message.reply_text(
        f"✅ Added ${amount:.2f}\n"
        f"New Balance: ${users[user_id]['balance']:.2f}"
    )

# =========================
# MAIN
# =========================
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("addbalance", add_balance))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot is running...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
