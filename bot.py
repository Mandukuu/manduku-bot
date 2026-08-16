import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is Live!"

@app.route('/mpesa_callback', methods=['POST'])
def mpesa_callback():
    print("M-Pesa callback received")
    return {"ResultCode": 0, "ResultDesc": "Accepted"}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 Anything Trendy Bot is ONLINE!\nSend /products to shop\nTill: 1611583")

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

def run_bot():
    if not BOT_TOKEN:
        print("ERROR: BOT_TOKEN not set!")
        return
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    print("Telegram bot polling started...")
    application.run_polling()

if __name__ == '__main__':
    threading.Thread(target=run_flask).start()
    run_bot()
