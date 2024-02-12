'''Модуль таблиц определяет функции создания таблиц специалистов, клиентов, 
расписания приема. Заполняет таблицы тестовыми данными, содержит функцию записи на прием

'''
import sqlite3
import os
from functools import wraps
import pandas as pd 
import datetime
from random import randint

def print_as_dataframe(func):
    '''Декоратор преобразует ответ базы данных в красивый и удобный pd.Dataframe'''
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Вызов оригинальной функции
        result = func(*args, **kwargs)        
        # Преобразование в датафрйем с описанием колонок
        df = pd.DataFrame(result, columns=[col[0] for col in result.description])        
        return df          
    return wrapper

def drop_tables(conn):
    cursor = conn.cursor()     
    try:
        cursor.execute('DROP TABLE customers')
        cursor.execute('DROP TABLE specialists')
        cursor.execute('DROP TABLE work_schedule')
    except Exception as e:
        conn.rollback()
        print("Error:", e)
    conn.commit() 


def create_tables(conn):    
    '''Функция инициализации таблиц специалистов, посетителей, рабочего расписания'''
    try:
        os.remove(conn)
    except:
        pass
    cursor = conn.cursor()         
    try:
        cursor.execute('''
            CREATE TABLE specialists(
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,            
            work_position TEXT NOT NULL
            );
            ''')
        cursor.execute('''
            CREATE TABLE customers (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                telegram_id TEXT NOT NULL
                
            );
            ''')
        cursor.execute('''
            CREATE TABLE work_schedule (
                id INTEGER PRIMARY KEY,
                specialist_id INTEGER NOT NULL,
                customer_id INTEGER NOT NULL,
                appointment_date DATE NOT NULL,
                appointment_time TEXT NOT NULL,
                FOREIGN KEY (specialist_id) REFERENCES specialists(id),
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            );
            ''')               
        conn.commit() 
    except Exception as e:
        conn.rollback()
        print("Error:", e)

def generate_random_work_schedule_records(n_records = 40):
    record = 'INSERT INTO work_schedule (specialist_id, customer_id, appointment_date, appointment_time) VALUES\n'
    for i in range(n_records):
        specialist_id = randint(1, 5)
        customer_id = randint(1, 5)
        random_hour = randint(8, 18)
        random_date = datetime.date.today() + datetime.timedelta(days=randint(1, 2))
        random_date = random_date.strftime('%Y-%m-%d')
        record += f'({specialist_id}, {customer_id}, "{random_date}", "{random_hour:02d}:00"),\n'

    record = record[:-2] + ';'
    return record

