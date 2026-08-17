import os, re, threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.environ.get("BOT_TOKEN")
TILL_NUMBER = "1611583"
CHANNEL_LINK = os.environ.get("CHANNEL_LINK", "https://t.me/+vXKBKovKUKUyODg8")
PRICE = 20

app = Flask(__name__)
@app.route('/')
def home(): return f"Bot Live - Till {TILL_NUMBER} - 20KSH"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🔥 **ANYTHING TRENDY PREMIUM**\n\n"
        "Unlock VIP Channel with all trending content.\n\n"
        f"💰 Price: **Ksh {PRICE}** - 24 Hours Access\n"
        f"🏦 Till: **{TILL_NUMBER}**\n\n"
        "👇 Click below:"
    )
    keyboard = [
        [InlineKeyboardButton(f"💳 Pay Ksh {PRICE} - Till {TILL_NUMBER}", callback_data="pay")],
        [InlineKeyboardButton("✅ I Have Paid - Get Link", callback_data="paid")]
    ]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data == "pay":
        msg = (
            f"👑 **Pay Ksh {PRICE} to Unlock**\n\n"
            f"• Till Number: **{TILL_NUMBER}**\n"
            f"• Amount: **{PRICE}**\n\n"
            f"**Steps:**\n"
            f"1. M-Pesa > Lipa na M-Pesa > Buy Goods\n"
            f"2. Till: {TILL_NUMBER}\n"
            f"3. Amount: {PRICE}\n"
            f"4. Enter PIN\n\n"
            f"After paying, click I Have Paid."
        )
        await q.edit_message_text(msg, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ I Have Paid", callback_data="paid")]]), parse_mode="Markdown")
    elif q.data == "paid":
        await q.edit_message_text(
            f"📱 **Send your M-Pesa Code**\n\n"
            f"Send code like `SH12AB34CD` you got after paying Ksh {PRICE} to Till {TILL_NUMBER}.\n\n"
            f"Or just type `paid` to get link instantly."
        )

async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = update.message.text.strip()
    # Accept any code or word 'paid' - instant link (Till mode)
    if re.match(r"^[A-Z0-9]{6,12}$", txt.upper()) or "paid" in txt.lower() or re.match(r"^SH\w+", txt.upper()):
        reply = (
            f"✅ **Payment Received! Till {TILL_NUMBER}**\n\n"
            f"🎉 Welcome to VIP!\n\n"
            f"👇 **Your Private Channel Link:**\n{CHANNEL_LINK}\n\n"
            f"Click to join. Don't share - 24hr access.\n\n"
            f"Enjoy 🔥"
        )
        await update.message.reply_text(reply, parse_mode="Markdown")
    else:
        await update.message.reply_text(f"Send M-Pesa code after paying {PRICE} to Till {TILL_NUMBER}, or type 'paid'.")

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

def run_bot():
    b = ApplicationBuilder().token(BOT_TOKEN).build()
    b.add_handler(CommandHandler("start", start))
    b.add_handler(CallbackQueryHandler(buttons))
    b.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_msg))
    print("TILL BOT LIVE - Link:", CHANNEL_LINK)
    b.run_polling()

if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    run_bot()    payload = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerBuyGoodsOnline",
        "Amount": amount,
        "PartyA": phone,
        "PartyB": shortcode,
        "PhoneNumber": phone,
        "CallBackURL": CALLBACK_URL,
        "AccountReference": f"trendy_{user_id}",
        "TransactionDesc": "Anything Trendy Access"
    }
    try:
        res = requests.post("https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest", json=payload, headers=headers)
        print(res.text)
        data = res.json()
        if data.get("ResponseCode") == "0":
            PENDING[data.get("CheckoutRequestID")] = user_id
            return True
    except Exception as e:
        print("STK Error:", e)
    return False

@app.route('/')
def home(): return "Anything Trendy Bot Live - 20KSH"

@app.route('/mpesa_callback', methods=['POST'])
def callback():
    print("Callback:", request.json)
    return jsonify({"ResultCode":0,"ResultDesc":"Accepted"})

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🔥 **ANYTHING TRENDY PREMIUM** — Unlock full access 👇\n\n"
        "Get all trending videos, leaks & premium channels.\n\n"
        "👇 Select plan to continue:"
    )
    keyboard = [
        [InlineKeyboardButton("⚡ Daily Access — 24 Hours (Ksh 20)", callback_data="buy_20")],
        [InlineKeyboardButton("« Back to Channels", callback_data="back")]
    ]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "buy_20":
        msg = (
            f"👑 Confirm Your Plan\n\n"
            f"• Plan: {PLAN['name']}\n"
            f"• Duration: {PLAN['duration']}\n"
            f"• Amount: Ksh {PLAN['price']}\n\n"
            f"Enter your M-Pesa phone number to receive the payment prompt.\n\n"
            f"Format: 0712345678 or 0110000000"
        )
        keyboard = [[InlineKeyboardButton("« Back", callback_data="back_plans")]]
        await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await query.edit_message_text("🔥 **ANYTHING TRENDY PREMIUM** — Unlock full access 👇\n\n👇 Select plan:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⚡ Daily Access — 24 Hours (Ksh 20)", callback_data="buy_20")]]), parse_mode="Markdown")

async def handle_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw = update.message.text.strip()
    phone = re.sub(r"\D", "", raw)
    if not re.match(r"^(07|01)\d{8}$", phone):
        await update.message.reply_text("❌ Invalid. Send like: 0712345678")
        return
    phone254 = "254" + phone[1:]
    await update.message.reply_text(f"⏳ Sending STK Push of Ksh {PLAN['price']} to {phone}...\nCheck your phone!")

    ok = stk_push(phone254, PLAN['price'], update.effective_user.id)
    if ok:
        await update.message.reply_text("✅ STK sent! Enter M-Pesa PIN. I will unlock after payment.")
    else:
        # Fallback while waiting Safaricom email
        await update.message.reply_text(
            f"📱 **Pay Manually (Safaricom pending approval)**\n\n"
            f"Till: **{TILL_NUMBER}**\n"
            f"Amount: **Ksh {PLAN['price']}**\n\n"
            f"Lipa na M-Pesa > Buy Goods > Till {TILL_NUMBER} > Ksh 20\n"
            f"Then send your M-Pesa code here to unlock.\n\n"
            f"STK auto will work once Safaricom approves email."
        )

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

def run_bot():
    app_builder = ApplicationBuilder().token(BOT_TOKEN).build()
    app_builder.add_handler(CommandHandler("start", start))
    app_builder.add_handler(CallbackQueryHandler(button_click))
    app_builder.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_phone))
    print("Bot running - 20KSH plan active")
    app_builder.run_polling()

if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    run_bot()
