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

    def get_people_chat_id(self, name):
        with self.connection.cursor() as cursor:
            sql = ("SELECT `user_id` "
                   "FROM `people` "
                   "WHERE `name` = %s")
            cursor.execute(sql, (name,))
            result = cursor.fetchone()

        return result

    def get_trainer_name(self, trainer_id):
        with self.connection.cursor() as cursor:
            sql = ("SELECT `name` "
                   "FROM `people` "
                   "LEFT JOIN `trainers` ON people.id = trainers.person_id "
                   "WHERE trainers.person_id = %s")
            cursor.execute(sql, (trainer_id,))
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

    def get_trainer_info(self, user_id, offset):
        with self.connection.cursor() as cursor:
            sql = ("SELECT `person_id`, `name`, `description`, `photo`, `price`, `schedule`, `phone_number` "
                   "FROM `people` "
                   "LEFT JOIN `trainers` ON people.id = trainers.person_id "
                   "WHERE `description` IS NOT NULL ")
            if user_id is not None:
                sql = sql + " " + f"AND `person_id` <> {user_id}"
            cursor.execute(sql + " " + f"LIMIT 1 OFFSET {offset}")
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
                current_schedule[day][time] = value
            else:
                current_schedule[day][time].append(value)

            sql = ("INSERT INTO `timetable` (`trainer_id`, `schedule`) "
                   "VALUES (%s, %s) "
                   "ON DUPLICATE KEY UPDATE `schedule` = VALUES(`schedule`)")
            cursor.execute(sql, (trainer_id, json.dumps(current_schedule)))

        self.connection.commit()

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

    def get_schedule(self, trainer_id=""):
        with self.connection.cursor() as cursor:
            if trainer_id == "":
                sql = ("SELECT `trainer_id`, `schedule`, `standing_schedule` "
                       "FROM `timetable`")
                cursor.execute(sql)
                result = cursor.fetchall()
            else:
                sql = ("SELECT `schedule`, `standing_schedule` "
                       "FROM `timetable` "
                       "WHERE `trainer_id` = %s")
                cursor.execute(sql, (trainer_id,))
                result = cursor.fetchone()

        return result

    def add_standing_schedule(self, trainer_id, time, days, client_name):
        with self.connection.cursor() as cursor:
            result = self.get_schedule(trainer_id)
            if type(result) == list and result[0]['standing_schedule'] is not None:
                current_schedule = json.loads(result[0]['standing_schedule'])
            else:
                current_schedule = {}

            for day in days:
                if len(current_schedule) == 0 or day not in current_schedule.keys():
                    current_schedule[day] = {time: client_name}
                else:
                    current_schedule[str(day)].setdefault(time, client_name)

            sql = ("INSERT INTO `timetable` (`trainer_id`, `schedule`, `standing_schedule`) "
                   "VALUES (%s, %s, %s) "
                   "ON DUPLICATE KEY UPDATE `standing_schedule` = VALUES(`standing_schedule`)")
            if result:
                cursor.execute(sql, (trainer_id, result[0]['schedule'], json.dumps(current_schedule)))
            else:
                cursor.execute(sql, (trainer_id, json.dumps({}), json.dumps(current_schedule)))

        self.connection.commit()

    def update_schedule(self, trainer_id, data):
        with self.connection.cursor() as cursor:
            sql = ("UPDATE `timetable` "
                   "SET `schedule` = %s "
                   "WHERE `trainer_id` = %s")
            cursor.execute(sql, (json.dumps(data), trainer_id))
        self.connection.commit()

    def get_trainer_id(self, user_id):
        with self.connection.cursor() as cursor:
            sql = ("SELECT `person_id` "
                   "FROM `trainers` "
                   "LEFT JOIN `people` ON people.id = trainers.person_id "
                   "WHERE people.user_id = %s")
            cursor.execute(sql, (user_id,))
            result = cursor.fetchone()

        return result['person_id']
