import telebot
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import random

load_dotenv("udance_bot/config.env")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
import json
creds = ServiceAccountCredentials.from_json_keyfile_dict(
    json.loads(os.getenv("GOOGLE_CREDS")), scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(GOOGLE_SHEET_ID).worksheet("Udance25_26")

ADMIN_ID = os.getenv("ADMIN_ID")

EVENTS = [
    "18-19.10.2025 Global Talent Lviv 2025",
    "9.11.2025 Global Talent Odesa 2025",
    "15.11.2025 Global Talent Cherkasy 2025",
    "22.11.2025 Global Talent Chernivtsi 2025",
    "23.11.2025 World of Dance Ukraine 2025",
    "7.12.2025 Global Talent Zaporizhzhia 2025",
    "13-14.12.2025 Feel the Beat",
    "14.02.2026 Global Talent Ivano -Frankivsk 2026",
    "15.02.2026 Global Talent Kropyvnytskyi 2026",
    "21.02.2026 Global Talent Khmelnytskyi 2026",
    "01.03.2026 Global Talent Ukraine Mykolaiv 2026",
    "07.03.2026 Global Talent Chernigiv 2026",
    "08.03.2026 Global Talent Vinnytsya 2026",
    "20-22.03.2026 Global Talent Lviv 2026",
    "28.03.2026 Global Talent Kyiv 2026",
    "29.03.2026 World of Dance Kyiv Solo 2026",
    "04-05.04.2026 Global Talent Zaporizhzhia 2026",
    "18.04.2026 Global Talent Rivne 2026",
    "26.04.2026 World of Dance Lviv 2026",
    "10.05.2026 Global Talent Dnipro 2026",
    "23.05.2026 Global Talent Ternopil 2026",
    "30-31.05.2026 Global Talent Superfinal 2025"
]

user_data = {}

@bot.message_handler(commands=["start"])
def start(message):
    chat_id = message.chat.id
    user_data[chat_id] = {"events": []}
    markup = InlineKeyboardMarkup(row_width=1)
    for event in EVENTS:
        markup.add(InlineKeyboardButton(event, callback_data=event))
    markup.add(InlineKeyboardButton("✅ Завершити вибір", callback_data="done"))
    bot.send_message(chat_id, "🗓️ Оберіть одну або декілька подій:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_event_selection(call):
    chat_id = call.message.chat.id
    if call.data == "done":
        bot.send_message(chat_id, "💃 Скільки танцювальних команд ви плануєте зареєструвати?")
        bot.register_next_step_handler(call.message, ask_teams)
    else:
        if call.data not in user_data[chat_id]["events"]:
            user_data[chat_id]["events"].append(call.data)
        bot.answer_callback_query(call.id, f"✅ Обрано: {call.data}")

def ask_teams(message):
    chat_id = message.chat.id
    user_data[chat_id]["teams"] = message.text
    bot.send_message(chat_id, "👥 Орієнтовна кількість учасників:")
    bot.register_next_step_handler(message, ask_participants)

def ask_participants(message):
    chat_id = message.chat.id
    user_data[chat_id]["participants"] = message.text
    bot.send_message(chat_id, "🏙️ Ваше місто:")
    bot.register_next_step_handler(message, ask_city)

def ask_city(message):
    chat_id = message.chat.id
    user_data[chat_id]["city"] = message.text
    bot.send_message(chat_id, "🏫 Назва студії:")
    bot.register_next_step_handler(message, ask_studio)

def ask_studio(message):
    chat_id = message.chat.id
    user_data[chat_id]["studio"] = message.text
    bot.send_message(chat_id, "👤 Ваше ПІБ:")
    bot.register_next_step_handler(message, ask_name)

def ask_name(message):
    chat_id = message.chat.id
    user_data[chat_id]["name"] = message.text
    bot.send_message(chat_id, "📞 Телефон (Telegram, WhatsApp):")
    bot.register_next_step_handler(message, ask_phone)

def ask_phone(message):
    chat_id = message.chat.id
    user_data[chat_id]["phone"] = message.text
    bot.send_message(chat_id, "📸 Instagram:")
    bot.register_next_step_handler(message, ask_instagram)

def ask_instagram(message):
    chat_id = message.chat.id
    user_data[chat_id]["instagram"] = message.text
    bot.send_message(chat_id, "📧 Email:")
    bot.register_next_step_handler(message, finish)

def finish(message):
    chat_id = message.chat.id
    user_data[chat_id]["email"] = message.text
    promo_code = str(random.randint(100000, 999999))
    user_data[chat_id]["promo"] = promo_code
    data = user_data[chat_id]

    sheet.append_row([
        ", ".join(data["events"]),
        data["teams"],
        data["participants"],
        data["city"],
        data["studio"],
        data["name"],
        data["phone"],
        data["instagram"],
        data["email"],
        data["promo"]
    ])

    bot.send_message(chat_id, f"✅ Дані надіслані!
🎁 Ваш промокод: `{promo_code}`", parse_mode="Markdown")

    bot.send_message(ADMIN_ID, f"📥 Нова заявка від @{message.from_user.username or 'без ніка'}:
"
                                f"Події: {data['events']}
Студія: {data['studio']}
"
                                f"Місто: {data['city']}
Учасників: {data['participants']}
"
                                f"Команди: {data['teams']}
ПІБ: {data['name']}
"
                                f"Телефон: {data['phone']}
Instagram: {data['instagram']}
"
                                f"Email: {data['email']}
Промокод: {data['promo']}")

bot.infinity_polling()
