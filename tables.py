import sqlite3
import os
from functools import wraps
import pandas as pd 

def print_as_dataframe(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Call the original function
        result = func(*args, **kwargs)
        
        # Convert the result to a pandas DataFrame
        df = pd.DataFrame(result, columns=[col[0] for col in result.description])        
        return df  # Return the DataFrame
        
    return wrapper

def create_tables(conn):    
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
    try:
        cursor = conn.cursor()
        # Identify the first record for each combination of appointment time and specialist
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
    cursor = conn.cursor()
    cursor = cursor.execute(f"SELECT * FROM {table};")
    return cursor

def delete_duplicates_from_specialists(conn):
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
    # Check if the appointment time is available
    cursor = conn.cursor()
    cursor.execute('''SELECT 1 FROM work_schedule 
                       WHERE appointment_time = ? AND
                       specialist_id = ?''', 
                   (appointment_time, specialist_id))
    existing_appointment = cursor.fetchone()
    if existing_appointment:
        # If appointment exists, return an error
        print("Error: Appointment time is not available.")
    else:
        # Insert the new entry into the work_schedule table
        cursor.execute('''INSERT INTO work_schedule (specialist_id, customer_id, 
        appointment_time) VALUES (?, ?, ?)''',
                       (specialist_id, customer_id, appointment_time))
        conn.commit()
        print("Appointment successfully scheduled.")

# os.remove('scheduler.db')
conn = sqlite3.connect('scheduler.db')