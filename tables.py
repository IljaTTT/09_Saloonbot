'''Модуль таблиц определяет функции создания таблиц специалистов, клиентов, 
расписания приема. Заполняет таблицы тестовыми данными, содержит функцию записи на прием

'''
import sqlite3
import os
from functools import wraps
import pandas as pd 


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

def create_tables(conn):    
    '''Функция инициализации таблиц специалистов, посетителей, рабочего расписания'''
    cursor = conn.cursor()         
    try:
        cursor.execute('''
            CREATE TABLE specialists(
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            work_position TEXT NOT NULL
            );
            ''')
        cursor.execute('''
            CREATE TABLE customers (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                phone TEXT NOT NULL
            );
            ''')
        cursor.execute('''
            CREATE TABLE work_schedule (
                id INTEGER PRIMARY KEY,
                specialist_id INTEGER NOT NULL,
                customer_id INTEGER NOT NULL,
                appointment_time DATETIME NOT NULL,
                FOREIGN KEY (specialist_id) REFERENCES specialists(id),
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            );
            ''')               
        conn.commit() 
    except Exception as e:
        conn.rollback()
        print("Error:", e)

def fill_test_data_to_tables(conn):
    '''Функция заполнения таблиц тестовыми данными'''
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO specialists (name, work_position) VALUES
        ('John Smith', 'Hair Stylist'),
        ('Emily Johnson', 'Nail Technician'),
        ('Michael Brown', 'Esthetician'),
        ('Jessica Martinez', 'Massage Therapist'),
        ('David Wilson', 'Makeup Artist');''')
    print('Specialists added to specialists table.', end = ' ')

    cursor.execute('''INSERT INTO customers (name, phone) VALUES
        ('Alice Smith', '555-1234'),
        ('Bob Johnson', '555-5678'),
        ('Charlie Brown', '555-9012'),
        ('Diana Martinez', '555-3456'),
        ('Eva Wilson', '555-7890');''')
    print('Customers added to customers table.', end = ' ')
    
    cursor.execute('''INSERT INTO work_schedule (specialist_id, customer_id, appointment_time) VALUES
        (1, 1, '2024-02-08 09:00:00'), -- John Smith's appointment with Alice Smith
        (1, 1, '2024-02-08 09:00:00'), -- John Smith's appointment with Alice Smith
        (2, 1, '2024-02-08 09:00:00'), -- John Smith's appointment with Alice Smith
        (2, 2, '2024-02-08 10:00:00'), -- Emily Johnson's appointment with Bob Johnson
        (3, 3, '2024-02-08 11:00:00'), -- Michael Brown's appointment with Charlie Brown
        (4, 4, '2024-02-08 12:00:00'), -- Jessica Martinez's appointment with Diana Martinez
        (5, 5, '2024-02-08 13:00:00'), -- David Wilson's appointment with Eva Wilson
        (1, 2, '2024-02-08 14:00:00'), -- John Smith's appointment with Bob Johnson
        (2, 3, '2024-02-08 15:00:00'), -- Emily Johnson's appointment with Charlie Brown
        (3, 4, '2024-02-08 16:00:00'), -- Michael Brown's appointment with Diana Martinez
        (4, 5, '2024-02-08 17:00:00'), -- Jessica Martinez's appointment with Eva Wilson
        (5, 1, '2024-02-08 18:00:00'), -- David Wilson's appointment with Alice Smith
        (1, 2, '2024-02-09 09:00:00'), -- John Smith's appointment with Bob Johnson
        (2, 3, '2024-02-09 10:00:00'), -- Emily Johnson's appointment with Charlie Brown
        (3, 4, '2024-02-09 11:00:00'), -- Michael Brown's appointment with Diana Martinez
        (4, 5, '2024-02-09 12:00:00'), -- Jessica Martinez's appointment with Eva Wilson
        (5, 1, '2024-02-09 13:00:00'), -- David Wilson's appointment with Alice Smith
        (1, 3, '2024-02-09 14:00:00'), -- John Smith's appointment with Charlie Brown
        (2, 4, '2024-02-09 15:00:00'), -- Emily Johnson's appointment with Diana Martinez
        (3, 5, '2024-02-09 16:00:00'), -- Michael Brown's appointment with Eva Wilson
        (4, 1, '2024-02-09 17:00:00'), -- Jessica Martinez's appointment with Alice Smith
        (5, 2, '2024-02-09 18:00:00'), -- David Wilson's appointment with Bob Johnson
        (1, 4, '2024-02-10 09:00:00'), -- John Smith's appointment with Diana Martinez
        (2, 5, '2024-02-10 09:30:00'), -- Emily Johnson's appointment with Eva Wilson
        (3, 1, '2024-02-10 10:00:00'), -- Michael Brown's appointment with Alice Smith
        (4, 2, '2024-02-10 10:30:00'), -- Jessica Martinez's appointment with Bob Johnson
        (5, 3, '2024-02-10 11:00:00'), -- David Wilson's appointment with Charlie Brown
        (1, 5, '2024-02-10 11:30:00'), -- John Smith's appointment with Eva Wilson
        (2, 1, '2024-02-10 12:00:00'), -- Emily Johnson's appointment with Alice Smith
        (3, 2, '2024-02-10 12:30:00'), -- Michael Brown's appointment with Bob Johnson
        (4, 3, '2024-02-10 13:00:00'), -- Jessica Martinez's appointment with Charlie Brown
        (5, 4, '2024-02-10 13:30:00'); -- David Wilson's appointment with Diana Martinez''')
    
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
                GROUP BY appointment_time, specialist_id
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
        ws.appointment_time;''')

    return cursor

@print_as_dataframe
def show_specialist_schedule(conn, specialist_id):
    '''Возвращает рабочее расписание для выбранного специалиста в виде: 
    |дата-время|имя посетителя|телефон|  '''
    cursor = conn.cursor()
    cursor = cursor.execute('''
    SELECT
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
        ws.appointment_time;''', (str(specialist_id)))

    return cursor

def insert_appointment(conn, specialist_id, customer_id, appointment_time):
    '''Функция записи на прием к специалисту, принимает коннект на базу, идентификатор специалиста, 
    идентификатор посетителя, время приема'''
    # Проверяем есть ли на уразанное время запись
    cursor = conn.cursor()
    cursor.execute('''SELECT 1 FROM work_schedule 
                       WHERE appointment_time = '?' AND
                       specialist_id = ?''', 
                   (appointment_time, specialist_id))
    existing_appointment = cursor.fetchone()
    if existing_appointment: 
        # Если занято то выводим ошибку
        print("Error: Appointment time is not available.")
    else:
        # Делаем запись в расписании если свободно
        cursor.execute('''INSERT INTO work_schedule (specialist_id, customer_id, 
        appointment_time) VALUES (?, ?, ?)''',
                       (specialist_id, customer_id, appointment_time))
        conn.commit()
        print("Appointment successfully scheduled.")

def get_customer_id(conn, name, phone):
    cursor = conn.cursor()
    cursor.execute(f'SELECT id FROM customers WHERE phone = "{phone}"')
    customer_id = cursor.fetchone()
    if not customer_id:
        cursor.execute(f'''INSERT INTO customers (name, phone) VALUES 
        ("{name}", "{phone}");''')
        conn.commit()
        cursor.execute(f'SELECT id FROM customers WHERE phone = "{phone}"')
        return cursor.fetchone()        
    return customer_id[0]
        
    
                       
                     
    
    
    
    
    
# os.remove('scheduler.db')
# conn = sqlite3.connect('scheduler.db')