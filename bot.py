import os, threading, re, json
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.environ.get("BOT_TOKEN")
TILL = "1611583"
LINK = "https://t.me/+vXKBKovKUKUyODg8"
FILE = "/tmp/codes.json"

app = Flask(__name__)
@app.route('/')
def home(): return "Live - Strict Manual Mode"

def load():
    try:
        with open(FILE) as f: return json.load(f)
    except: return []

def save(c):
    try:
        with open(FILE, "w") as f: json.dump(c, f)
    except: pass

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = f"🔥 ANYTHING TRENDY VIP\n\n💰 Ksh 20 - Till {TILL}\n\nPay first, then send M-Pesa code."
    kb = [
        [InlineKeyboardButton(f"💳 How to Pay Till {TILL}", callback_data="pay")],
        [InlineKeyboardButton("📱 I Have Code", callback_data="code")]
    ]
    await update.message.reply_text(txt, reply_markup=InlineKeyboardMarkup(kb))

async def btn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data == "pay":
        await q.edit_message_text(
            f"Pay Ksh 20 to Till **{TILL}**\n\n1. M-Pesa > Lipa > Buy Goods\n2. Till: {TILL}\n3. Amount: 20\n\nYou will get SMS with code like **SH12AB34CD**\nSend THAT code here. Don't type 'paid'.",
            parse_mode="Markdown"
        )
    else:
        await q.edit_message_text("Send your 10-char M-Pesa code, e.g. UHHKG2RW49")

async def msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = update.message.text.strip().upper()
    used = load()

    # BLOCK paid, hello, anything not 10 chars
    if code == "PAID":
        await update.message.reply_text("❌ Don't type 'paid'. Send the real M-Pesa code like UHHKG2RW49 from your M-Pesa SMS.")
        return

    if not re.match(r"^[A-Z0-9]{10}$", code):
        await update.message.reply_text(f"❌ Invalid code: {code}\n\nMust be exactly 10 letters/numbers like UHHKG2RW49\n\nPay Till {TILL} first!")
        return

    if code in used:
        await update.message.reply_text(f"❌ Code {code} already used! One code = one person.")
        return

    used.append(code)
    save(used)
    await update.message.reply_text(f"✅ Code {code} OK!\n\nVIP Link:\n{LINK}\n\nJoin now. I will verify this code in M-Pesa app later.")

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

def run_bot():
    b = ApplicationBuilder().token(BOT_TOKEN).build()
    b.add_handler(CommandHandler("start", start))
    b.add_handler(CallbackQueryHandler(btn))
    b.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, msg))
    print("STRICT MANUAL LIVE")
    b.run_polling()

if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    run_bot()
