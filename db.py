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

    def add_trainer(self, trainer_name, description, photo):
        with self.cursor:
            sql = "INSERT INTO `trainer` (`trainer_name`, `description`, `photo`) VALUES(%s, %s, %s)"
            self.cursor.execute(sql, (trainer_name, description, photo))
        self.connection.commit()

    def add_client(self, client_name):
        with self.cursor:
            sql = "INSERT INTO `client` (`client_name`) VALUES(%s)"
            self.cursor.execute(sql, client_name)
        self.connection.commit()

