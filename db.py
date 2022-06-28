from mysql.connector import connect
import os

config = {
    "host": os.environ["DB_HOST"],
    "user": os.environ["DB_USER"],
    "password": os.environ["DB_PASSWORD"],
    "database": os.environ["DB_NAME"],
    "charset": "utf8",
}

connection = connect(**config)
cursor = connection.cursor(buffered=True)

cursor.execute(
    """
CREATE TABLE IF NOT EXISTS `users` (
  `telegram_id` VARCHAR(100) PRIMARY KEY,
  `name` VARCHAR(255),
  `username` VARCHAR(100)
)
"""
)

cursor.execute(
    """
CREATE TABLE IF NOT EXISTS `messages` (
  `id` INT(11) PRIMARY KEY AUTO_INCREMENT,
  `message` TEXT NOT NULL
)
"""
)

cursor.execute(
    """
CREATE TABLE IF NOT EXISTS words (
  `word` VARCHAR(255) PRIMARY KEY,
  `message_id` INT(11),
  FOREIGN KEY (`message_id`) REFERENCES `messages` (`id`) ON DELETE SET NULL
)
"""
)
connection.commit()
cursor.close()
connection.close()


def getWords():
    connection = connect(**config)
    cursor = connection.cursor()
    cursor.execute(
        """
    SELECT words.word, messages.message FROM words LEFT JOIN messages ON words.message_id = messages.id
    """
    )
    a = {}
    for (word, message) in cursor:
        a[word] = message
    cursor.close()
    connection.close()
    return a


def getUsers():
    connection = connect(**config)
    cursor = connection.cursor(dictionary=True)
    cursor.execute(
        """
    SELECT * FROM users
    """
    )
    a = list(cursor)
    cursor.close()
    connection.close()
    return a


def insertUser(data):
    connection = connect(**config)
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO users(telegram_id, name, username) VALUES (%s, %s, %s)",
        (data["id"], data["name"], data["username"]),
    )
    connection.commit()
    cursor.close()
    connection.close()
