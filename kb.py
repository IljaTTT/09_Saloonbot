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

def specialists_keyboard(conn):
    specialists = show_table(conn, 'specialists')


    # Create a list of tuples containing specialist names and their corresponding IDs
    specialists_list = [f"{spec['work_position']} {spec['name']} {spec['id']}" 
                        for _, spec in specialists.iterrows()]

    # Create inline keyboard buttons for each specialist
    specialists_keys = [
        [types.InlineKeyboardButton(
            text=specialist, 
            callback_data=f"specialist_{specialist}")]
        for specialist in specialists_list]

    # Create an InlineKeyboardMarkup with the keyboard buttons
    specialists_keyboard = types.InlineKeyboardMarkup(inline_keyboard=specialists_keys)
    return specialists_keyboard

def specialist_days_keyboard(conn, specialist_id):    
    specialist_days = show_specialist_schedule(conn, specialist_id)
    print(specialist_days)
    specialist_days_list =  [f"{spec_d['appointment_time']} {spec_d['customer_name']}" 
                        for _, spec_d in specialist_days.iterrows()]

    specialist_days_keys = [
        [types.InlineKeyboardButton(
            text=specialist_day, 
            callback_data=f"specialist_days{specialist_day}")]
        for specialist_day in specialist_days_list]

    specialist_days_keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=specialist_days_keys)
    
    return specialist_days_keyboard