import os, re, json, requests, base64, threading
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CONSUMER_KEY = os.environ.get("DARAJA_CONSUMER_KEY")
CONSUMER_SECRET = os.environ.get("DARAJA_CONSUMER_SECRET")
TILL_NUMBER = "1611583"
CALLBACK_URL = os.environ.get("CALLBACK_URL", "https://manduku-bot.onrender.com/mpesa_callback")

# YOUR PLAN - Only 20 KSH
PLAN = {"name": "Anything Trendy Access", "price": 20, "duration": "24 Hours"}

USER_DATA = {}
PENDING = {}

app = Flask(__name__)

def get_token():
    try:
        url = "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        r = requests.get(url, auth=(CONSUMER_KEY, CONSUMER_SECRET))
        return r.json().get("access_token")
    except: return None

def stk_push(phone, amount, user_id):
    token = get_token()
    if not token: return False
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    shortcode = TILL_NUMBER
    passkey = os.environ.get("DARAJA_PASSKEY", "")
    password = base64.b64encode((shortcode + passkey + timestamp).encode()).decode() if passkey else ""
    
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
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
