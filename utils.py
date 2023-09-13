import datetime
import json
from db import Database

db = Database()

DAYS_OF_WEEK_DICT = {
    0: "Понеділок",
    1: "Вівторок",
    2: "Середа",
    3: "Четвер",
    4: "П'ятниця",
    5: "Субота",
    6: "Неділя"
}


def get_time_slots(interim: str, day=None):
    TIME_FORMAT = "%H:%M"
    day_now = datetime.date.today()
    time = interim.split('-')
    start_time = datetime.datetime.strptime(time[0].strip(), TIME_FORMAT)
    end_time = datetime.datetime.strptime(time[1].strip(), TIME_FORMAT)
    time_step = datetime.timedelta(hours=1)
    time_list = []
    current_time = start_time

    while current_time < end_time:
        time_list.append(current_time.strftime(TIME_FORMAT))
        current_time += time_step

    if str(day_now) == day:
        time_now = datetime.datetime.now()
        hours = time_now.hour
        minutes = time_now.minute
        if len(str(minutes)) == 1:
            minutes = "0" + str(minutes)
        time_now = str(hours) + ":" + str(minutes)
        for el in time_list:
            if time_now < el:
                time_list = time_list[time_list.index(el):]
                break

    return time_list


def get_next_five_days():
    today = datetime.datetime.today()
    days = [(today + datetime.timedelta(days=i)).strftime('%Y-%m-%d') for i in range(5)]

    return days


def get_dict(data):
    py_obj = None
    if len(data) == 1:
        py_obj = json.loads(data[0]['schedule'])
    else:
        for el in data:
            py_obj = json.loads(el['schedule'])
    return py_obj


def get_trainer_id(user_id):
    people_id = db.get_people(user_id)
    trainer_id = db.get_trainer(people_id['id'])
    if people_id is None or trainer_id is None:
        return None

    return trainer_id['person_id']
