"""Модуль клавиатур, подключается к таблицам данных и создает клавиатуры"""
import sqlite3
from tables import (
    #     create_tables, fill_test_data_to_tables,
    #     delete_collisions_by_appointment_time,
    #     delete_duplicates_from_customers,
    #     delete_duplicates_from_specialists,
    show_table, show_full_schedule,
    show_specialist_schedule,
    insert_appointment,
    get_busy_hours
)
import datetime
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

def admin_keyboard(conn: sqlite3.connect) -> InlineKeyboardMarkup:
    buttons = ['/cust_list', '/spec_list',]
    buttons = [
        [InlineKeyboardButton(text=button, callback_data=button)]
         for button in buttons]
    # Клавиатура
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def specialists_keyboard(conn: sqlite3.connect) -> InlineKeyboardMarkup:
    """Клавиатура выбора специалистов"""
    # pd.Dataframe со специалистами салона
    specialists = show_table(conn, 'specialists')
    # Список специалистов
    specialists_list = [f"{spec['work_position']} {spec['name']},{spec['id']}"
                        for _, spec in specialists.iterrows()]

    # Кнопки клавиатуры из списка специалистов
    specialists_keys = [
        [InlineKeyboardButton(
            text=specialist.split(',')[0],
            callback_data='spec_' + specialist)]
        for specialist in specialists_list]
    # Клавиатура
    keyboard = InlineKeyboardMarkup(inline_keyboard=specialists_keys)
    return keyboard


def days_keyboard(n_days: int = 20) -> InlineKeyboardMarkup:
    """Возвращает клавиатуру с днями для записи"""

    # Генерация списка дней из n_days начиная с сегодняшнего дня
    dates = [datetime.date.today() + datetime.timedelta(days=i) for i in range(n_days)]

    # Форматируем дни как строки
    date_strings = [date.strftime('%Y-%m-%d') for date in dates]

    # Создаем клавиатуру из списка дней
    builder = InlineKeyboardBuilder()
    for date in date_strings:
        builder.button(text=date[5:], callback_data='date_' + date)
        # Добавляем кнопу Назад
    builder.button(text='Назад', callback_data='date_backward_')
    # Раскидываем кнопки
    builder.adjust(5, 5, 5)

    return builder.as_markup()


def specialist_time_keyboard(conn: sqlite3.connect, specialist_id: int,
                             date: str, start_hour: int = 8,
                             end_hour: int = 18) -> InlineKeyboardMarkup:
    """!!!!Клавиатура выбора времени записи, с учетом рассписания специалиста,
    принимает ид специалиста, дату"""
    hours = [f'{hour:02d}:00' for hour in range(start_hour, end_hour + 1)]  #
    busy_hours = get_busy_hours(conn, specialist_id, date)
    free_hours = [hour for hour in hours if hour not in busy_hours]
    builder = InlineKeyboardBuilder()

    for hour in free_hours:
        builder.button(text=hour, callback_data='time_' + hour)

    builder.button(text='Назад', callback_data='time_backward_')
    builder.adjust(5, 5, 1)

    return builder.as_markup()


def yes_no_keyboard():
    keys = ['Да', 'Нет']
    builder = InlineKeyboardBuilder()
    for key in keys:
        builder.button(text=key, callback_data='yes_no_' + key)
    builder.adjust(2)
    return builder.as_markup()


def specialist_schedule_keyboard(conn: sqlite3.connect, specialist_id: int):
    """Принимает sqlite3.connect  и id специалиста, возвращает список записей на прием к
    данному специалисту, в виде aiogram.types.InlineKeyboardMarkup"""

    # pd.Dataframe с расписанием специалиста
    specialist_days = show_specialist_schedule(conn, specialist_id)
    # Список записей на прием
    specialist_days_list = [f"{spec_d['appointment_time']} {spec_d['customer_name']}"
                            for _, spec_d in specialist_days.iterrows()]
    # Кнопки клавиатуры из списка записей
    specialist_days_keys = [
        [InlineKeyboardButton(
            text=specialist_day,
            callback_data=f"specialist_day{specialist_day}")]
        for specialist_day in specialist_days_list]

    # Клавиатура
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=specialist_days_keys)

    return keyboard
