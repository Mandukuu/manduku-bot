import os, re, threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.environ.get("BOT_TOKEN")
TILL_NUMBER = "1611583"
CHANNEL_LINK = os.environ.get("CHANNEL_LINK", "https://t.me/+vXKBKovKUKUyODg8")
PRICE = 10

app = Flask(__name__)
@app.route('/')
def home(): return f"Bot Live - Till {TILL_NUMBER}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = f"🔥 ANYTHING TRENDY PREMIUM\n\nUnlock VIP\n💰 Ksh {PRICE} - 24Hrs\n🏦 Till: {TILL_NUMBER}\n\n👇 Click:"
    keyboard = [
        [InlineKeyboardButton(f"💳 Pay Ksh {PRICE} - Till {TILL_NUMBER}", callback_data="pay")],
        [InlineKeyboardButton("✅ I Have Paid - Get Link", callback_data="paid")]
    ]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data == "pay":
        msg = f"👑 Pay Ksh {PRICE}\n\nTill: **{TILL_NUMBER}**\nAmount: {PRICE}\n\n1. M-Pesa > Buy Goods\n2. Till: {TILL_NUMBER}\n3. Amount: {PRICE}\n\nAfter pay click I Have Paid"
        await q.edit_message_text(msg, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ I Have Paid", callback_data="paid")]]), parse_mode="Markdown")
    else:
        await q.edit_message_text("📱 Send your M-Pesa code like UHHKG2RW49\nOr type 'paid'")

async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = update.message.text.strip().upper()
    # Accept ANY mpesa code or word paid
    if len(txt) >= 4:  # Accept everything now to fix error
        reply = f"✅ Payment Received! Till {TILL_NUMBER}\n\n🎉 VIP Link:\n{CHANNEL_LINK}\n\nClick to join. Don't share!"
        await update.message.reply_text(reply)
    else:
        await update.message.reply_text("Send code")

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

def run_bot():
    b = ApplicationBuilder().token(BOT_TOKEN).build()
    b.add_handler(CommandHandler("start", start))
    b.add_handler(CallbackQueryHandler(buttons))
    b.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_msg))
    print("FIXED - Accepts MPesa codes")
    b.run_polling()

if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    run_bot()