def fill_test_data_to_tables(conn):
    '''Функция заполнения таблиц тестовыми данными'''
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO specialists (name, phone, work_position) VALUES
        ('John Smith', '444-2326', 'Hair Stylist'),
        ('Emily Johnson', '444-3453', 'Nail Technician'),
        ('Michael Brown', '444-7880', 'Esthetician'),
        ('Jessica Martinez', '444-23234', 'Massage Therapist'),
        ('David Wilson', '444-2346', 'Makeup Artist');''')
    print('Specialists added to specialists table.', end = ' ')

    cursor.execute('''INSERT INTO customers (name, phone, telegram_id) VALUES
        ('Alice Smith', '555-1234', '@Smith'),
        ('Bob Johnson', '555-5678', '@John' ),
        ('Charlie Brown', '555-9012', '@Briwn'),
        ('Diana Martinez', '555-3456', '@Marta'),
        ('Eva Wilson', '555-7890', '@Sida');''')
    print('Customers added to customers table.', end = ' ')
    
    cursor.execute(generate_random_work_schedule_records(20))
    
    print('Test records added to work_schedule table.')
    
    conn.commit()

    
def delete_collisions_by_appointment_time(conn):
    '''Функция удаления дубликатов записей в рабочем расписании'''
    try:
        cursor = conn.cursor()
        # Оставляет только первую запись в расписании  удаляя все остальные 
        # с одинаковым временем записи и специалистом 
        cursor.execute("""
            DELETE FROM work_schedule
            WHERE id NOT IN (
                SELECT MIN(id)
                FROM work_schedule
                GROUP BY appointment_time, appointment_time, specialist_id
            )
        """)
        
        # Commit the transaction
        conn.commit()
        
        print("Collisions deleted successfully.")
    except Exception as e:
        conn.rollback()
        print("Error:", e)
        
@print_as_dataframe
def show_table(conn, table: str):
    '''Возвращает ответ базы данных для заданной таблицы'''
    cursor = conn.cursor()
    cursor = cursor.execute(f"SELECT * FROM {table};")
    return cursor

def delete_duplicates_from_specialists(conn):
    '''Функция удаления дубликатов записей в таблице специалистов'''    
    try:
        cursor = conn.cursor()
        # Identify the first occurrence of each unique specialist
        cursor.execute("""
            DELETE FROM specialists
            WHERE id NOT IN (
                SELECT MIN(id)
                FROM specialists
                GROUP BY name, work_position
            )
        """)
        
        # Commit the transaction
        conn.commit()
        
        print("Duplicates deleted successfully.")
    except Exception as e:
        conn.rollback()
        print("Error:", e)
        
def delete_duplicates_from_customers(conn):
    '''Функция удаления дубликатов записей в таблице посетителей'''    
    
    try:
        cursor = conn.cursor()
        # Identify the first occurrence of each unique specialist
        cursor.execute("""
            DELETE FROM customers
            WHERE id NOT IN (
                SELECT MIN(id)
                FROM customers
                GROUP BY name, phone
            )
        """)
        
        # Commit the transaction
        conn.commit()
        
        print("Duplicates deleted successfully.")
    except Exception as e:
        conn.rollback()
        print("Error:", e)
        
@print_as_dataframe
def show_full_schedule(conn):
    '''Возвращает рабочее расписание в отсортированном по времени записи виде: 
    |дата-время|имя посетителя|телефон|имя специалиста|специальность|  '''
    cursor = conn.cursor()
    cursor = cursor.execute('''
    SELECT
        ws.appointment_date,
        ws.appointment_time,
        c.name AS customer_name,
        c.phone AS customer_phone,
        s.name AS specialist_name,
        s.work_position AS specialist_position
    FROM
        work_schedule ws
    JOIN
        customers c ON ws.customer_id = c.id
    JOIN
        specialists s ON ws.specialist_id = s.id
    ORDER BY
        specialist_name, ws.appointment_date, ws.appointment_time;''')

    return cursor

@print_as_dataframe
def show_specialist_schedule(conn, specialist_id):
    '''Возвращает рабочее расписание для выбранного специалиста в виде: 
    |дата-время|имя посетителя|телефон|  '''
    cursor = conn.cursor()
    cursor = cursor.execute('''
    SELECT
        ws.appointment_date,
        ws.appointment_time,
        c.name AS customer_name,
        c.phone AS customer_phone
    FROM
        work_schedule ws
    JOIN
        customers c ON ws.customer_id = c.id
    WHERE
        ws.specialist_id = ?
    ORDER BY
        ws.appointment_date, ws.appointment_time;''', (str(specialist_id)))

    return cursor

def get_busy_hours(conn, specialist_id, day):
    '''Возвращает рабочее расписание для выбранного специалиста в виде: 
    |дата-время|имя посетителя|телефон|  '''
    cursor = conn.cursor()
    cursor = cursor.execute('''
    SELECT
        ws.appointment_time
    FROM
        work_schedule ws
    WHERE
        ws.specialist_id = ? AND ws.appointment_date = ?
    ORDER BY
        ws.appointment_time;''', (str(specialist_id), str(day)))
    result = [item[0] for item in cursor.fetchall()]
    return result

def insert_appointment(conn, specialist_id, customer_id, appointment_date, appointment_time):
    '''Функция записи на прием к специалисту, принимает коннект на базу, идентификатор специалиста, 
    идентификатор посетителя, время приема'''
    # Проверяем есть ли на уразанное время запись
    cursor = conn.cursor()
    cursor.execute(f'''SELECT 1 FROM work_schedule 
                       WHERE appointment_date = "{appointment_date}" AND
                       appointment_time = "{appointment_time}" AND
                       specialist_id = "{specialist_id}"''')                   
    existing_appointment = cursor.fetchone()
    if existing_appointment: 
        # Если занято то выводим ошибку
        print("Error: Appointment time is not available.")
        return False
    else:
        # Делаем запись в расписании если свободно
        cursor.execute('''INSERT INTO work_schedule (specialist_id, customer_id, 
        appointment_date, appointment_time) VALUES (?, ?, ?, ?)''',
                       (specialist_id, customer_id, appointment_date, appointment_time))
        conn.commit()
        print("Appointment successfully scheduled.")
        return True

def get_customer_id(conn, name, phone, telegram_id = '@test'):
    cursor = conn.cursor()
    cursor.execute(f'SELECT id FROM customers WHERE phone = "{phone}"')
    customer_id = cursor.fetchone()
    if not customer_id:
        cursor.execute(f'''INSERT INTO customers (name, phone, telegram_id) VALUES 
        ("{name}", "{phone}", "{telegram_id}");''')
        conn.commit()
        cursor.execute(f'SELECT id FROM customers WHERE phone = "{phone}"')
        return cursor.fetchone()[0]        
    return customer_id[0]
        
    
# os.remove('scheduler.db')
# conn = sqlite3.connect('scheduler.db')