import datetime


def hours(interim: str, day):
    day_now = datetime.date.today()
    time = interim.split('-')
    if str(day_now) == day:
        time_now = datetime.datetime.now().time()
        result = rounding(time_now)
        temp = str(time_now)
        temp.split(":")
        if temp[1] != "00":
            time_format = "%H:%M"
            time1 = datetime.datetime.strptime(result, time_format)
            rounded_time = (time1.replace(second=0, microsecond=0, minute=0) + datetime.timedelta(hours=1)).time()
            start_time = datetime.datetime.strptime(rounding(rounded_time), "%H:%M")
        else:
            start_time = datetime.datetime.strptime(time[0].strip(), "%H:%M")
    end_time = datetime.datetime.strptime(time[1].strip(), "%H:%M")
    time_step = datetime.timedelta(hours=1)
    time_list = []
    current_time = start_time
    while current_time < end_time:
        time_list.append(current_time.strftime("%H:%M"))
        current_time += time_step
    return time_list


def five_days():
    today = datetime.datetime.today()
    days = [(today + datetime.timedelta(days=i)).strftime('%Y-%m-%d') for i in range(5)]
    return days


def rounding(time_now):
    time_now = str(time_now)
    time_now = time_now.split(":")
    return time_now[0] + ":" + time_now[1]
