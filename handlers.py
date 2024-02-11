'''Модуль обработчиков '''

'''https://mastergroosha.github.io/aiogram-3-guide/fsm/'''
from aiogram import types, F
from misc import dp
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from kb import specialists_keyboard, days_keyboard, specialist_daytime_keyboard
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

import sqlite3

# Коннект на базу данных
conn = sqlite3.connect('scheduler.db')

# Define states
class AppointmentStates(StatesGroup):
    CHOOSE_SPECIALIST = State()  # State for choosing specialist
    CHOOSE_DAY = State()         # State for choosing day
    CHOOSE_TIME = State()        # State for choosing time

# Separate handler functions for each type of callback query


@dp.message(Command("start"))
async def start_handler(message: Message, state: FSMContext):    
    '''Начальный обработчик, вызывает клавиатуру специалистов'''
    await message.answer(text = "Здравствуйте, выберите специалиста",
                         reply_markup=specialists_keyboard(conn))
    await state.update_data(day=day)
    await state.set_state(AppointmentStates.CHOOSE_SPECIALIST)


@dp.message(AppointmentStates.CHOOSE_SPECIALIST)
async def handle_specialist_select(, state: FSMContext):
    specialist_data = callback_query.data.replace('specialist_', '').split()
    specialist_id = int(specialist_data[-1])

    await state.update_data(specialist_id=specialist_id)

    await callback_query.message.answer(
        f"Вы выбрали специалиста: {callback_query.data}")
    await callback_query.message.answer(
        "Выберите день для записи:", reply_markup=days_keyboard())

    await state.set_state(AppointmentStates.CHOOSE_DAY)  # Move to the next state

async def handle_day_select(callback_query: types.CallbackQuery, state: FSMContext):
    day = callback_query.data.replace('day_', '')
    await state.update_data(day=day)
    data = await state.get_data()

    await callback_query.message.answer(f"Вы выбрали дату: {day}")
    await callback_query.message.answer(
        "Выберите время приема:", 
        reply_markup=specialist_daytime_keyboard(conn, data['specialist_id']))

    await state.set_state(AppointmentStates.CHOOSE_TIME)  # Move to the next state

async def handle_time_select(callback_query: types.CallbackQuery, state: FSMContext):
    time = callback_query.data.replace('time_', '')
    await state.update_data(time=time)
    data = await state.get_data()

    await callback_query.message.answer(
        f"Вы записались к {data['specialist_id']} на {data['day']} число в {time}")

    # Process the appointment with specialist_id, day, and time

    # Reset state
    await state.clear()

# Combined handler to dispatch to individual handlers
@dp.callback_query()
async def specialist_select_handler(callback_query: types.CallbackQuery, state: FSMContext):
    
    await handle_specialist_select(callback_query, state)
    await handle_day_select(callback_query, state)
    await handle_time_select(callback_query, state)

    await callback_query.answer()




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
