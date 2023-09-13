import config
import json


class Database:

    def __init__(self):
        self.connection = config.DB_CONFIG

    def get_people(self, user_id):
        with self.connection.cursor() as cursor:
            sql = (f"SELECT `id`, `user_id`, `name` "
                   f"FROM `people`"
                   f"WHERE {user_id} = `user_id`")
            cursor.execute(sql)
            result = cursor.fetchone()

        return result

    def get_trainer(self, person_id):
        with self.connection.cursor() as cursor:
            sql = ("SELECT `person_id` "
                   "FROM `trainers` "
                   "WHERE `person_id` = %s")
            cursor.execute(sql, person_id)
            result = cursor.fetchone()

        return result

    def add_people(self, user_id, name):
        with self.connection.cursor() as cursor:
            sql = "INSERT INTO `people` (`user_id`, `name`) VALUES(%s, %s)"
            cursor.execute(sql, (user_id, name))
        self.connection.commit()

    def add_trainer(self, person_id: int, description: str, photo: str, price: int, schedule: str,
                    phone_number: str):
        with self.connection.cursor() as cursor:
            sql = ("INSERT INTO `trainers` (`person_id`, `description`, `photo`, `price`, `schedule`, `phone_number`)"
                   "VALUES(%s, %s, %s, %s, %s, %s)")
            cursor.execute(sql, (person_id, description, photo, price, schedule, phone_number))
        self.connection.commit()

    def get_trainers(self, offset, user_id):
        with self.connection.cursor() as cursor:
            if user_id is None or offset > 0:
                sql = (f"SELECT `person_id`, `name`, `description`, `photo`, `price`, `schedule`, `phone_number` "
                       f"FROM `people` "
                       f"LEFT JOIN `trainers` ON people.id = trainers.person_id "
                       f"LIMIT 1 OFFSET {offset}")
            elif offset == 0:
                sql = (f"SELECT `person_id`, `name`, `description`, `photo`, `price`, `schedule`, `phone_number` "
                       f"FROM `people` "
                       f"LEFT JOIN `trainers` ON people.id = trainers.person_id "
                       f"LIMIT 1 OFFSET {offset}")
                # f"WHERE `person_id` <> {user_id}")
            else:
                sql = (f"SELECT `person_id`, `name`, `description`, `photo`, `price`, `schedule`, `phone_number` "
                       f"FROM `people` "
                       f"LEFT JOIN `trainers` ON people.id = trainers.person_id "
                       f"WHERE `person_id` <> {user_id} "
                       f"LIMIT 1 OFFSET {offset}")
            cursor.execute(sql)
            result = cursor.fetchone()
        return result

    def add_to_timetable(self, trainer_id, day, time, value):
        with self.connection.cursor() as cursor:
            sql = ("SELECT `schedule` "
                   "FROM `timetable` "
                   "WHERE `trainer_id` = %s")
            cursor.execute(sql, (trainer_id,))
            result = cursor.fetchone()

            if result:
                current_schedule = json.loads(result['schedule'])
            else:
                current_schedule = {}

            if day not in current_schedule:
                current_schedule[day] = {}
            if time not in current_schedule[day]:
                current_schedule[day][time] = [value]
            else:
                current_schedule[day][time].append(value)

            sql = ("INSERT INTO `timetable` (`trainer_id`, `schedule`) "
                   "VALUES (%s, %s) "
                   "ON DUPLICATE KEY UPDATE `schedule` = VALUES(`schedule`)")
            cursor.execute(sql, (trainer_id, json.dumps(current_schedule)))

        self.connection.commit()

    def get_schedule(self, trainer_id=None):
        with self.connection.cursor() as cursor:
            if trainer_id is None:
                sql = ("SELECT `schedule` "
                       "FROM `timetable`")
            else:
                sql = (f"SELECT `schedule` "
                       f"FROM `timetable` "
                       f"WHERE `trainer_id` = {trainer_id}")
            cursor.execute(sql)
            result = cursor.fetchall()
        return result

    def change_trainer_info(self, trainer_id, trainer_command, new_info):
        with self.connection.cursor() as cursor:
            base_sql = "UPDATE `trainers` SET field = %s WHERE `person_id` = %s"
            if trainer_command == "/change_price":
                base_sql = base_sql.replace("field", "`price`")
            elif trainer_command == "/change_schedule":
                base_sql = base_sql.replace("field", "`schedule`")
            elif trainer_command == "/change_number":
                base_sql = base_sql.replace("field", "`phone_number`")
            elif trainer_command == "/change_desc":
                base_sql = base_sql.replace("field", "`description`")
            elif trainer_command == "/change_photo":
                base_sql = base_sql.replace("field", "`photo`")
            cursor.execute(base_sql, (new_info, trainer_id))
        self.connection.commit()

    def get_standing_schedule(self, trainer_id):
        with self.connection.cursor() as cursor:
            sql = ("SELECT `schedule`, `standing_schedule` "
                   "FROM `timetable` "
                   "WHERE `trainer_id` = %s")
            cursor.execute(sql, (trainer_id,))
        result = cursor.fetchall()

        return result

    def add_standing_schedule(self, trainer_id, time, days, client_name):
        from utils import DAYS_OF_WEEK_DICT
        with self.connection.cursor() as cursor:
            result = Database.get_standing_schedule(self, trainer_id)
            if result[0]['standing_schedule'] is not None:
                current_schedule = json.loads(result[0]['standing_schedule'])
            else:
                current_schedule = {}

            for day in days:
                for key, value in DAYS_OF_WEEK_DICT.items():
                    if day == value:
                        if len(current_schedule) == 0 or str(key) not in current_schedule.keys():
                            current_schedule.setdefault(key, {time: client_name})
                        else:
                            current_schedule[str(key)].setdefault(time, client_name)

            sql = ("INSERT INTO `timetable` (`trainer_id`, `schedule`, `standing_schedule`) "
                   "VALUES (%s, %s, %s) "
                   "ON DUPLICATE KEY UPDATE `standing_schedule` = VALUES(`standing_schedule`)")
            cursor.execute(sql, (trainer_id, result[0]['schedule'], json.dumps(current_schedule)))

        self.connection.commit()
