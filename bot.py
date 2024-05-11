import buttons as bt
import database as db
import telebot
from geopy import Nominatim


# Создаем объект бота
bot = telebot.TeleBot('TOKEN')
# Работа с картами
geolocator = Nominatim(user_agent='Mozilla/5.0 '
                                  '(Windows NT 10.0; Win64; x64) '
                                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                                  'Chrome/124.0.0.0 Safari/537.36')

## Сторона пользователя ##
# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(msg):
    user_id = msg.from_user.id
    check = db.check_user(user_id)
    if check:
        bot.send_message(user_id,
                            f'Добро пожаловать, '
                            f'{msg.from_user.first_name}')
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
        bot.send_message(admin_id, 'Выберите товар!')
    elif msg.text == 'Изменить количество':
        bot.send_message(admin_id, 'Выберите товар!')


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
