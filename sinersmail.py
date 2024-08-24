import telebot
from telebot import types
import sqlite3
from datetime import datetime, timedelta
import requests
import certifi
from decimal import Decimal
import telebot
import requests
from bs4 import BeautifulSoup
import re 
bot_token = "7388880847:AAEZKcyZazOgoCydK3tfMpxUC4u3PsDcMC8"
Crypto_Pay_API_Token = "252897:AACv7Wi56fKGb3ik0SKvMWOay6a4IaVaNqs"

def generate_payment_link(payment_system, amount):
    api_url = "https://pay.crypt.bot/api/createInvoice"
    headers = {"Crypto-Pay-API-Token": Crypto_Pay_API_Token}
    data = {
        "asset": payment_system,
        "amount": float(amount)
    }

    response = requests.post(api_url, headers=headers, json=data)
    if response.status_code == 200:
        json_data = response.json()
        invoice = json_data.get("result")
        payment_link = invoice.get("pay_url")
        invoice_id = invoice.get("invoice_id")
        return payment_link, invoice_id
    else:
        return None, None

def get_invoice_status(invoice_id):
    api_url = f"https://pay.crypt.bot/api/getInvoices?invoice_ids={invoice_id}"
    headers = {"Crypto-Pay-API-Token": Crypto_Pay_API_Token}

    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        json_data = response.json()
        if json_data.get("ok"):
            invoices = json_data.get("result")
            if invoices and 'items' in invoices and invoices['items']:
                status = invoices['items'][0]['status']
                payment_link = invoices['items'][0]['pay_url']
                amount = Decimal(invoices['items'][0]['amount'])
                return status, payment_link, amount

    return None, None, None

def get_exchange_rates():
    api_url = "https://pay.crypt.bot/api/getExchangeRates"
    headers = {"Crypto-Pay-API-Token": Crypto_Pay_API_Token}

    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        json_data = response.json()
        if json_data.get("ok"):
            return json_data["result"]
    return []

def convert_to_crypto(amount, asset):
    rates = get_exchange_rates()
    rate = None
    for exchange_rate in rates:
        if exchange_rate["source"] == asset and exchange_rate["target"] == 'USD':
            rate = Decimal(str(exchange_rate["rate"]))
            break

    if rate is None:
        raise ValueError(f"☄️Не удалось найти курс обмена для {asset}")

    amount = Decimal(str(amount))
    return amount / rate

bot = telebot.TeleBot('7388880847:AAEZKcyZazOgoCydK3tfMpxUC4u3PsDcMC8', parse_mode='HTML')
admin_id = 7162072206
log_chat_id = 7162072206

def start_cmd(message):
  register = check_user(message.chat.id)
  if not register:
    markup = types.InlineKeyboardMarkup()
    continue_button = types.InlineKeyboardButton("✅ Продолжить",
                                                 callback_data='continue')
    markup.add(continue_button)
    with open('had.jpg', 'rb') as had:
      bot.send_photo(message.chat.id,
                     had,
                     '<b>☄️Приветствуем вас в SinersMail Bot!',
                     parse_mode='HTML',
                     reply_markup=markup)






def create_database():
  conn = sqlite3.connect('database.db')
  cursor = conn.cursor()

  # Создание таблицы users, если она ещё не существует
  cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            user_id INTEGER UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

  cursor.execute('''
    CREATE TABLE IF NOT EXISTS subscriptions (
        user_id INTEGER PRIMARY KEY,
        expiration_date DATETIME
    );
    ''')

  conn.commit()
  conn.close()


create_database()




def add_subscription(user_id, expiration_date):
  conn = sqlite3.connect('database.db')
  cursor = conn.cursor()

  cursor.execute(
      "INSERT OR REPLACE INTO subscriptions (user_id, expiration_date) VALUES (?, ?)",
      (user_id, expiration_date))
  conn.commit()
  conn.close()


# Функция для проверки статуса подписки
def check_subscription_status(user_id):
  conn = sqlite3.connect('database.db')
  cursor = conn.cursor()

  cursor.execute("SELECT expiration_date FROM subscriptions WHERE user_id=?",
                 (user_id, ))
  subscription = cursor.fetchone()

  if subscription:
    expiration_date = subscription[0]
    date = datetime.strptime(expiration_date, '%Y-%m-%d %H:%M:%S.%f')
    current_date = datetime.now()

    if current_date <= date:
      days_left = (date - current_date).days
      status = f"<b>☄️У вас присутствует активная подписка\n☄️У вас осталось {days_left} дней\n=============================\n🆔 ID: {user_id}\n=============================\n⚙️Админ: @platonov_scm \n❤️Наш канал: @SinersMail \n❤️Приятного пользования</b>"
    else:
      status = f"<b>☄️У вас истекла подписка.\n☄️\n=============================\n🆔 ID: {user_id}\n=============================\n⚙️Админ: @platonov_scm \n☄️Наш канал: @SinersMail \n❤️Приятного пользования </b>"
  else:
    status = f"<b>☄️У вас отсутствует подписка.\n☄️\n=============================\n🆔 ID: {user_id}\n=============================\n⚙️Админ: @platonov_scm \n☄️Наш канал: @SinersMail \n❤️Приятного пользования </b>"

  conn.close()
  return status


