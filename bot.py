import buttons as bt
import database as db
import telebot
from geopy import Nominatim


# Создаем объект бота
bot = telebot.TeleBot('7117428954:AAGYDL9dS7gtQghi1eujdNom65-mRKg1vQ4')
# Работа с картами
geolocator = Nominatim(user_agent='Mozilla/5.0 '
                                  '(Windows NT 10.0; Win64; x64) '
                                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                                  'Chrome/124.0.0.0 Safari/537.36')
# Временные данные
users = {}

## Сторона пользователя ##
# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(msg):
    user_id = msg.from_user.id
    check = db.check_user(user_id)
    products_from_db = db.get_all_pr()
    if check:
        bot.send_message(user_id,
                            f'Добро пожаловать, '
                            f'{msg.from_user.first_name}!\n'
                            f'Выберите пункт меню:', reply_markup=bt.pr_buttons(products_from_db))
    else:
        bot.send_message(user_id, 'Здравствуйте! Давайте начнем регистрацию!\n'
                                  'Введите свое имя!')
        # Переход на этап получения имени
        bot.register_next_step_handler(msg, get_name)


# Этап получения имени
def get_name(msg):
    user_id = msg.from_user.id
    user_name = msg.text

    bot.send_message(user_id, 'Отлично, теперь отправьте номер!',
                     reply_markup=bt.num_button())
    # Переход на этап получения номера
    bot.register_next_step_handler(msg, get_num, user_name)


# Этап получения номера
def get_num(msg, user_name):
    user_id = msg.from_user.id
    # Если пользователь отправил номер через кнопку
    if msg.contact:
        user_num = msg.contact.phone_number
        bot.send_message(user_id, 'Супер, теперь локация!',
                         reply_markup=bt.loc_button())
        # Переход на получение локации
        bot.register_next_step_handler(msg, get_loc, user_name, user_num)
    # Если пользователь отправил номер не по кнопке
    else:
        bot.send_message(user_id, 'Отправьте номер через кнопку!')
        # Возврат на этап получения номера
        bot.register_next_step_handler(msg, get_num, user_name)


# Выбор количества
@bot.callback_query_handler(lambda call: call.data in ['increment', 'decrement', 'to_cart', 'back'])
def choose_count(call):
    chat_id = call.message.chat.id
    if call.data == 'increment':
        bot.edit_message_reply_markup(chat_id=chat_id, message_id=call.message.message_id,
                                      reply_markup=bt.choose_pr_count_buttons('increment', users[chat_id]['pr_amount']))
        users[chat_id]['pr_amount'] += 1
    elif call.data == 'decrement':
        bot.edit_message_reply_markup(chat_id=chat_id, message_id=call.message.message_id,
                                      reply_markup=bt.choose_pr_count_buttons('decrement', users[chat_id]['pr_amount']))
        users[chat_id]['pr_amount'] -= 1
    elif call.data == 'to_cart':
        pr_name = db.get_exact_pr(users[chat_id]['pr_name'])[1]
        db.add_pr_to_cart(chat_id, pr_name, users[chat_id]['pr_amount'])
        bot.delete_message(chat_id=chat_id, message_id=call.message.message_id)
        bot.send_message(chat_id, 'Товар успешно помещен в корзину! Желаете что-то ещё?',
                         reply_markup=bt.pr_buttons(db.get_all_pr()))
    elif call.data == 'back':
        products_from_db = db.get_all_pr()
        bot.delete_message(chat_id=chat_id, message_id=call.message.message_id)
        bot.send_message(chat_id, 'Перенаправляю вас обратно в меню',
                         reply_markup=bt.pr_buttons(products_from_db))


