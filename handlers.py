'''Модуль обработчиков '''

'''https://mastergroosha.github.io/aiogram-3-guide/fsm/'''
from aiogram import types, F
from misc import dp
import datetime
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from kb import (specialists_keyboard, days_keyboard, 
                specialist_time_keyboard, yes_no_keyboard)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from tables import (insert_appointment, insert_customer,
                    get_customer_id, show_specialist_schedule,
                    show_specialist_day_schedule,
                    get_specialists_telegramm_ids, 
                    get_specialist_name_and_id_by_telegram_id)

import sqlite3

# Коннект на базу данных
conn = sqlite3.connect('scheduler.db', timeout = 5)

# Define states
class SpecialistStates(StatesGroup):
    L1 = State()
    L2 = State()
    
class AppointmentStates(StatesGroup):
    NAME_ASKED = State()
    SPECIALIST_CHOOSED = State()  # State for choosing specialist
    DAY_CHOOSED = State()         # State for choosing day
    TIME_CHOOSED = State()        # State for choosing time
    ONE_MORE_TIME = State()        # State for choosing time
    

# Separate handler functions for each type of callback query



@dp.message(Command("start"))
async def start_handler(message: Message, state: FSMContext):    
    '''Начальный обработчик, смотрит telegram_id, определет специалист/посетитель
    вызывает спрашивает имя и телефон у посетителя и рабочий день у специалиста '''
    telegram_id = message.chat.username 
    if telegram_id in get_specialists_telegramm_ids(conn):
        await message.answer(text = 'Вы специалист!')
        name_id = await get_specialist_name_and_id_by_telegram_id(conn, telegram_id)
        (specialist_name, specialist_id) = name_id
        await message.answer(text = f'Здравствуйте {specialist_name}, выберете рабочий день.',
                            reply_markup=days_keyboard())
        await state.update_data(specialist_id= specialist_id)
        await state.set_state(SpecialistStates.L1)        
    else:
        await state.update_data(telegram_id = telegram_id)
        await message.answer(text = 'Здравствуйте, введите свое имя и телефон через пробел') 
        await state.set_state(AppointmentStates.NAME_ASKED)
    

@dp.callback_query(SpecialistStates.L1, 
                   lambda c: c.data.startswith('date_'))                  
async def specialist_selected_day_handler(callback_query: CallbackQuery, state: FSMContext):
    '''Обработчик даты для специалиста'''
    date = callback_query.data.replace('date_', '')
    data = await state.get_data()
    specialist_id = data['specialist_id']
    await callback_query.message.answer(text = f'Ваш график на {date}:')
    dataframe = show_specialist_day_schedule(conn, specialist_id, date)
    await callback_query.message.answer(text = str(dataframe)) 
    

@dp.message(AppointmentStates.NAME_ASKED)
async def specialist_select_handler(message: Message, state: FSMContext):    
    ''''''
    await state.update_data(message_= message)
    name_phone = message.text    
    *customer_name, customer_phone = name_phone.split(' ')
    customer_name = '_'.join(customer_name) if type(customer_name) == list else customer_name        
    customer_id = await get_customer_id(conn, customer_name, customer_phone)
    
    data = await state.get_data()
    telegram_id = data['telegram_id']
    
    
    
    await state.update_data(customer_id=customer_id,
                            customer_name=customer_name,
                            customer_phone=customer_phone)
    
    await insert_customer(conn, name = customer_name, phone = customer_phone,
                          telegram_id = telegram_id)    
    
    await message.answer(text = "Здравствуйте, выберите специалиста:",
                         reply_markup=specialists_keyboard(conn))
    
    await state.set_state(AppointmentStates.SPECIALIST_CHOOSED)
    

@dp.callback_query(AppointmentStates.SPECIALIST_CHOOSED,
                   lambda c: c.data.startswith('spec_'))

async def date_select_handler(callback_query: CallbackQuery, state: FSMContext):    
    ''''''
    await state.update_data(callback_query_= callback_query)
    
    specialist_data = callback_query.data.replace('spec_', '')
    await callback_query.message.answer(text = "Выберите день записи", 
                                       reply_markup=days_keyboard())
    
    await state.update_data(specialist_data=specialist_data)
    
#     data = await state.get_data()    
    
    await state.set_state(AppointmentStates.DAY_CHOOSED)
    
    
@dp.callback_query(AppointmentStates.DAY_CHOOSED, 
                   lambda c: c.data.startswith('date_'))                  
async def time_select_handler(callback_query: CallbackQuery, state: FSMContext):    
    '''Обработчик даты записи для посетителя, выводит клавиатуру даты'''
    date = callback_query.data.replace('date_', '')
    if date == 'backward_':
        data = await state.get_data()          
        message = data['message_']
        await state.set_state(AppointmentStates.NAME_ASKED)    
        await specialist_select_handler(message, state)
    
    else:
        
        data = await state.get_data()
        specialist_id = data['specialist_data'].split(',')[-1]
        await callback_query.message.answer(text = "Время записи", 
                                            reply_markup=specialist_time_keyboard(conn, specialist_id, date))
        await state.update_data(date=date)
        await state.set_state(AppointmentStates.TIME_CHOOSED)    


    
@dp.callback_query(AppointmentStates.TIME_CHOOSED, lambda c: c.data.startswith('time_'))    
async def insert_appointment_handler(callback_query: CallbackQuery, state: FSMContext):    

    
    time = callback_query.data.replace('time_', '')
    
    if time == 'backward_':
        data = await state.get_data()          
        await state.set_state(AppointmentStates.SPECIALIST_CHOOSED) 
        callback_query = data['callback_query_']
        await date_select_handler(callback_query, state)
    
    
    else:
        await state.update_data(time=time)
        data = await state.get_data()                  
        specialist_data, customer_id = data['specialist_data'], data['customer_id']
        appointment_date, appointment_time = data['date'], data['time']

        specialist, specialist_id = specialist_data.split(',')
        specialist_id = int(specialist_id)
        await insert_appointment(conn, specialist_id, customer_id, appointment_date, appointment_time)
        await callback_query.message.answer(
            f"{specialist} будет ждать вас {appointment_date} числа в {appointment_time}")    
        
        await callback_query.message.answer("Хотите записаться еще?", 
                                           reply_markup=yes_no_keyboard())

        await state.set_state(AppointmentStates.ONE_MORE_TIME)
                            
@dp.callback_query(AppointmentStates.ONE_MORE_TIME, 
                   lambda c: c.data.startswith('yes_no_'))

async def repeat_appiontment(callback_query: CallbackQuery, state: FSMContext):  
    answer = callback_query.data.replace('yes_no_', '')
    data = await state.get_data()     
    if answer == 'Да':                
        message = data['message_']
        await state.set_state(AppointmentStates.NAME_ASKED)        
        await specialist_select_handler(message, state)
        
    else:
        print('END')
        await callback_query.message.answer('Отлично, вы записаны. Вам перезвонят. Если хотите повторить напишите /start')
        await state.clear()


    
# @dp.callback_query(lambda c: c.data.startswith('specialist_'))
# async def specialist_selected_handler(callback_query: CallbackQuery):
#     '''Ответ на start_handler'''
#     # Извлекает информацию о выбранном специалисте в формате: должность, имя, ид
#     specialist = callback_query.data.replace('specialist_', '')  
#     # Ид специалиста
#     specialist_id = specialist.split()[-1]
#     # Выводим в чат 
#     await callback_query.message.answer(f"Вы выбрали специалиста: {specialist}")   
    
    
    
    
    
    
    
    
    
    
    
    
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