def check_subscription(user_id):
  conn = sqlite3.connect('database.db')
  cursor = conn.cursor()

  cursor.execute("SELECT expiration_date FROM subscriptions WHERE user_id=?",
                 (user_id, ))
  subscription = cursor.fetchone()
  conn.close()

  if subscription:
    expiration_date = subscription[0]
    date = datetime.strptime(expiration_date, '%Y-%m-%d %H:%M:%S.%f')
    current_date = datetime.now()

    if current_date <= date:
      return True
    else:
      return False
  else:
    return False


del_markup = types.InlineKeyboardMarkup(row_width=2)
del_button = types.InlineKeyboardButton("☄️Назад", callback_data="del")
del_markup.add(del_button)

back_markup = types.InlineKeyboardMarkup(row_width=2)
back_button = types.InlineKeyboardButton("☄️Назад", callback_data="del")
back_markup.add(back_button)


@bot.message_handler(commands=['admin'])
def admin_cmd(message):
  if message.chat.id == admin_id:
    markup = types.InlineKeyboardMarkup()
    send_sub = types.InlineKeyboardButton("☄️Выдать подписку",callback_data='send_sub')
    send_message = types.InlineKeyboardButton("☄️Сделать рассылку",callback_data='send_message2')
    usercounts = types.InlineKeyboardButton("📊Статистика",callback_data='usercounts')

    markup.add(send_sub,send_message,usercounts)
    with open('had.jpg', 'rb') as had:
      bot.send_photo(chat_id=message.chat.id,
                     photo=had,
                     caption='<b>☄️Админ-меню: </b>',
                     reply_markup=markup)
  else:
    with open('had.jpg', 'rb') as had:
      bot.send_photo(chat_id=message.chat.id,
                     photo=had,
                     caption='<b>❌ Я не понимаю вас.</b>')
      







@bot.message_handler(commands=['start'])
def home(message):
    start_cmd(message)

    user_id = message.from_user.id

    channel_id1 = -1002231663863

    user_status1 = bot.get_chat_member(channel_id1, user_id).status

    if (user_status1 in ["member", "administrator", "creator"]):
        if check_subscription(message.chat.id) == True:
            markup = types.InlineKeyboardMarkup(row_width=2)
            cabinet = types.InlineKeyboardButton("🎩Профиль", callback_data='cabinet')
            send_mail = types.InlineKeyboardButton("✉️Отправить письмо", callback_data='send_mail')
            pars = types.InlineKeyboardButton("🔍парсер почт", callback_data='parser_em')
            subb = types.InlineKeyboardButton("🥼Подписка", callback_data='sub')
            markup.add( cabinet, send_mail,pars,subb)
            with open('had.jpg', 'rb') as had:
                bot.send_photo(
                    chat_id=message.chat.id,
                    photo=had,
                    caption='''<b>☄️Главное меню:
                    👋наш канал - @sinersmail
                    ⚙️админ - @platonov_scm
                    
                      </b>''',
                    reply_markup=markup)
        else:
            markup = types.InlineKeyboardMarkup()
            cabinet = types.InlineKeyboardButton("🎩Профиль", callback_data='cabinet')
            subb = types.InlineKeyboardButton("🥼Подписка", callback_data='sub')
            markup.add(cabinet,subb)
            with open('had.jpg', 'rb') as had:
                bot.send_photo(chat_id=message.chat.id,
                                photo=had,
                                caption='<b>Главное меню </b>',
                                reply_markup=markup)
    else:
        url = types.InlineKeyboardMarkup(row_width=3)
        url_b = types.InlineKeyboardButton("☄️sinersmail", url=f"https://t.me/+tu9FoKV9mS43MDRi")
        url_c = types.InlineKeyboardButton("☄️amolzz1k", url=f"https://t.me/amolzz1k")

        url.add(url_b, url_c)

        bot.send_message(message.chat.id, "☄️Что бы использовать <b>функционал</b> бота, вы должны быть <b>подписаны</b> на <b>официальные</b> ресурсы <b>бота</b>!\n\nПосле подписки <b>используйте</b> команду /start заново!", reply_markup=url, parse_mode='html')


@bot.callback_query_handler(func=lambda call: call.data == 'parser_em')
def parser_em(call):
    if call.data == 'parser_em':
      bot.send_message(call.message.chat.id,"☄️для парсинга почт команда для парсинга /parser")
   
   
