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
conn = sqlite3.connect('scheduler.db')  
specialists = show_table(conn, 'specialists')

# Create a list of tuples containing specialist names and their corresponding IDs
specialists_list = [f"{spec['work_position']} {spec['name']}" 
                    for _, spec in specialists.iterrows()]
 
# Create inline keyboard buttons for each specialist
specialists_keys = [
    [types.InlineKeyboardButton(
        text=specialist, 
        callback_data=f"specialist_{specialist}")]
    for specialist in specialists_list]

# Create an InlineKeyboardMarkup with the keyboard buttons
specialists_keyboard = types.InlineKeyboardMarkup(inline_keyboard=specialists_keys)
