from telebot import types


# Кнопка для отправки номера
def num_button():
    # Создаем пространство для кнопок
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # Создаем кнопки
    but1 = types.KeyboardButton('Отправить номер📞',
                                request_contact=True)
    # Добавляем кнопки в пространство
    kb.add(but1)
    return kb


# Кнопка для отправки локации
def loc_button():
    # Создаем пространство для кнопок
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # Создаем кнопки
    but1 = types.KeyboardButton('Отправить геопозоцию📌',
                                request_location=True)
    # Добавляем кнопки в пространство
    kb.add(but1)
    return kb


# Кнопки админ-меню
def admin_menu():
    # Создаем пространство
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # Создаем сами кнопки
    add = types.KeyboardButton('Добавить продукт')
    delete = types.KeyboardButton('Удалить продукт')
    change = types.KeyboardButton('Изменить количество')
    back = types.KeyboardButton('Обратно в меню')
    # Добавляем кнопки в пространство
    kb.add(add, delete, change)
    kb.row(back)


# Кнопки для подтверждения
def confirm_buttons():
    # Создаем пространство
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # Создаем сами кнопки
    yes = types.KeyboardButton('Да')
    no = types.KeyboardButton('Нет')
    # Добавляем кнопки в пространство
    kb.add(yes, no)
