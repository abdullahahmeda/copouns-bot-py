from telegram import Update, error
from telegram.ext import (
    CallbackContext,
    ConversationHandler,
    JobQueue,
    DispatcherHandlerStop,
)
from constants import Messages, ConversationsStates
from db import getUsers
from utils import chunk


def _sendMessages(context: CallbackContext):
    job = context.job
    for user in job.context["users"]:
        try:
            context.bot.send_message(user["telegram_id"], job.context["message"])
        except:
            pass


def start(update: Update, context: CallbackContext):
    if context.user_data["mode"] != "admin":
        return
    context.bot.send_message(update.effective_chat.id, Messages.enter_message)
    raise DispatcherHandlerStop(ConversationsStates.RECEIVED_MESSAGE)


def receivedMessage(update: Update, context: CallbackContext):
    if context.user_data["mode"] != "admin":
        return
    message = update.message.text
    chat_id = update.effective_message.chat_id
    context.bot.send_message(update.effective_chat.id, Messages.will_send_messages)
    all_users = getUsers()
    all_users = list(chunk(all_users, 20))
    for index in range(len(all_users)):
        some_users = all_users[index]
        context.job_queue.run_once(
            _sendMessages,
            index,
            context={"users": some_users, "message": message},
        )
    raise DispatcherHandlerStop(ConversationHandler.END)
