from mysql.connector import connect, IntegrityError
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
CREATE TABLE IF NOT EXISTS `words` (
  `id` INT(11) PRIMARY KEY AUTO_INCREMENT,
  `word` VARCHAR(255) UNIQUE NOT NULL,
  `visible` BOOL NOT NULL DEFAULT 1,
  `order` INT(11),
  `times_used` INT(11) NOT NULL DEFAULT 0
#  `synonym_id` INT(11),
#  FOREIGN KEY (`synonym_id`) REFERENCES `words` (`id`) ON DELETE CASCADE
)
"""
)

cursor.execute(
    """
CREATE TABLE IF NOT EXISTS `messages` (
  `id` INT(11) PRIMARY KEY AUTO_INCREMENT,
  `message` TEXT NOT NULL,
  `word_id` INT(11),
  `order` INT(11),

  FOREIGN KEY (`word_id`) REFERENCES `words` (`id`) ON DELETE SET NULL,
  INDEX word_id_idx (`word_id`)
)
"""
)

cursor.execute(
    """
CREATE TABLE IF NOT EXISTS `commands_messages` (
  command VARCHAR(255) PRIMARY KEY,
  message TEXT NOT NULL 
)
"""
)

try:
    cursor.execute(
        "INSERT INTO commands_messages (command, message) VALUES (%s, %s)",
        ("start", "قم بتغيير هذه الرسالة"),
    )
    cursor.execute(
        "INSERT INTO commands_messages (command, message) VALUES (%s, %s)",
        ("list", "قم بتغيير هذه الرسالة"),
    )
except IntegrityError:
    pass


connection.commit()
cursor.close()
connection.close()


def getWords():
    connection = connect(**config)
    cursor = connection.cursor()
    cursor.execute(
        """
    SELECT words.id, words.word, words.visible, messages.message FROM words INNER JOIN messages ON words.id = messages.word_id ORDER BY words.order, messages.order
    """
    )
    a = {}
    for (id, word, visible, message) in cursor:
        a[word] = a.get(
            word,
            {
                "id": id,
                "visible": bool(int(visible)),
            },
        )
        arr = a[word].get("messages", [])
        arr.append(message)
        a[word]["messages"] = arr
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


def incrementTimesUsed(id: int, by: int = 1):
    connection = connect(**config)
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE words SET times_used = %s + times_used WHERE id = %s",
        (by, id),
    )
    connection.commit()
    cursor.close()
    connection.close()


def getCommandsMessages():
    connection = connect(**config)
    cursor = connection.cursor(dictionary=True)
    cursor.execute(
        """
    SELECT * FROM commands_messages
    """
    )
    a = {}
    for command_message in cursor:
        a[command_message["command"]] = command_message["message"]
    cursor.close()
    connection.close()
    return a


def updateCommandMessage(command, message):
    connection = connect(**config)
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE commands_messages SET message = %s WHERE command = %s",
        (message, command),
    )
    connection.commit()
    cursor.close()
    connection.close()