@bot.message_handler(commands=['parser'])
def parser_email(message):
  bot.send_message(
      message.chat.id,
      "<b>☄️Функция парсинга почт по ключевым словам\nпример: суды Киев\nпример: суды Саратов\nпример: суды Новосибирск\nВведите поисковой запрос для парсинга почты:</b>",
      parse_mode='HTML')

@bot.message_handler(func=lambda message: True)
def parser_email(message):
  # Получаем текст запроса
  search_query = message.text  # Получаем текст запроса
  # Формируем URL-адрес для поиска в Google
  url = f"https://www.google.com/search?q=почты {search_query}"
  # Отправляем GET-запрос на Google
  response = requests.get(url)
  # Получаем содержимое страницы
  page_content = response.text
  # Создаем объект BeautifulSoup для парсинга HTML
  soup = BeautifulSoup(page_content, 'html.parser')
  # Находим все текстовые узлы на странице
  text_nodes = soup.find_all(text=True)
  # Ищем почтовые адреса с помощью регулярного выражения
  email_pattern = r'[\w\.-]+@[\w\.-]+'
  email_addresses = re.findall(email_pattern, ' '.join(text_nodes))
  # Фильтруем почтовые адреса, убираем точки в конце домена
  filtered_emails = [
      email.split('@')[0] + '@' + email.split('@')[-1].rstrip('.')
      for email in email_addresses if '.' in email.split('@')[-1]
  ]
  bot.send_message(
      message.chat.id,
      "<b>☄️Найдены следующие электронные почты по вашему запросу:</b>\n" +
      "<pre>" + ','.join(filtered_emails) + "</pre>",
      parse_mode='HTML')

def check_user(user_id):
  conn = sqlite3.connect('database.db')
  cursor = conn.cursor()

  cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id, ))
  existing_user = cursor.fetchone()

  if existing_user:
    return True
  else:
    cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id, ))
    conn.commit()
    send_log(
        f'<b>🔔 Зарегистрирован новый <a href="tg://openmessage?user_id={user_id}">пользователь</a>\bID: </b><code>{user_id}</code>')
  conn.close()
  return False

@bot.callback_query_handler(func=lambda call: call.data == 'sub')
def cabinet(call):
    user_id = call.message.chat.id
    status = check_subscription_status(user_id)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("💸 Приобрести подписку", callback_data="buy_subscription"))
    markup.add(types.InlineKeyboardButton(text="Назад", callback_data="home"))
    bot.edit_message_caption(chat_id=user_id, message_id=call.message.message_id, caption=status, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'cabinet')
def cabinet(call):
    user_id = call.message.chat.id
    status = check_subscription_status(user_id)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="Назад", callback_data=" home"))
    bot.edit_message_caption(chat_id=user_id, message_id=call.message.message_id, caption=status, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'buy_subscription')
def buy_subscription(call):
    markup = types.InlineKeyboardMarkup()
    subscription_options = [
        ("☄️15 дней - 0.5$", "buy_15"),
        ("☄️1 месяц - 1$", "buy_30"),
        ("☄️2 месяца - 2$", "buy_60"),
        ("☄️3 месяца - 3$", "buy_90"),
        ("☄️Lifetime - 5$", "buy_lifetime") 
    ]
    for option_text, callback_data in subscription_options:
        markup.add(types.InlineKeyboardButton(option_text, callback_data=callback_data))
    bot.edit_message_caption("⌛️Выберите срок подписки:", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('buy_'))
def subscription_duration_selected(call):
    duration = call.data
    markup = types.InlineKeyboardMarkup()
    currency_options = [
        ("💵 USDT", "currency_USDT_" + duration),
        ("💎 TON", "currency_TON_" + duration),
        ("🪙 BTC", "currency_BTC_" + duration),
        ("💶 ETH", "currency_ETH_" + duration)
    ]
    for option_text, callback_data in currency_options:
        markup.add(types.InlineKeyboardButton(option_text, callback_data=callback_data))
    bot.edit_message_caption("💸Выберите валюту для оплаты:", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('currency_'))
def currency_selected(call):
    parts = call.data.split('_')
    currency = parts[1]
    duration_parts = parts[2:]
    duration = "_".join(duration_parts)

    amount = get_amount_by_duration(duration.replace('buy_', ''))
    
    try:
        print(amount, currency)
        converted_amount = convert_to_crypto(amount, currency)
        payment_link, invoice_id = generate_payment_link(currency, converted_amount)
        if payment_link and invoice_id:
            markup = types.InlineKeyboardMarkup()
            check_payment_button = types.InlineKeyboardButton("💸Проверить оплату", callback_data=f"check_payment:{call.from_user.id}:{invoice_id}")
            markup.add(check_payment_button)
            
            bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                                  caption=f"💸Счет для оплаты: {payment_link}", reply_markup=markup)
        else:
            bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                                  caption="❌Не удалось создать счет для оплаты. Пожалуйста, попробуйте позже.")
    except ValueError as e:
        bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                              caption=str(e))

