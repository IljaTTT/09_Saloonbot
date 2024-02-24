from aiogram.fsm.state import StatesGroup, State

'''Состояния для работы с админом'''
class AdminStates(StatesGroup):
    BASE = State() #
    SPEC_SCHEDULE = State()
    SPEC_DAY_SCHEDULE = State()
    CUSTOMER = State()



'''Состояния для работы со специалистами'''
class SpecialistStates(StatesGroup):
    DATE_SELECT = State() # Состояние выбора даты 
    # L2 = State()
    
'''Состояния для работы с гостями'''    
class AppointmentStates(StatesGroup):
    SPEC_SELECT = State() # Состояние выбора специалиста
    DATE_SELECT = State() # Состояние выбора даты
    TIME_SELECT = State() # Состояние выбора времени
    INSERT_APPO = State() # Состояние записи в таблицу
    REPEAT_THIS = State() # Состояние опроса о повторе