import datetime
import locale
import json


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


def get_general_dict(all_schedule):
    locale.setlocale(locale.LC_TIME, 'uk_UA.utf8')
    days = get_next_five_days()
    general_dict = {}
    standing_schedule = {}
    schedule = {}
    if all_schedule:
        if isinstance(all_schedule['schedule'], str):
            schedule = json.loads(all_schedule['schedule'])
        if isinstance(all_schedule['standing_schedule'], str):
            standing_schedule = json.loads(all_schedule['standing_schedule'])

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


def get_trainers_id(client_name, trainer_info):
    trainers_id_list = []
    for el in trainer_info:
        temp = json.loads(el['schedule']) | json.loads(el['standing_schedule'])
        for value in temp.values():
            if client_name in value.values() and el['trainer_id'] not in trainers_id_list:
                trainers_id_list.append(el['trainer_id'])

    return trainers_id_list