def get_amount_by_duration(duration):
    prices = {
        '15': 0.5,
        '30': 1,
        '60': 2,
        '90': 3,
        'lifetime': 5
    }
    return prices.get(duration, 0)

@bot.callback_query_handler(func=lambda call: call.data.startswith('check_payment:'))
def check_payment(call):
    _, user_id_str, invoice_id_str = call.data.split(':')
    user_id = int(user_id_str)
    invoice_id = invoice_id_str

    if user_id == call.from_user.id:
        status, payment_link, amount = get_invoice_status(invoice_id)
        
        if status == "paid":
            duration_days = get_duration_by_amount(amount)
            expiration_date = datetime.now() + timedelta(days=duration_days)
            add_subscription(user_id, expiration_date)

            bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                                  caption="✅Оплата подтверждена. Подписка активирована. Спасибо за покупку.")
        else:
            bot.answer_callback_query(call.id, "❌Оплата не найдена. Пожалуйста, проверьте позже или свяжитесь с поддержкой.")
    else:
        bot.answer_callback_query(call.id, "❌Вы не можете проверить эту оплату.", show_alert=True)

def get_duration_by_amount(amount):
    amount = round(amount, 2)
    if amount <= 0.5:
        return 7
    elif amount <= 1:
        return 15
    elif amount <= 2:
        return 30
    elif amount <= 4:
        return 60
    elif amount <= 6:
        return 90
    elif amount >= 25:
        return 365 * 99
    else:
        return 0

@bot.callback_query_handler(func=lambda call: True)
def handle_inline_button_click(call):
  user_id = call.message.chat.id
  if call.data == 'send_sub':
    bot.edit_message_caption(
        chat_id=user_id,
        message_id=call.message.id,
        caption='<b>✍Укажите ID пользователя и кол-во дней через пробел:</b>')
    bot.register_next_step_handler(call.message, give_sub)
  elif call.data == 'my_sub':
    with open('had.jpg', 'rb') as had:
      bot.send_photo(user_id,
                     had,
                     check_subscription_status(user_id),
                     reply_markup=del_markup)
  elif call.data == 'del':
    home(call.message)
    bot.delete_message(call.message.chat.id, call.message.id)
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
  elif call.data == 'back':
    home(call.message)
    bot.delete_message(call.message.chat.id, call.message.id)
  elif call.data == 'send_mail':
    bot.edit_message_caption(chat_id=user_id,
                             message_id=call.message.id,
                             caption='<b>☄️Укажи тему вашего письма: </b>')
    bot.register_next_step_handler(call.message, sm, call.message.id)
  elif call.data == 'send_message2':
    sent_message = bot.reply_to(call.message, "☄️Введите сообщение для отправки пользователям:")
    bot.register_next_step_handler(sent_message, process_sent_message)
  elif call.data == 'usercounts':
    total_users, subscribed_users = get_user_counts()
    bot.reply_to(call.message, f'<b>📊 MistMail  stats📊\n📊Количество пользователей: {total_users}\n📊Пользователи с подпиской: {subscribed_users}</b>')



def get_user_counts():
    # Create a new connection and cursor within the function
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Get total user count
    cursor.execute('SELECT COUNT(*) FROM users')
    total_users = cursor.fetchone()[0]

    # Get subscribed user count
    cursor.execute('SELECT COUNT(*) FROM subscriptions')
    subscribed_users = cursor.fetchone()[0]

    # Close the connection
    conn.close()

    return total_users, subscribed_users

def sm(message, ms):
    if message.text:
        title = message.text
        bot.edit_message_caption(
            chat_id=message.chat.id,
            message_id=ms,
            caption='<b>☄️Укажите текст вашего письма: </b>')
        bot.register_next_step_handler(message, sm1, title, ms)
        bot.delete_message(message.chat.id, message.message_id)  # Удаляем сообщение пользователя
    else:
        bot.edit_message_caption(chat_id=message.chat.id,
                                 message_id=ms,
                                 caption='<b>❌ Только текстом.</b>')

def sm1(message, title, ms):
    if message.text:
        text = message.text
        bot.edit_message_caption(
            chat_id=message.chat.id,
            message_id=ms,
            caption=
            '<b>☄️Укажи отправителя сообщения: \nпримеры отправителей \n- test@sinersmail.ru\n- test@gmail.ru \n- test@gmail.com \n- test@mvd.gov \n домены почты можно писать любые даже @anime.ru \n(любой который вам захочется)</b>'
        )
        bot.register_next_step_handler(message, sm2, title, text, ms)
        bot.delete_m
