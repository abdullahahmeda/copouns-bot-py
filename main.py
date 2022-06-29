from dotenv import load_dotenv

load_dotenv()

from bot import updater, dispatcher
from telegram import Update, ReplyKeyboardRemove, ReplyKeyboardMarkup
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    DispatcherHandlerStop,
    MessageHandler,
    Filters,
    ConversationHandler,
)
import constants
import db
from mysql.connector import IntegrityError
import state
from utils import chunk
import send_message_conversation as SendMessageConversation

ADMIN_IDS = {929722187, 661745675}  # Abdullah Ahmed

print("Bot started")
updater.start_polling()


def handleAnyMessage(update: Update, context: CallbackContext):
    print(update.message.from_user)
    if "mode" not in context.user_data:
        context.user_data["mode"] = constants.BotModes.normal
    from_user = update.message.from_user
    try:
        db.insertUser(
            {
                "id": from_user.id,
                "name": from_user.full_name,
                "username": from_user.username,
            }
        )
    except IntegrityError:
        pass  # user already exists, ignore


all_handler = MessageHandler(Filters.all, handleAnyMessage)
dispatcher.add_handler(all_handler, -99)


def start(update: Update, context: CallbackContext):
    visible_words = [k for k, v in state.getWords().items() if v["visible"] == True]
    context.bot.send_message(
        update.effective_chat.id,
        constants.Messages.start,
        reply_markup=ReplyKeyboardMarkup(list(chunk(visible_words, 3))),
    )


start_handler = CommandHandler("start", start)
dispatcher.add_handler(start_handler)


def list_all(update: Update, context: CallbackContext):
    visible_words = [k for k, v in state.getWords().items() if v["visible"] == True]
    context.bot.send_message(
        update.effective_chat.id,
        constants.Messages.list_all,
        reply_markup=ReplyKeyboardMarkup(list(chunk(visible_words, 3))),
    )


list_all_handler = CommandHandler("list", list_all)
dispatcher.add_handler(list_all_handler)


def admin(update: Update, context: CallbackContext):
    if update.message.from_user.id not in ADMIN_IDS:
        return
    if context.user_data["mode"] == constants.BotModes.normal:
        context.user_data["mode"] = constants.BotModes.admin
        context.bot.send_message(
            update.effective_chat.id,
            constants.Messages.switched_to_admin,
            reply_markup=constants.Markups.admin,
        )
    elif context.user_data["mode"] == constants.BotModes.admin:
        context.bot.send_message(
            update.effective_chat.id,
            constants.Messages.already_in_mode,
            reply_markup=constants.Markups.admin,
        )
    raise DispatcherHandlerStop()


admin_handler = CommandHandler("admin", admin)
dispatcher.add_handler(admin_handler, -1)


def normal(update: Update, context: CallbackContext):
    if update.message.from_user.id not in ADMIN_IDS:
        return
    if context.user_data["mode"] == constants.BotModes.admin:
        context.user_data["mode"] = constants.BotModes.normal
        context.bot.send_message(
            update.effective_chat.id,
            constants.Messages.switched_to_normal,
            reply_markup=ReplyKeyboardRemove(),
        )
    elif context.user_data["mode"] == constants.BotModes.normal:
        context.bot.send_message(
            update.effective_chat.id,
            constants.Messages.already_in_mode,
            reply_markup=ReplyKeyboardRemove(),
        )
    raise DispatcherHandlerStop()


normal_handler = CommandHandler("normal", normal)
dispatcher.add_handler(normal_handler, -1)


def conversationFallback(update: Update, context: CallbackContext):
    context.bot.send_message(
        update.effective_chat.id, constants.Messages.mode_cancelled
    )
    return ConversationHandler.END


send_message_conversation_handler = ConversationHandler(
    [
        MessageHandler(
            Filters.regex("إرسال رسالة عامة لكل المشتركين"),
            SendMessageConversation.start,
        )
    ],
    {
        constants.ConversationsStates.RECEIVED_MESSAGE: [
            CommandHandler("cancel", SendMessageConversation.cancel),
            MessageHandler(
                Filters.all,
                SendMessageConversation.receivedMessage,
            ),
        ]
    },
    [MessageHandler(Filters.all, conversationFallback)],
)
dispatcher.add_handler(send_message_conversation_handler, -1)


def updateWords(update: Update, context: CallbackContext):
    if context.user_data["mode"] != constants.BotModes.admin:
        return
    state.updateWords()
    context.bot.send_message(update.effective_chat.id, constants.Messages.words_updated)
    raise DispatcherHandlerStop()


update_words_handler = MessageHandler(Filters.regex("تحديث الأقسام"), updateWords)
dispatcher.add_handler(update_words_handler, -1)


def message(update: Update, context: CallbackContext):
    message = update.message.text
    words = state.getWords()

    if not words.get(message):
        context.bot.send_message(
            update.effective_chat.id,
            constants.Messages.word_not_found,
            reply_markup=ReplyKeyboardRemove(),
        )
        return

    context.bot.send_message(update.effective_chat.id, words[message]["message"])


message_handler = MessageHandler(Filters.all, message)
dispatcher.add_handler(message_handler)

updater.idle()
