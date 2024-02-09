'''Модуль обработчиков '''
from aiogram import types, F
import pandas as pd
from misc import dp
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from kb import specialists_keyboard, specialist_days_keyboard
# from aiogram.dispatcher.filters import CommandStart
import sqlite3

# Коннект на базу данных
conn = sqlite3.connect('scheduler.db')
# cursor = conn.cursor()


@dp.message(Command("start"))
async def start_handler(msg: Message):    
    '''Начальный обработчик, вызывает клавиатуру специалистов'''
    await msg.answer("Здравствуйте, выберите специалиста", reply_markup=specialists_keyboard(conn))

'''!!!ДОРОБОТАТЬ!!!'''
@dp.callback_query(lambda c: c.data.startswith('specialist_'))
async def specialist_selected_handler(callback_query: CallbackQuery):
    '''Ответ на start_handler'''
    # Извлекает информацию о выбранном специалисте в формате: должность, имя, ид
    specialist = callback_query.data.replace('specialist_', '')  
    # Ид специалиста
    specialist_id = specialist.split()[-1]
    # Выводим в чат 
    await callback_query.message.answer(f"Вы выбрали специалиста: {specialist}")
    # Показываем клавиатуру  
    await callback_query.message.answer(f"Его id: {specialist_id}",
                     reply_markup = specialist_days_keyboard(conn, specialist_id))
    



    
    
    
    
    
    
    
    
    
    
    
    
    
# @dp.message(Command("insert_appointment"))
# async def insert_appointment_handler(msg: Message):    
#     await msg.answer('Здравствуйте, введите id посетителя, id специалиста, и дату-время записи в виде "1, 1, 2024-02-08 09:00:00"')
    
    
    
# # Bot functionality
# @dp.message(Command("start"))
# async def start_handler(msg: Message):
#     await msg.answer("Welcome! Please select a specialist:")

#     # Fetch specialists from the database
#     specialists = cursor.execute('SELECT id, name FROM specialists').fetchall()

#     # Display list of specialists to the user
#     for specialist in specialists:
#         await msg.answer(f"{specialist[0]}. {specialist[1]}")

# @dp.callback_query(lambda c: c.data.startswith('view_calendar_'))
# async def view_calendar_handler(callback_query: types.CallbackQuery):
#     specialist_id = int(callback_query.data.replace('view_calendar_', ''))

#     # Fetch appointments for the specialist from the database
#     appointments = cursor.execute('SELECT time FROM appointments WHERE specialist_id = ?', (specialist_id,)).fetchall()

#     # Display calendar to the user
#     if appointments:
#         await callback_query.message.answer("Calendar:")
#         for appointment in appointments:
#             await callback_query.message.answer(appointment[0])
#     else:
#         await callback_query.message.answer("No appointments scheduled.")

# @dp.callback_query(lambda c: c.data.startswith('book_appointment_'))
# async def book_appointment_handler(callback_query: types.CallbackQuery):
#     specialist_id, appointment_time = callback_query.data.replace('book_appointment_', '').split('_')

#     # Check if appointment is available
#     if is_available(specialist_id, appointment_time):
#         # Book appointment in the database
#         cursor.execute('INSERT INTO appointments (specialist_id, time) VALUES (?, ?)', (specialist_id, appointment_time))
#         conn.commit()
#         await callback_query.message.answer("Appointment booked successfully!")
#     else:
#         await callback_query.message.answer("Sorry, this appointment is not available.")

# # Other handlers for interacting with the scheduler
