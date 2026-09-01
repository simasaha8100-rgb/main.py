import telebot
import json
import os
import random
import threading
from flask import Flask
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime

BOT_TOKEN = 8829932703:AAFBf5Lle1hAoTYhYC8rQGvs2baqOHbh2sI
 # ⚠️ Ekhane new token bosao
ADMIN_ID = 6384181929 # ⚠️ Tomar Telegram ID ( @userinfobot )

DB_FILE = "users.json"
TASK_FILE = "task.json"

if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f: json.dump({}, f)
if not os.path.exists(TASK_FILE):
    with open(TASK_FILE, "w") as f: json.dump({"link": "https://youtube.com/shorts/defaultlink"}, f)

app = Flask(__name__)
@app.route('/')
def home(): return "✅ Bot is Live & Running!"
def keep_alive(): threading.Thread(target=lambda: app.run(host="0.0.0.0", port=8080)).start()

bot = telebot.TeleBot(BOT_TOKEN)

def load_users():
    with open(DB_FILE, "r") as f: return json.load(f)
def save_users(d):
    with open(DB_FILE, "w") as f: json.dump(d, f, indent=2)
def load_task():
    with open(TASK_FILE, "r") as f: return json.load(f)
def save_task(d):
    with open(TASK_FILE, "w") as f: json.dump(d, f, indent=2)

def get_user(uid):
    users = load_users()
    uid = str(uid)
    if uid not in users:
        users[uid] = {
            "balance": 0, "spins": 0,
            "claimed_task": False, "can_claim": False,
            "temp_reward": 0, "history": []
        }
        save_users(users)
    return users

def add_history(uid, text):
    users = load_users()
    time = datetime.now().strftime("%d/%m %H:%M")
    users[str(uid)]["history"].append(f"{text} | {time}")
    # Sudhu last 20 ta rakhbo
    users[str(uid)]["history"] = users[str(uid)]["history"][-20:]
    save_users(users)

# 👮‍♂️ ADMIN: /addtask link
@bot.message_handler(commands=['addtask'])
def add_task(message):
    if message.from_user.id!= ADMIN_ID:
        bot.reply_to(message, "❌ Tumi admin na! 🙏"); return
    try:
        link = message.text.split(" ", 1)[1]
        save_task({"link": link})
        users = load_users()
        for u in users: users[u]["claimed_task"] = False
        save_users(users)
        bot.reply_to(message, f"✅ **Task Update Success!** 🎉\n\n🔗 New Link: {link}\n♻️ Sobar task reset hoye geche!", parse_mode="Markdown")
    except:
        bot.reply_to(message, "⚠️ **Use:** `/addtask https://youtube.com/shorts/xxx`", parse_mode="Markdown")

@bot.message_handler(commands=['start'])
def start(message):
    get_user(message.from_user.id)
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🎡 Spin & Earn 💸", callback_data="spin"),
        InlineKeyboardButton("🎬 Task 50₹ 🎥", callback_data="task"),
        InlineKeyboardButton("💰 Balance 💵", callback_data="balance"),
        InlineKeyboardButton("📜 History 📋", callback_data="history"),
        InlineKeyboardButton("🏦 Withdraw 💳", callback_data="withdraw")
    )
    bot.send_message(message.chat.id, f"👋 **Hello {message.from_user.first_name}!** 🙏\n\n🎡 **Spin koro** - Taka jito! 💰\n🎬 **Task koro** - 50₹ nao! 🎥\n📜 **History dekho** - Sob hisab! 📋\n🏦 **100₹ holei Withdraw!** 💳", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    uid = str(call.from_user.id)
    users = load_users()
    if uid not in users: get_user(uid); users = load_users()
    user = users[uid]
    task = load_task()

    if call.data == "spin":
        if user.get("can_claim", False):
            bot.answer_callback_query(call.id, "⚠️ Age Claim koro! 👆", show_alert=True); return
        reward = random.choice([2, 5, 10, 15, 20]) # Loss komanor jonno reward komalam
        user["balance"] += reward; user["spins"] += 1
        user["can_claim"] = True; user["temp_reward"] = reward
        save_users(users)
        add_history(uid, f"🎡 Spin Win: +{reward}₹")
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton(f"✅ {reward}₹ Claim Koro 🎁", callback_data="claim"))
        bot.edit_message_text(f"🎉 **Wow! You Won {reward}₹!** 💸\n\n👇 Niche click kore claim koro!", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == "claim":
        if not user.get("can_claim", False):
            bot.answer_callback_query(call.id, "❌ Already Claimed! 😅", show_alert=True); return
        reward = user.get("temp_reward", 0)
        user["can_claim"] = False; user["temp_reward"] = 0; save_users(users)
        bot.answer_callback_query(call.id, f"✅ {reward}₹ Added to Balance! 💰", show_alert=True)
        bot.edit_message_text(f"✅ **{reward}₹ Balance e add hoye geche!** 🥳", call.message.chat.id, call.message.message_id)

    elif call.data == "balance":
        bot.answer_callback_query(call.id, f"💰 Balance: {user['balance']}₹ 💵", show_alert=True)

    elif call.data == "history":
        hist = user.get("history", [])
        if not hist:
            text = "📜 **History Khali!** 😴\n\nSpin ba
