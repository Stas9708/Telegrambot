import config


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

    def add_to_timetable(self, trainer_id, data):
        with self.connection.cursor() as cursor:
            sql = ("SELECT `trainer_id` "
                   "FROM `timetable` ")
            cursor.execute(sql)
            result = cursor.fetchall()
            for dictionary in result:
                if dictionary['trainer_id'] == trainer_id:
                    sql = ("UPDATE `timetable` "
                           "SET `schedule` = JSON_SET(`schedule`, '$', %s) "
                           "WHERE `trainer_id` = %s")
                    cursor.execute(sql, (data, trainer_id))
                    break
            else:
                sql = ("INSERT INTO `timetable` (`trainer_id`, `schedule`) "
                       "VALUES (%s, %s)")
                cursor.execute(sql, (trainer_id, data))
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
            if trainer_command == "/change_price":
                sql = ("UPDATE `trainers` "
                       "SET `price` = %s "
                       "WHERE `person_id` = %s")
            elif trainer_command == "/change_schedule":
                sql = ("UPDATE `trainers` "
                       "SET `schedule` = %s "
                       "WHERE `person_id` = %s")
            elif trainer_command == "/change_number":
                sql = ("UPDATE `trainers` "
                       "SET `phone_number` = %s "
                       "WHERE `person_id` = %s")
            elif trainer_command == "/change_desc":
                sql = ("UPDATE `trainers` "
                       "SET `description` = %s "
                       "WHERE `person_id` = %s")
            elif trainer_command == "/change_photo":
                sql = ("UPDATE `trainers` "
                       "SET `photo` = %s "
                       "WHERE `person_id` = %s")
            cursor.execute(sql, (new_info, trainer_id))
        self.connection.commit()
