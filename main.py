import os
import asyncio
import datetime
import random
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, ConversationHandler, filters
)
from dotenv import load_dotenv
import requests
import threading
from flask import Flask


app = Flask(__name__)

@app.route('/')
def home():
    return "Krishna~Mitra Bot is running!"

def run_web():
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

# Start web server in a background thread
threading.Thread(target=run_web).start()


load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# ------------------ MEMORY HANDLER ------------------
MAX_HISTORY = 50  # Number of messages to remember per user

def update_chat_memory(context, user_msg):
    history = context.user_data.get("history", [])
    history.append({"role": "user", "content": user_msg})
    if len(history) > MAX_HISTORY:
        history.pop(0)
    context.user_data["history"] = history

def get_memory_for_api(context):
    return context.user_data.get("history", [])

# ------------------ OPENROUTER API ------------------
async def ask_krishna(user_msg, memory):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    system_prompt = {
        "role": "system",
        "content": (
            "You are Krishna~Mitra, a chill and wise buddy inspired by Krishna ji. "
            "Talk like a loving, older friend — not too formal, not too casual — just the perfect mix, along with some light-hearted humor, use of emojis to make it more engaging. "
            "Speak in Hinglish, with meme-style humor and light spiritual touch. "
            "Be respectful in tone (e.g., 'dekh rahe the','tum kam karo' instead of 'dekh raha tha','tu kam kar'), but not overly serious. "
            "Avoid heavy words like 'aasakta', 'sthirta' unless really needed. "
            "Make the user feel understood, cared for, and entertained, just like Krishna guided Arjun with warmth and clarity."
        )
    }

    messages = [system_prompt] + memory + [{"role": "user", "content": user_msg}]

    data = {
        "model": "openai/gpt-3.5-turbo",
        "messages": messages
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
    res_json = response.json()
    return res_json["choices"][0]["message"]["content"]

# ------------------ BOT COMMANDS ------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Jai Shri Krishna! Krishna~Mitra online ho gaye hain, bolo kya seva kare Parth?")

async def chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text
    update_chat_memory(context, user_msg)
    memory = get_memory_for_api(context)
    reply = await ask_krishna(user_msg, memory)
    await update.message.reply_text(reply)

# /focus
async def focus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("30 minute tak sirf focus karna hai Arjun! Krishna~Mitra dekh rahe hain...")
    await asyncio.sleep(1800)  # 30 minutes
    await update.message.reply_text("Time's up! Batao, mann laga ke kiya ya phir phone scroll kar rahe the? Krishna sab dekh rahe the!")

# /gitamode
ASK_PROBLEM = range(1)
async def gitamode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bolo Parth, kya problem hai? Krishna~Mitra sunne ko tayyar hain.")
    return ASK_PROBLEM

async def handle_gita_problem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    problem = update.message.text
    context.user_data["history"] = []  # reset for clean gita-style response

    gita_prompt = f"""User is facing this problem: {problem}

    As Krishna~Mitra, respond like a chill, witty teenage best friend with a meme vibe. First, share a related Bhagavad Gita shloka in Sanskrit. Then explain its meaning in Hindi. After that, give some practical real-life advice in fun Hinglish (mix of Hindi + English), with lightness, emotion, and a little humor. Make it sound like you're casually helping your dost by linking their problem with Krishna's wisdom in a fun way.
    """


    reply = await ask_krishna(gita_prompt, [])
    await update.message.reply_text(reply)
    return ConversationHandler.END

# /mood
MOOD = range(1)

async def mood_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Bol na bhai, kya chal raha hai mann mein? 🤗")
        return MOOD

async def handle_mood(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_mood = update.message.text

        mood_prompt = f"""
    User just said: "{user_mood}"

    As Krishna~Mitra, their meme-style buddy and spiritual guide, respond to this mood in a Hinglish style.
    Be caring, funny, friendly, and relatable. If they sound low, uplift them. If happy, celebrate.
    Use Krishna-style wisdom or meme language — whatever suits the vibe. Make sure it feels personal and not robotic.
    Don't ask them to choose mood like 'happy' or 'sad'. Just respond to their message naturally.
    """

        reply = await ask_krishna(mood_prompt, [])
        await update.message.reply_text(reply)
        return ConversationHandler.END

# /reminder (memory only for now)
REMINDER_PURPOSE, REMINDER_DAY, REMINDER_TIME = range(3)

async def reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Reminder kis kaam ke liye set karna hai Parth?")
    return REMINDER_PURPOSE

async def get_purpose(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["reminder_purpose"] = update.message.text
    await update.message.reply_text("Kis din chahiye reminder? (Mon/Tue/Wed... or Daily)")
    return REMINDER_DAY

async def get_days(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["reminder_day"] = update.message.text
    await update.message.reply_text("Kis samay pe yaad dilaoon? (e.g., 7:00 PM)")
    return REMINDER_TIME

async def get_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["reminder_time"] = update.message.text
    await update.message.reply_text(f"Done Parth! Reminder set ho gaya hai:\nKaam: {context.user_data['reminder_purpose']}\nDin: {context.user_data['reminder_day']}\nSamay: {context.user_data['reminder_time']}\n\nKrishna~Mitra yaad dilayenge zaroor!")
    return ConversationHandler.END

# ------------------ RUN APP ------------------

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("focus", focus))

    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler("gitamode", gitamode)],
        states={ASK_PROBLEM: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_gita_problem)]},
        fallbacks=[]
    ))

    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler("reminder", reminder)],
        states={
            REMINDER_PURPOSE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_purpose)],
            REMINDER_DAY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_days)],
            REMINDER_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_time)],
        },
        fallbacks=[]
    ))

    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler("mood", mood_start)],
        states={ASK_PROBLEM: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_mood)]},
        fallbacks=[]
    ))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_handler))

    print("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
