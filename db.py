import pymysql.cursors


class Database:

    def __init__(self):
        self.connection = pymysql.connect(
            host="127.0.0.1",
            port=3306,
            user="root",
            password="123456",
            db="telegrambot_db",
            cursorclass=pymysql.cursors.DictCursor
        )

    def get_people(self, user_id):
        with self.connection.cursor() as cursor:
            sql = "SELECT `id`, `user_id` FROM `people`"
            cursor.execute(sql)
            result = cursor.fetchall()
        for el in result:
            if user_id == el['user_id']:
                return el
        return None

    def get_trainer(self, person_id):
        with self.connection.cursor() as cursor:
            sql = ("SELECT `person_id` "
                   "FROM `trainers` ")
            cursor.execute(sql)
            result = cursor.fetchone()

        return result

    def add_people(self, user_id, name):
        with self.connection.cursor() as cursor:
            sql = "INSERT INTO `people` (`user_id`, `name`) VALUES(%s, %s)"
            cursor.execute(sql, (user_id, name))
        self.connection.commit()

    def add_trainer(self, person_id: int, description: str, photo: bytes, price: int, schedule: str,
                    phone_number: str):
        with self.connection.cursor() as cursor:
            sql = ("INSERT INTO `trainers` (`person_id`, `description`, `photo`, `price`, `schedule`, `phone_number`)"
                   "VALUES(%s, %s, %s, %s, %s, %s)")
            cursor.execute(sql, (person_id, description, photo, price, schedule, phone_number))
        self.connection.commit()

    def get_trainers(self, offset):
        with self.connection.cursor() as cursor:
            if offset == 0:
                sql = ("SELECT `person_id`, `name`, `description`, `photo`, `price`, `schedule`, `phone_number` "
                       "FROM `people` "
                       "LEFT JOIN `trainers` ON people.id = trainers.person_id")
            else:
                sql = (f"SELECT `person_id`, `name`, `description`, `photo`, `price`, `schedule`, `phone_number` "
                       f"FROM `people` "
                       f"LEFT JOIN `trainers` ON people.id = trainers.person_id "
                       f"LIMIT 1 OFFSET {offset}")
            cursor.execute(sql)
            result = cursor.fetchone()
            return result



