'''Модуль обработчиков '''

'''https://mastergroosha.github.io/aiogram-3-guide/fsm/'''
from aiogram import types, F
from misc import dp
from config import TABLES_PATH
import datetime
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from kb import (specialists_keyboard, days_keyboard, 
                specialist_time_keyboard, yes_no_keyboard)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from states import SpecialistStates, AppointmentStates
from tables import (insert_appointment, insert_customer, show_table, 
                    get_customer_id, show_specialist_schedule,
                    show_specialist_day_schedule,
                    show_full_schedule,
                    get_specialists_telegramm_ids, 
                    get_spec_nameid)

import sqlite3

# Коннект на базу данных
conn = sqlite3.connect(TABLES_PATH, timeout = 5)

"""Собираем телеграм ид специалистов"""
specialists_telegramm_ids = get_specialists_telegramm_ids(conn)

# Separate handler functions for each type of callback query

@dp.message(Command("start"))
async def start_handler(message: Message, state: FSMContext):    
    '''Начальный обработчик, смотрит telegram_id, определет специалист/посетитель
    вызывает спрашивает имя и телефон у посетителя и рабочий день у специалиста '''
    telegram_id = message.chat.username # Определение телеграм ид
    if telegram_id in specialists_telegramm_ids: #Проверяем специалист/посетитель
        await message.answer(text = 'Вы специалист!')
        """Определяем имя и ид специалиста в таблице по телеграм ид"""
        (specialist_name, specialist_id) = await get_spec_nameid(conn, telegram_id)
        await message.answer(text = f'Здравствуйте {specialist_name}, выберете рабочий день.',
                            reply_markup=days_keyboard()) # Приветствуем, показываем клавиатуру даты
        await state.update_data(specialist_id = specialist_id) # Сохраняем ид в контексте
        await state.set_state(SpecialistStates.DATE_SELECT) # Состояние выбора даты       
    else:
        await state.update_data(telegram_id = telegram_id)
        await message.answer(text = 'Здравствуйте, введите свое имя и телефон через пробел') 
        await state.set_state(AppointmentStates.SPEC_SELECT)
    
@dp.callback_query(SpecialistStates.DATE_SELECT, 
                   lambda c: c.data.startswith('date_'))                  
async def specialist_selected_day_handler(callback_query: CallbackQuery, state: FSMContext):
    '''Обработчик даты для специалиста'''
    date = callback_query.data.replace('date_', '') # Определяем дату с клавиатуры даты
    data = await state.get_data() # Данные контекста
    specialist_id = data['specialist_id'] # Берем ид
    await callback_query.message.answer(text = f'Ваш график на {date}:')
    """Показываем расписание специалиста на выбраннный день"""
    dataframe = show_specialist_day_schedule(conn, specialist_id, date) 
    await callback_query.message.answer(text = str(dataframe)) 
    
@dp.message(AppointmentStates.SPEC_SELECT)
async def specialist_select_handler(message: Message, state: FSMContext):    
    '''Обработчик выбора специалиста для записи посетителя на прием'''
    await state.update_data(message_= message) # Сохраняем имя, телефон с предидущего этапа,
    name_phone = message.text    # это нужно если человек захочет записаться еще к др. спец.
    *customer_name, customer_phone = name_phone.split(' ') # Если несколько слов в имени
    customer_name = '_'.join(customer_name) if type(customer_name) == list else customer_name        
    customer_id = await get_customer_id(conn, customer_name, customer_phone)  #ид пос. из таблицы
    
    await state.update_data(customer_id=customer_id, # Сохраняем ид, имя, тел. в контекст
                            customer_name=customer_name,
                            customer_phone=customer_phone)
    
    data = await state.get_data() # Берем телеграм ид из контекста
    telegram_id = data['telegram_id']    
    await insert_customer(conn, name = customer_name, phone = customer_phone,
                          telegram_id = telegram_id) #Добавляем посетителя в таблицу
    
    await message.answer(text = "Здравствуйте, выберите специалиста:", #Клавиатура выбора специалиста
                         reply_markup=specialists_keyboard(conn))
    await state.set_state(AppointmentStates.DATE_SELECT) #Состояние выбора даты
    
@dp.callback_query(AppointmentStates.DATE_SELECT,
                   lambda c: c.data.startswith('spec_'))
