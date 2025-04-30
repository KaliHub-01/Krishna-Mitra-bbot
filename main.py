import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# Flask server to keep the bot alive
app = Flask('')

@app.route('/')
def home():
    return "Krishna~Mitra is active bro 😎"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()


# Load .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Arrey bhai! Krishna~Mitra online aa gaya, bol kya haal chaal?")

# Main chat function
async def chat_with_krishna(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are Krishna~Mitra, a meme-style Krishna bot who speaks Hinglish. "
                    "Act like a teenage best friend — full chill, spiritual gyaan with memes, reels-style replies, and never formal."
                )
            },
            {"role": "user", "content": user_msg}
        ]
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        result = response.json()

        if "choices" in result:
            reply = result['choices'][0]['message']['content']
        else:
            reply = "Arrey bhai, thoda glitch aaya hai!"

    except Exception as e:
        reply = f"Error: {str(e)}"

    await update.message.reply_text(reply)

# Run the bot
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_with_krishna))

    print("Bot is running...")
    app.run_polling()


if __name__ == '__main__':
    keep_alive()
    main()

