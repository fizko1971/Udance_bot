import os
import json
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from oauth2client.service_account import ServiceAccountCredentials
import gspread
print("TOKEN:", os.getenv("TELEGRAM_TOKEN"))
bot = telebot.TeleBot(os.getenv("TELEGRAM_TOKEN"))

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_dict(
    json.loads(os.getenv("credentials.json")), scope)
client = gspread.authorize(creds)

SPREADSHEET_ID = os.getenv("GOOGLE_SHEET_ID")
sheet = client.open_by_key(SPREADSHEET_ID).worksheet("Udance25_26")

user_data = {}

events_list = [
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

def generate_event_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    buttons = [InlineKeyboardButton(text=e, callback_data=f"event_{i}") for i, e in enumerate(events_list)]
    done = InlineKeyboardButton("✅ Завершити вибір", callback_data="done")
    keyboard.add(*buttons)
    keyboard.add(done)
    return keyboard

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user_data[chat_id] = {'events': []}
    bot.send_message(chat_id, "🎉 Вітаю! Оберіть події, в яких плануєте участь:", reply_markup=generate_event_keyboard())

@bot.callback_query_handler(func=lambda call: call.data.startswith("event_") or call.data == "done")
def handle_event_selection(call):
    chat_id = call.message.chat.id
    if call.data == "done":
        bot.send_message(chat_id, "✍️ Скільки команд плануєте зареєструвати?")
        bot.register_next_step_handler(call.message, get_teams)
        return

    index = int(call.data.split("_")[1])
    event = events_list[index]
    if event not in user_data[chat_id]['events']:
        user_data[chat_id]['events'].append(event)
        bot.answer_callback_query(call.id, text=f"Додано: {event}")
    else:
        bot.answer_callback_query(call.id, text="Вже обрано")

def get_teams(message):
    chat_id = message.chat.id
    user_data[chat_id]['teams'] = message.text
    bot.send_message(chat_id, "👥 Орієнтовна кількість учасників?")
    bot.register_next_step_handler(message, get_participants)

def get_participants(message):
    chat_id = message.chat.id
    user_data[chat_id]['participants'] = message.text
    bot.send_message(chat_id, "🏙 Ваше місто:")
    bot.register_next_step_handler(message, get_city)

def get_city(message):
    chat_id = message.chat.id
    user_data[chat_id]['city'] = message.text
    bot.send_message(chat_id, "🏫 Назва студії:")
    bot.register_next_step_handler(message, get_studio)

def get_studio(message):
    chat_id = message.chat.id
    user_data[chat_id]['studio'] = message.text
    bot.send_message(chat_id, "👤 Ваше ПІБ:")
    bot.register_next_step_handler(message, get_name)

def get_name(message):
    chat_id = message.chat.id
    user_data[chat_id]['name'] = message.text
    bot.send_message(chat_id, "📞 Телефон (Telegram / WhatsApp):")
    bot.register_next_step_handler(message, get_phone)

def get_phone(message):
    chat_id = message.chat.id
    user_data[chat_id]['phone'] = message.text
    bot.send_message(chat_id, "📸 Instagram:")
    bot.register_next_step_handler(message, get_instagram)

def get_instagram(message):
    chat_id = message.chat.id
    user_data[chat_id]['instagram'] = message.text
    bot.send_message(chat_id, "📧 Email:")
    bot.register_next_step_handler(message, get_email)

def get_email(message):
    chat_id = message.chat.id
    user_data[chat_id]['email'] = message.text
    promo = str(chat_id)[-6:]
    user_data[chat_id]['promo'] = promo

    sheet.append_row([
        ", ".join(user_data[chat_id]['events']),
        user_data[chat_id]['studio'],
        user_data[chat_id]['city'],
        user_data[chat_id]['participants'],
        user_data[chat_id]['teams'],
        user_data[chat_id]['name'],
        user_data[chat_id]['phone'],
        user_data[chat_id]['instagram'],
        user_data[chat_id]['email'],
        promo
    ])

    bot.send_message(chat_id, f"""✅ Дані надіслані!
🗓 Події: {", ".join(user_data[chat_id]['events'])}
🏫 Студія: {user_data[chat_id]['studio']}
🏙 Місто: {user_data[chat_id]['city']}
👥 Учасників: {user_data[chat_id]['participants']}
👯‍♀️ Команди: {user_data[chat_id]['teams']}
👤 ПІБ: {user_data[chat_id]['name']}
📞 Телефон: {user_data[chat_id]['phone']}
📸 Instagram: {user_data[chat_id]['instagram']}
📧 Email: {user_data[chat_id]['email']}
🎁 Промокод: `{promo}`""", parse_mode="Markdown")

bot.infinity_polling()