async def date_select_handler(callback_query: CallbackQuery, state: FSMContext):    
    '''Обработчик выбора даты для записи на прием к выбранному специалисту'''
    
    """Сохраняем в контекст данные о выбранном специалисте, это нужно, если мы далее,
    в insert_appointment_handler нажмем кнопку назад"""    
    await state.update_data(callback_query_= callback_query)     
    
    specialist_data = callback_query.data.replace('spec_', '') #Данные по специалисту
    await state.update_data(specialist_data=specialist_data) #Сохраняем данные по спец. в контекст   
    
    await callback_query.message.answer(text = "Выберите день записи", # Клавиатура дней
                                       reply_markup=days_keyboard())    
    
    await state.set_state(AppointmentStates.TIME_SELECT) # Состояние выбора времени

    
@dp.callback_query(AppointmentStates.TIME_SELECT, 
                   lambda c: c.data.startswith('date_'))                  
async def time_select_handler(callback_query: CallbackQuery, state: FSMContext):    
    '''Обработчик времени записи для посетителя'''
    date = callback_query.data.replace('date_', '') #Дата с клавиатуры дней
    if date == 'backward_': # Если была нажата кнопка Назад:
        data = await state.get_data() # Берем ранее сохраненный message_ из контекста
        message = data['message_']
        await state.set_state(AppointmentStates.SPEC_SELECT) # Возвращаемся в состояние выбора спец
        await specialist_select_handler(message, state) # Вызываем обработчик выбора специалиста
    
    else: # Если была выбрана нажата кнопка с датой
        data = await state.get_data() # Берем id специалиста из контекста
        specialist_id = data['specialist_data'].split(',')[-1]
        """Выводим клавиатуру выбора времени для конкретного специалиста в  выбранный день"""
        await callback_query.message.answer(text = "Время записи", 
                                            reply_markup=specialist_time_keyboard(conn, specialist_id, date))
        await state.update_data(date=date) # Сохраняем дату в контекст
        await state.set_state(AppointmentStates.INSERT_APPO) # Состояние записи в таблицу


@dp.callback_query(AppointmentStates.INSERT_APPO, lambda c: c.data.startswith('time_'))    
async def insert_appointment_handler(callback_query: CallbackQuery, state: FSMContext):    
    """Обработчик внесения записи в таблицу"""
    
    time = callback_query.data.replace('time_', '') #Берем время с клавиатуры времени
    
    if time == 'backward_':  # Если была нажата кнопка Назад:
        data = await state.get_data() # Берем ранее сохраненный callback_query_ из контекста          
        callback_query = data['callback_query_'] #Он был сохранен на в обработчике date_select_handler
        await state.set_state(AppointmentStates.DATE_SELECT) #Возврат в состяние выбора даты        
        await date_select_handler(callback_query, state) #Обработчик выбора даты
        
    else: # Если была нажата кнопка выбора времени:
        await state.update_data(time=time) # Сохраняем в контекст время записи ???? можно обойтись
        data = await state.get_data() # Берем данные из контекста                 
        specialist_data, customer_id = data['specialist_data'], data['customer_id']
        appointment_date, appointment_time = data['date'], data['time']        
        specialist, specialist_id = specialist_data.split(',')
        specialist_id = int(specialist_id)
        """Вносим всю информацию в таблицу"""
        await insert_appointment(conn, specialist_id, customer_id, appointment_date, appointment_time)
        
        await callback_query.message.answer(
            f"{specialist} будет ждать вас {appointment_date} числа в {appointment_time}")    
        
        await callback_query.message.answer("Хотите записаться еще?", #Клавиатура повтора
                                           reply_markup=yes_no_keyboard())

        await state.set_state(AppointmentStates.REPEAT_THIS)
                            
@dp.callback_query(AppointmentStates.REPEAT_THIS, 
                   lambda c: c.data.startswith('yes_no_'))
async def repeat_appiontment(callback_query: CallbackQuery, state: FSMContext):  
    """Обработчик повтора записи"""
    answer = callback_query.data.replace('yes_no_', '')
    
    if answer == 'Да': # Если повторяем запись, то               
        data = await state.get_data() # Берем данные из контекста    
        message = data['message_'] #ранее сохраненный message в обработчике specialist_select_handler
#         print(show_full_schedule(conn))
        await state.set_state(AppointmentStates.SPEC_SELECT) # Состояние выюора специалиста        
        await specialist_select_handler(message, state) # Обработчик specialist_select_handler        
    else: # Завершение записи на прием
        print('END') 
        await callback_query.message.answer('Отлично, вы записаны. Вам перезвонят. Если хотите повторить напишите /start')
        await state.clear()