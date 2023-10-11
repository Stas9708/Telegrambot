import datetime
import locale
import json
from db import Database

db = Database()


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


def get_general_dict(trainer_id):
    locale.setlocale(locale.LC_TIME, 'uk_UA.utf8')
    general_schedule = db.get_schedule(trainer_id)
    days = get_next_five_days()
    general_dict = {}
    standing_schedule = {}
    schedule = {}
    if general_schedule:
        if len(general_schedule[0]['schedule']) > 0:
            schedule = json.loads(general_schedule[0]['schedule'])
        if general_schedule[0]['standing_schedule'] is not None:
            standing_schedule = json.loads(general_schedule[0]['standing_schedule'])

    if schedule:
        day_now = datetime.date.today()
        for key, value in schedule.items():
            date = datetime.datetime.strptime(key, '%Y-%m-%d').date()
            if date >= day_now:
                general_dict[key] = value

    if standing_schedule:
        days_of_week_list = [datetime.datetime.strptime(day, '%Y-%m-%d').strftime('%A').capitalize()
                             for day in days]
        for k, v in standing_schedule.items():
            if k not in days_of_week_list:
                continue
            else:
                index = days_of_week_list.index(k)
                temp = general_dict.setdefault(days[index], {})
                general_dict[days[index]] = temp | v

    return general_dict


def get_trainers_name(client_name):
    trainers_name_list = []
    trainers_id = db.get_schedule()
    for el in trainers_id:
        result = get_general_dict(el['trainer_id'])
        for value in result.values():
            if client_name in value.values():
                trainers_name_list.append({el['trainer_id']: db.get_trainer_name(el['trainer_id'])['name']})
                break
    return trainers_name_list
