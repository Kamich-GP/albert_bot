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
    return kb


# Кнопки вывода товаров
def choose_pr_buttons(products):
    # Создаем пространство
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # Создаем сами кнопки
    all_products = [types.KeyboardButton(i[1]) for i in products]
    # Добавляем кнопки в пространство
    kb.add(*all_products)
    return kb


# Кнопки для подтверждения
def confirm_buttons():
    # Создаем пространство
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # Создаем сами кнопки
    yes = types.KeyboardButton('Да')
    no = types.KeyboardButton('Нет')
    # Добавляем кнопки в пространство
    kb.add(yes, no)
    return kb


# Кнопки вывода товаров
def pr_buttons(products):
    # Создаем пространство
    kb = types.InlineKeyboardMarkup(row_width=2)
    # Создаем кнопки
    cart = types.InlineKeyboardButton(text='Корзина', callback_data='cart')
    all_products = [types.InlineKeyboardButton(text=i[1], callback_data=i[0]) for i in products
                    if i[2] > 0]
    # Добавляем кнопки в пространство
    kb.add(*all_products)
    kb.row(cart)
    return kb


# Кнопки выбора количества
def choose_pr_count_buttons(plus_or_minus='', amount=1):
    # Создаем пространство
    kb = types.InlineKeyboardMarkup(row_width=3)
    # Создаем сами кнопки
    minus = types.InlineKeyboardButton(text='-', callback_data='decrement')
    count = types.InlineKeyboardButton(text=amount, callback_data=amount)
    plus = types.InlineKeyboardButton(text='+', callback_data='increment')
    to_cart = types.InlineKeyboardButton(text='Добавить в корзину', callback_data='to_cart')
    back = types.InlineKeyboardButton(text='Назад', callback_data='back')
    # Алгоритм определения кол-ва товара
    if plus_or_minus == 'decrement':
        if amount > 1:
            count = types.InlineKeyboardButton(text=str(amount-1), callback_data=amount)
    elif plus_or_minus == 'increment':
        count = types.InlineKeyboardButton(text=str(amount+1), callback_data=amount)
    # Добавляем кнопки в пространство
    kb.add(minus, count, plus)
    kb.row(to_cart, back)
    return kb


# Кнопки корзины
def cart_buttons():
    # Создаем пространство
    kb = types.InlineKeyboardMarkup(row_width=2)
    # Создаем сами кнопки
    clear = types.InlineKeyboardButton(text='Очистить корзину', callback_data='clear')
    order = types.InlineKeyboardButton(text='Оформить заказ', callback_data='order')
    back = types.InlineKeyboardButton(text='Назад', callback_data='back')
    # Добавляем кнопки в пространство
    kb.add(clear, order)
    kb.row(back)
    return kb
