import sqlite3


# Создание БД
conn = sqlite3.connect('delivery.db', check_same_thread=False)
# Python + SQL
sql = conn.cursor()


# Создание таблицы пользователей
sql.execute('CREATE TABLE IF NOT EXISTS users '
            '(id INTEGER, name TEXT, number TEXT, location TEXT);')
# Создание таблицы продуктов
sql.execute('CREATE TABLE IF NOT EXISTS products '
            '(pr_id INTEGER PRIMARY KEY AUTOINCREMENT, '
            'pr_name TEXT, pr_des TEXT, pr_price REAL, '
            'pr_photo TEXT, pr_count INTEGER);')
# Создание таблицы
sql.execute('CREATE TABLE IF NOT EXISTS cart '
            '(user_id INTEGER, user_product TEXT, '
            'user_quantity INTEGER);')


## Методы для пользователя ##
# Регистрация
def register(id, name, number, location):
    sql.execute('INSERT INTO users VALUES (?, ?, ?, ?);',
                (id, name, number, location))
    # Фиксируем изменения
    conn.commit()


# Проверка на наличие пользователя в БД
def check_user(id):
    if sql.execute('SELECT * FROM users WHERE id=?;', (id,)).fetchone():
        return True
    else:
        return False


## Методы для продуктов ##
# Метод для вывода всех товаров
def get_all_pr():
    return sql.execute('SELECT pr_id, pr_name, pr_count FROM products;').fetchall()


# Метод для проверки товара
def get_pr_id():
    result = sql.execute('SELECT pr_id FROM products;').fetchall()
    pr_list = [i[0] for i in result]
    return pr_list


# Метод для вывода определенного товара
def get_exact_pr(id):
    return sql.execute('SELECT * FROM products WHERE pr_id=?;', (id,)).fetchone()


# Метод для вывода цены товара по названию
def get_exact_price(pr_name):
    return sql.execute('SELECT pr_price FROM products WHERE pr_name=?;', (pr_name,)).fetchone()


# Метод для добавления продукта в БД
def add_pr(pr_name, pr_des, pr_price, pr_photo, pr_count):
    sql.execute('INSERT INTO products '
                '(pr_name, pr_des, pr_price, pr_photo, pr_count) VALUES '
                '(?, ?, ?, ?, ?);',
                (pr_name, pr_des, pr_price, pr_photo, pr_count))

    # Фиксируем изменения
    conn.commit()


# Метод для удаления товара
def del_pr(id):
    sql.execute('DELETE FROM products WHERE pr_id=?;', (id,))

    # Фиксируем изменения
    conn.commit()


# Метод для изменения количества товара
def change_pr_count(id, new_count):
    # Текущее количество товара
    now_count = sql.execute('SELECT pr_count FROM products WHERE pr_id=?;', (id,)).fetchone()
    # Новое количество
    plus_count = now_count[0] + new_count
    sql.execute('UPDATE products SET pr_count=? WHERE pr_id=?;', (plus_count, id))
    # Фиксируем изменения
    conn.commit()


# Проверка на наличие товара в БД
def check_pr():
    if sql.execute('SELECT * FROM products;').fetchall():
        return True
    else:
        return False


## Методы для корзины ##
# Метод для добавления товара в корзину
def add_pr_to_cart(user_id, user_product, user_quantity):
    sql.execute('INSERT INTO cart VALUES (?, ?, ?);', (user_id, user_product, user_quantity))
    # Фиксируем изменения
    conn.commit()


# Метод для очистки корзины
def clear_cart(user_id):
    sql.execute('DELETE FROM cart WHERE user_id=?;', (user_id,))
    # Фиксируем изменения
    conn.commit()


# Вывод корзины
def show_cart(user_id):
    return sql.execute('SELECT * FROM cart WHERE user_id=?;', (user_id,)).fetchall()


# Оформление заказа
def make_order(user_id):
    # Вещи, которые выбрал пользователь
    product_name = sql.execute('SELECT user_product FROM cart WHERE user_id=?;', (user_id,)).fetchall()
    product_quantity = sql.execute('SELECT user_quantity FROM cart WHERE user_id=?;', (user_id,)).fetchall()
    # Склад
    product_counts = []
    for i in product_name:
        product_counts.append(sql.execute('SELECT pr_count FROM products WHERE pr_name=?;', (i[0],)).fetchone()[0])
    totals = []
    for e in product_quantity:
        for c in product_counts:
            totals.append(c - e[0])
    for t in totals:
        for n in product_name:
            sql.execute('UPDATE products SET pr_count=? WHERE pr_name=?;', (t, n[0]))
    sql.execute('DELETE FROM CART WHERE user_id=?;', (user_id,))
    address = sql.execute('SELECT location FROM users WHERE id=?;', (user_id,)).fetchone()
    # Фиксируем изменения
    conn.commit()
    return product_counts, totals, address
