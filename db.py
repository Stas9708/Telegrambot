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
        self.cursor = self.connection.cursor()

    def add_trainer(self, trainer_name, description, photo, user_id, role, schedule):
        with self.cursor:
            sql = "INSERT INTO `trainer` (`trainer_name`, `description`, `photo`, `user_id`, `role`, `schedule`) VALUES(%s, %s, %s, %s, %s, %s)"
            self.cursor.execute(sql, (trainer_name, description, photo, user_id, role, schedule))
        self.connection.commit()

    def add_client(self, user_id, client_name, role):
        with self.cursor:
            sql = "INSERT INTO `client` (`user_id`, `name`, `role`) VALUES(%s, %s, %s)"
            self.cursor.execute(sql, (user_id, client_name, role))
        self.connection.commit()

    def check_role(self, user_id):
        with self.cursor:
            sql1 = "SELECT `user_id` FROM `client`"
            self.cursor.execute(sql1)
            client_result = self.cursor.fetchone()

            sql2 = "SELECT `user_id` FROM `trainer`"
            self.cursor.execute(sql2)
            trainer_result = self.cursor.fetchone()

            data = {
                'trainer': trainer_result,
                'client': client_result
            }
        return data
