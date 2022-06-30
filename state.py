"""
This file contains the global state.
"""

from db import getWords as getWordsFromDb

words = getWordsFromDb()


def getWords():
    global words
    return words


def updateWords():
    global words
    words = getWordsFromDb()
