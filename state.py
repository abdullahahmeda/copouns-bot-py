"""
This file contains the global state.
"""

from db import (
    getWords as getWordsFromDb,
    getCommandsMessages as getCommandsMessagesFromDb,
)

words = getWordsFromDb()
commands_messages = getCommandsMessagesFromDb()


def getWords():
    global words
    return words


def updateWords():
    global words
    words = getWordsFromDb()


def getCommandsMessages():
    global commands_messages
    return commands_messages


def updateCommandsMessages():
    global commands_messages
    commands_messages = getCommandsMessagesFromDb()
