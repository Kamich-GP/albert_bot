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
            '(pr_id INTEGER AUTOINCRIMENT, '
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


