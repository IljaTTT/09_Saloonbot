'''Модуль клавиатур, подключается к таблицам данных и создает клавиатуры'''
import sqlite3
from tables import (
#     create_tables, fill_test_data_to_tables,     
#     delete_collisions_by_appointment_time, 
#     delete_duplicates_from_customers, 
#     delete_duplicates_from_specialists, 
    show_table, show_full_schedule, 
    show_specialist_schedule, 
    insert_appointment
)

import pandas as pd
from aiogram import types

# Load specialists data from fatabase
# conn = sqlite3.connect('scheduler.db')  

def specialists_keyboard(conn: sqlite3.connect):
    '''Принимает sqlite3.connect возвращает список специалистов 
    в виде aiogram.types.InlineKeyboardMarkup'''
    
    # pd.Dataframe со специалистами салона
    specialists = show_table(conn, 'specialists') 

    # Список специалистов
    specialists_list = [f"{spec['work_position']} {spec['name']} {spec['id']}" 
                        for _, spec in specialists.iterrows()]

    # Кнопки клавиатуры из списка специалистов
    specialists_keys = [
        [types.InlineKeyboardButton(
            text=specialist, 
            callback_data=f"specialist_{specialist}")]
        for specialist in specialists_list]

    # Клавиатура
    specialists_keyboard = types.InlineKeyboardMarkup(inline_keyboard=specialists_keys)
    return specialists_keyboard

def specialist_days_keyboard(conn: sqlite3.connect, specialist_id: int):
    '''Принимает sqlite3.connect  и id специалиста, возвращает список записей на прием к
    данному специалисту, в виде aiogram.types.InlineKeyboardMarkup'''
    
    # pd.Dataframe с расписанием специалиста
    specialist_days = show_specialist_schedule(conn, specialist_id)
#     print(specialist_days)
    # Список записей на прием
    specialist_days_list =  [f"{spec_d['appointment_time']} {spec_d['customer_name']}" 
                        for _, spec_d in specialist_days.iterrows()]
    # Кнопки клавиатуры из списка записей
    specialist_days_keys = [
        [types.InlineKeyboardButton(
            text=specialist_day, 
            callback_data=f"specialist_days{specialist_day}")]
        for specialist_day in specialist_days_list]
    
    # Клавиатура
    specialist_days_keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=specialist_days_keys)
    
    return specialist_days_keyboard