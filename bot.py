import os, requests, base64
from datetime import datetime
from threading import Thread
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CONSUMER_KEY = os.getenv("CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")
SHORTCODE = os.getenv("SHORTCODE", "174379")
PASSKEY = os.getenv("PASSKEY")
CALLBACK_URL = os.getenv("CALLBACK_URL", "https://example.com/mpesa/callback")
CHANNEL_ID = os.getenv("CHANNEL_ID")
AMOUNT = os.getenv("AMOUNT", "10")

app = Flask(__name__)
pending = {}

def clean_phone(phone):
    phone = str(phone).strip().replace(" ", "").replace("+", "")
    if phone.startswith("0"):
        phone = "254" + phone[1:]
    if phone.startswith("7") or phone.startswith("1"):
        phone = "254" + phone
    return phone

def get_token():
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    r = requests.get(url, auth=(CONSUMER_KEY, CONSUMER_SECRET))
    print("TOKEN:", r.text)
    return r.json().get("access_token")

def send_stk(phone, amount, account_ref):
    phone = clean_phone(phone)
    print(f"SENDING STK TO {phone}")
    token = get_token()
    if not token:
        return {"error": "No token"}
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    password = base64.b64encode(f"{SHORTCODE}{PASSKEY}{timestamp}".encode()).decode()
    payload = {
        "BusinessShortCode": SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(amount),
        "PartyA": phone,
        "PartyB": SHORTCODE,
        "PhoneNumber": phone,
        "CallBackURL": CALLBACK_URL,
        "AccountReference": account_ref,
        "TransactionDesc": "Join fee"
    }
    headers = {"Authorization": f"Bearer {token}"}
    url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    r = requests.post(url, json=payload, headers=headers)
    print("STK RESPONSE:", r.text)
    return r.json()

@app.route("/mpesa/callback", methods=["POST"])
def mpesa_callback():
    data = request.get_json()
    print("CALLBACK:", data)
    return jsonify({"ResultCode": 0})

def run_flask():
    app.run(host="0.0.0.0", port=5000)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Karibu! Fee is {AMOUNT} KES.\nSend /join to pay.")

async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Type your M-Pesa number:\nExample: 0712345678")

async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text.strip()
    chat_id = update.message.chat_id
    await update.message.reply_text(f"Sending STK to {phone}...")
    resp = send_stk(phone, AMOUNT, f"TG_{chat_id}")
    if "CheckoutRequestID" in str(resp):
        await update.message.reply_text("✅ STK Sent! Check phone.")
    else:
        await update.message.reply_text(f"❌ Failed:\n{resp}")

if __name__ == "__main__":
    Thread(target=run_flask, daemon=True).start()
    print("Bot is running...")
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("join", join))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, contact_handler))
    application.run_polling()
