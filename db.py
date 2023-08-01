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
            result = cursor.fetchone()

        return result

    def get_trainer(self, person_id):
        with self.connection.cursor() as cursor:
            sql = "SELECT `person_id` FROM `trainers`"
            cursor.execute(sql)
            result = cursor.fetchone()

        return result

    def add_people(self, user_id, name):
        with self.connection.cursor() as cursor:
            sql = "INSERT INTO `people` (`user_id`, `name`) VALUES(%s, %s)"
            cursor.execute(sql, (user_id, name))
        self.connection.commit()

    def add_trainer(self, person_id, description, photo, price, schedule):
        with self.connection.cursor() as cursor:
            sql = ("INSERT INTO `trainers` (`person_id`, `description`, `photo`, `price`, `schedule`)"
                   "VALUES(%s, %s, %s, %s, %s)")
            cursor.execute(sql, (person_id, description, photo, price, schedule))
        self.connection.commit()