# Корзина
@bot.callback_query_handler(lambda call: call.data in ['cart', 'order'])
def cart_handle(call):
    chat_id = call.message.chat.id
    user_cart = db.show_cart(chat_id)
    text = 'Ваша корзина:\n'
    total = 0
    for i in user_cart:
        text += (f'Товар: {i[1]}\n'
                 f'Количество {i[2]}\n\n')
        total += db.get_exact_price(i[1])[0] * i[2]
    text += str(total)
    if call.data == 'cart':
        bot.send_message(chat_id, text, reply_markup=bt.cart_buttons())
    elif call.data == 'order':
        text = text.replace('Ваша корзина:', 'Новый заказ!')
        info = db.make_order(chat_id)
        text += (f'Пользователь: @{call.message.chat.username}\n'
                 f'Адрес: {info[2][0]}')
        bot.send_message(-4273695435, text)
        bot.delete_message(chat_id=chat_id, message_id=call.message.message_id)
        bot.send_message(chat_id, 'Ваш заказ оформлен, с вами скоро свяжутся наши специалисты!',
                         reply_markup=bt.pr_buttons(db.get_all_pr()))


# Этап получения локации
def get_loc(msg, user_name, user_num):
    user_id = msg.from_user.id
    # Если пользователь отправил локацию через кнопку
    if msg.location:
        user_loc = geolocator.reverse(f'{msg.location.latitude},'
                                      f'{msg.location.longitude}')
        # Внесение пользователя в БД
        db.register(user_id, user_name, user_num, str(user_loc))
        bot.send_message(user_id, 'Регистрация успешно на этом пройдена!',
                         reply_markup=telebot.types.ReplyKeyboardRemove())
    # Если пользователь отправил номер не по кнопке
    else:
        bot.send_message(user_id, 'Отправьте локацию через кнопку!')
        # Возврат на этап получения локации
        bot.register_next_step_handler(msg, get_loc, user_name, user_num)


# Выбор товара и его количества
@bot.callback_query_handler(lambda call: int(call.data) in db.get_pr_id())
def choose_product(call):
    chat_id = call.message.chat.id
    users[chat_id] = {'pr_name': call.data, 'pr_amount': 1}
    bot.delete_message(chat_id=chat_id, message_id=call.message.message_id)
    pr_info = db.get_exact_pr(call.data)
    bot.send_photo(chat_id, photo=pr_info[4], caption=f'Название товара: {pr_info[1]}\n'
                                                      f'Описание товара: {pr_info[2]}\n'
                                                      f'Цена товара: {pr_info[3]}\n'
                                                      f'Количество на складе: {pr_info[5]}',
                   reply_markup=bt.choose_pr_count_buttons())


## Сторона администратора ##
# Обработчик команды /admin
@bot.message_handler(commands=['admin'])
def start_admin(msg):
    user_id = msg.from_user.id
    if user_id == 6775701667:
        bot.send_message(user_id, 'Добро пожаловать в админ панель!',
                         reply_markup=bt.admin_menu())
        # Переход на этап выбора админа
        bot.register_next_step_handler(msg, admin_choice)
    else:
        bot.send_message(user_id, 'Вы не админ!')


# Этап выбора админа
def admin_choice(msg):
    admin_id = msg.from_user.id
    if msg.text == 'Добавить продукт':
        bot.send_message(admin_id, 'Напишите наименование товара!',
                         reply_markup=telebot.types.ReplyKeyboardRemove())
        # Переход на этап получения названия
        bot.register_next_step_handler(msg, get_pr_name)
    elif msg.text == 'Удалить продукт':
        bot.send_message(admin_id, 'Выберите товар!',
                         reply_markup=bt.choose_pr_buttons(db.get_all_pr()))
        # Переход на этап выбора продукта
        bot.register_next_step_handler(msg, pr_to_del)
    elif msg.text == 'Изменить количество':
        bot.send_message(admin_id, 'Выберите товар!',
                         reply_markup=bt.choose_pr_buttons(db.get_all_pr()))
        # Переход на этап выбора продукта
        bot.register_next_step_handler(msg, pr_to_change)


# Удаление
def pr_to_del(msg):
    admin_id = msg.from_user.id
    pr_name = msg.text
    bot.send_message(admin_id, 'Вы уверены?',
                     reply_markup=bt.confirm_buttons())
    bot.register_next_step_handler(msg, del_confirm, pr_name)


