from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    CallbackContext,
    ConversationHandler,
    JobQueue,
    DispatcherHandlerStop,
)
from constants import Messages, ConversationsStates, Markups
from state import getCommandsMessages, updateCommandsMessages
import db


def start(update: Update, context: CallbackContext):
    if context.user_data["mode"] != "admin":
        return
    commands_messages = getCommandsMessages()
    context.bot.send_message(
        update.effective_chat.id,
        Messages.choose_command_to_change_message,
        reply_markup=ReplyKeyboardMarkup([[x] for x in commands_messages.keys()]),
    )
    raise DispatcherHandlerStop(ConversationsStates.CHOOSED_COMMAND)


def choosedComamnd(update: Update, context: CallbackContext):
    if context.user_data["mode"] != "admin":
        return
    commands_messages = getCommandsMessages()
    choosed_command = update.message.text
    if choosed_command not in commands_messages:
        context.bot.send_message(
            update.effective_chat.id, Messages.command_does_not_exist
        )
        context.bot.send_message(update.effective_chat.id, Messages.mode_cancelled)
        raise DispatcherHandlerStop(ConversationHandler.END)

    context.user_data["command"] = choosed_command
    context.bot.send_message(
        update.effective_chat.id,
        Messages.enter_new_command_message,
        reply_markup=ReplyKeyboardRemove(),
    )
    raise DispatcherHandlerStop(ConversationsStates.RECEIVED_COMMAND_MESSAGE)


def receivedMessage(update: Update, context: CallbackContext):
    if context.user_data["mode"] != "admin":
        return
    commands_messages = getCommandsMessages()
    message = update.message.text_markdown_v2
    db.updateCommandMessage(context.user_data["command"], message)
    updateCommandsMessages()
    context.bot.send_message(
        update.effective_chat.id,
        Messages.command_message_changed,
        reply_markup=Markups.admin,
    )
    raise DispatcherHandlerStop(ConversationHandler.END)
