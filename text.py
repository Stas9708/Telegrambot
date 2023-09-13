HELP_COMMAND = """
/start - початок роботи 
/help - список команд 
/trainer_reg - зареєструватись як тренер
/cancel_workout - відмінити тренування
"""

TRAINERS_COMMAND = """
/change_price - змінити ціну на тренування
/change_schedule - змінити час роботи
/change_number - змінити номер телефону
/change_desc - змінити резюме
/change_photo - змінити фото 
/work_out - вибрати собі тренера
/see_work_schedule - подивитись графік роботи
/cancel_training - відмінити тренування з тренером
"""

CLIENT_COMMANDS_LIST = ["/start", "/help", "/trainer_reg"]

TRAINER_COMMANDS_LIST = ["/start", "/change_price", "/change_schedule", "/change_number", "/change_desc",
                         "/change_photo", "/see_work_schedule", "/for_trainers"]

TRAINER_DESCRIPTION = ("Мене звати {}.\nОсь мої заслуги: {}!\nМій щоденний графік роботи: {}.\n"
                       "Ціна одного тренування становить - {} грн, мій номер телефону - {}!\n"
                       "Якщо ви хочете потренуватись разово, натисніть 'Записатись на разове тренування'.\n"
                       "Якщо ви хочете тренуватись постійно, натисніть 'Записатись на постіній основі'.\n"
                       "Якщо ви хочете подивитись інших тренерів, натисніть 'next >'.")