# Изменение кол-ва
def pr_to_change(msg):
    admin_id = msg.from_user.id
    pr_name = msg.text
    bot.send_message(admin_id, 'Сколько товара прибыло?',
                     reply_markup=telebot.types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, change_confirm, pr_name)


# Обработка текстовых сообщений
@bot.message_handler(content_types=['text'])
# Подтверждение удаления
def del_confirm(msg, pr_name):
    admin_id = msg.from_user.id
    if msg.text == 'Да':
        db.del_pr(pr_name)
        bot.send_message(admin_id, 'Товар успешно удален!',
                         reply_markup=bt.admin_menu())
        # Возврат на этап выбора
        bot.register_next_step_handler(msg, admin_choice)
    elif msg.text == 'Нет':
        bot.send_message(admin_id, 'Ну ок хули',
                         reply_markup=bt.admin_menu())
        # Возврат на этап выбора
        bot.register_next_step_handler(msg, admin_choice)


# Подтверждения добавления кол-ва
def change_confirm(msg, pr_name):
    admin_id = msg.from_user.id
    if msg.text.isnumeric():
        db.change_pr_count(pr_name, int(msg.text))
        bot.send_message(admin_id, 'Кол-во продукта изменено!',
                         reply_markup=bt.admin_menu())
        # Возврат на этап выбора
        bot.register_next_step_handler(msg, admin_choice)
    else:
        bot.send_message(admin_id, 'Пишите кол-во цифрами!')
        # Возврат на подтверждение кол-ва
        bot.register_next_step_handler(msg, change_confirm, pr_name)


# Этап получения названия
def get_pr_name(msg):
    admin_id = msg.from_user.id
    pr_name = msg.text
    bot.send_message(admin_id, 'Теперь придумайте описание товару!')
    # Переход на этап получения описания
    bot.register_next_step_handler(msg, get_pr_des, pr_name)


# Этап получения описания
def get_pr_des(msg, pr_name):
    admin_id = msg.from_user.id
    pr_des = msg.text
    bot.send_message(admin_id, 'Теперь введите цену товара!')
    # Переход на этап получения цены
    bot.register_next_step_handler(msg, get_pr_price, pr_name, pr_des)


# Этап получения цены
def get_pr_price(msg, pr_name, pr_des):
    admin_id = msg.from_user.id
    if msg.text.isdecimal():
        pr_price = float(msg.text)
        bot.send_message(admin_id, 'Перейдите на сайт https://postimages.org/\n'
                                   'Загрузите фото товара и отправьте мне прямую ссылку на него!')
        # Переход на этап получения фото
        bot.register_next_step_handler(msg, get_pr_photo, pr_name, pr_des, pr_price)
    else:
        bot.send_message(admin_id, 'Отправьте цену цифрами!')
        # Возврат на этап получения цены
        bot.register_next_step_handler(msg, get_pr_price, pr_name, pr_des)


# Этап получения названия
def get_pr_photo(msg, pr_name, pr_des, pr_price):
    admin_id = msg.from_user.id
    pr_photo = msg.text
    bot.send_message(admin_id, 'Какое количество у товара?')
    # Переход на этап получения количества
    bot.register_next_step_handler(msg, get_pr_count, pr_name, pr_des, pr_price, pr_photo)


# Этап получения количества
def get_pr_count(msg, pr_name, pr_des, pr_price, pr_photo):
    admin_id = msg.from_user.id
    if msg.text.isnumeric():
        pr_count = int(msg.text)
        db.add_pr(pr_name, pr_des, pr_price, pr_photo, pr_count)
        bot.send_message(admin_id, 'Товар успешно добавлен!', reply_markup=bt.admin_menu())
        # Переход на админ панель
        bot.register_next_step_handler(msg, start_admin)
    else:
        bot.send_message(admin_id, 'Отправьте цену цифрами!')
        # Возврат на этап получения количества
        bot.register_next_step_handler(msg, get_pr_count, pr_name, pr_des, pr_price, pr_photo)


# Запуск бота
bot.polling()
