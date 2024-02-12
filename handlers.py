'''Модуль обработчиков '''

'''https://mastergroosha.github.io/aiogram-3-guide/fsm/'''
from aiogram import types, F
from misc import dp
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from kb import specialists_keyboard, days_keyboard, specialist_daytime_keyboard, yes_no_keyboard
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from tables import insert_appointment, get_customer_id, show_specialist_schedule

import sqlite3

# Коннект на базу данных
conn = sqlite3.connect('scheduler.db', timeout = 5)

# Define states
class AppointmentStates(StatesGroup):
    ASKED_NAME = State()
    CHOOSED_SPECIALIST = State()  # State for choosing specialist
    CHOOSED_DAY = State()         # State for choosing day
    CHOOSED_TIME = State()        # State for choosing time
    ONE_MORE_TIME = State()        # State for choosing time
    

# Separate handler functions for each type of callback query



@dp.message(Command("start"))
async def start_handler(message: Message, state: FSMContext):    
    '''Начальный обработчик, вызывает клавиатуру специалистов'''
    await message.answer(text = "Здравствуйте, введите свое имя и телефон через пробел")                          
    
    await state.set_state(AppointmentStates.ASKED_NAME)
    
    
@dp.message(AppointmentStates.ASKED_NAME)
async def handle_specialist_select(message: Message, state: FSMContext):    
    ''''''
    name_phone = message.text    
    *customer_name, customer_phone = name_phone.split(' ')
    name = ' '.join(customer_name) if type(customer_name) == list else customer_name
    
    customer_id = get_customer_id(conn, customer_name, customer_phone)
    
    await state.update_data(customer_id=customer_id, 
                            customer_name=customer_name,
                            customer_phone=customer_phone)
    
    await message.answer(text = "Здравствуйте, выберите специалиста",
                         reply_markup=specialists_keyboard(conn))
    
    await state.set_state(AppointmentStates.CHOOSED_SPECIALIST)
    

@dp.callback_query(AppointmentStates.CHOOSED_SPECIALIST)
async def handle_specialist_selected(callback_query: CallbackQuery, state: FSMContext):    
    ''''''
    specialist_data = callback_query.data
    await callback_query.message.answer(text = "Здравствуйте, выберите день записи", 
                                       reply_markup=days_keyboard())
    await state.update_data(specialist_data=specialist_data)
    data = await state.get_data()    
    print(data)
    await state.set_state(AppointmentStates.CHOOSED_DAY)
    
    
@dp.callback_query(AppointmentStates.CHOOSED_DAY)
async def handle_day_selected(callback_query: CallbackQuery, state: FSMContext):    
    ''''''
    date = callback_query.data
    print(date)
    data = await state.get_data()
    specialist_id = data['specialist_data'].split(',')[-1]
    await callback_query.message.answer(text = "Здравствуйте, время записи", 
                                       reply_markup=specialist_daytime_keyboard(conn, specialist_id, date))
    await state.update_data(date=date)
    data = await state.get_data()    
    print(data)
    await state.set_state(AppointmentStates.CHOOSED_TIME)


    
@dp.callback_query(AppointmentStates.CHOOSED_TIME)
async def handle_time_selected(callback_query: CallbackQuery, state: FSMContext):    
    
    time = callback_query.data
    await state.update_data(time=time)
    data = await state.get_data()    
    specialist_data, customer_id = data['specialist_data'], data['customer_id']
    appointment_date, appointment_time = data['date'], data['time']
                                                                        
    specialist, specialist_id = specialist_data.split(',')
    specialist_id = int(specialist_id)
    
    print([specialist_id, customer_id, appointment_date, appointment_time])
    insert_appointment(conn, specialist_id, customer_id, appointment_date, appointment_time)
    await callback_query.message.answer(f"Вы записались к {specialist} на {appointment_date} число в {appointment_time}")    
    await callback_query.message.answer("Записатья еще?", 
                                       reply_markup=yes_no_keyboard())
    
    print(show_specialist_schedule(conn, specialist_id))
    
    await state.set_state(AppointmentStates.ONE_MORE_TIME)
    
@dp.message(AppointmentStates.ONE_MORE_TIME)
async def repeat_appiontment(message: Message, state: FSMContext):  
    answer = callback_query.data
    if answer == 'Да':        
        await state.set_state(AppointmentStates.ASKED_NAME)
        await specialist_select()
    else:
        print('Отлично, я записал вас на прием... Вам перезвонят')
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
