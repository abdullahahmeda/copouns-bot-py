from dotenv import load_dotenv

load_dotenv()

from bot import updater, dispatcher
from telegram import Update, ReplyKeyboardRemove, ReplyKeyboardMarkup, ParseMode
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
import edit_command_message_conversation as EditCommandMessageConversation

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
    commands_messages = state.getCommandsMessages()
    visible_words = [k for k, v in state.getWords().items() if v["visible"] == True]
    if len(visible_words) > 90:
        visible_words = visible_words[:90]
        context.user_data["page"] = 1
        visible_words.append(constants.Messages.next_page)
    context.bot.send_message(
        update.effective_chat.id,
        commands_messages["start"],
        reply_markup=ReplyKeyboardMarkup(list(chunk(visible_words, 3))),
        parse_mode=ParseMode.MARKDOWN_V2,
    )


start_handler = CommandHandler("start", start)
dispatcher.add_handler(start_handler)


def list_all(update: Update, context: CallbackContext):
    commands_messages = state.getCommandsMessages()
    visible_words = [k for k, v in state.getWords().items() if v["visible"] == True]
    if len(visible_words) > 90:
        visible_words = visible_words[:90]
        context.user_data["page"] = 1
        visible_words.append("الصفحة التالية ⏭")
    context.bot.send_message(
        update.effective_chat.id,
        commands_messages["list"],
        reply_markup=ReplyKeyboardMarkup(list(chunk(visible_words, 3))),
        parse_mode=ParseMode.MARKDOWN_V2,
    )


list_all_handler = CommandHandler("list", list_all)
dispatcher.add_handler(list_all_handler)


def cancel(update: Update, context: CallbackContext):
    context.bot.send_message(
        update.effective_chat.id,
        constants.Messages.send_message_cancelled,
        reply_markup=constants.Markups.admin,
    )
    raise DispatcherHandlerStop(ConversationHandler.END)


def conversationFallback(update: Update, context: CallbackContext):
    context.bot.send_message(
        update.effective_chat.id,
        constants.Messages.mode_cancelled,
        reply_markup=constants.Markups.admin,
    )
    return ConversationHandler.END


edit_command_message_conversation_handler = ConversationHandler(
    [
        MessageHandler(
            Filters.regex(constants.Messages.edit_command_message),
            EditCommandMessageConversation.start,
        )
    ],
    {
        constants.ConversationsStates.CHOOSED_COMMAND: [
            MessageHandler(
                Filters.all & ~Filters.command,
                EditCommandMessageConversation.choosedComamnd,
            ),
        ],
        constants.ConversationsStates.RECEIVED_COMMAND_MESSAGE: [
            MessageHandler(
                Filters.all & ~Filters.command("cancel"),
                EditCommandMessageConversation.receivedMessage,
            )
        ],
    },
    [
        CommandHandler("cancel", cancel),
        MessageHandler(Filters.all, conversationFallback),
    ],
)

dispatcher.add_handler(edit_command_message_conversation_handler, -1)


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


send_message_conversation_handler = ConversationHandler(
    [
        MessageHandler(
            Filters.regex(constants.Messages.send_public_message),
            SendMessageConversation.start,
        )
    ],
    {
        constants.ConversationsStates.RECEIVED_MESSAGE: [
            MessageHandler(
                Filters.all & ~Filters.command,
                SendMessageConversation.receivedMessage,
            ),
        ]
    },
    [
        CommandHandler("cancel", cancel),
        MessageHandler(Filters.all, conversationFallback),
    ],
)
dispatcher.add_handler(send_message_conversation_handler, -1)


def updateWords(update: Update, context: CallbackContext):
    if context.user_data["mode"] != constants.BotModes.admin:
        return
    state.updateWords()
    context.bot.send_message(update.effective_chat.id, constants.Messages.words_updated)
    raise DispatcherHandlerStop()


update_words_handler = MessageHandler(
    Filters.regex(constants.Messages.update_words), updateWords
)
dispatcher.add_handler(update_words_handler, -1)


def nextPage(update: Update, context: CallbackContext):
    all_visible_words = [k for k, v in state.getWords().items() if v["visible"] == True]
    visible_words = all_visible_words
    if len(visible_words) > 90:
        page = context.user_data.get("page", 1) + 1
        context.user_data["page"] = page
        visible_words = visible_words[(page - 1) * 90 : page * 90]
        visible_words.append(constants.Messages.prev_page)
        if page * 90 < len(all_visible_words):
            visible_words.append(constants.Messages.next_page)
    context.bot.send_message(
        update.effective_chat.id,
        "أكواد أخرى",
        reply_markup=ReplyKeyboardMarkup(list(chunk(visible_words, 3))),
    )


next_page_handler = MessageHandler(
    Filters.regex(constants.Messages.next_page), nextPage
)
dispatcher.add_handler(next_page_handler)


def prevPage(update: Update, context: CallbackContext):
    all_visible_words = [k for k, v in state.getWords().items() if v["visible"] == True]
    visible_words = all_visible_words
    if len(visible_words) > 90:
        page = context.user_data.get("page", 2) - 1
        context.user_data["page"] = page
        visible_words = visible_words[(page - 1) * 90 : page * 90]
        if page > 1:
            visible_words.append(constants.Messages.prev_page)
        visible_words.append(constants.Messages.next_page)
    context.bot.send_message(
        update.effective_chat.id,
        "أكواد أخرى",
        reply_markup=ReplyKeyboardMarkup(list(chunk(visible_words, 3))),
    )


prev_page_handler = MessageHandler(
    Filters.regex(constants.Messages.prev_page), prevPage
)
dispatcher.add_handler(prev_page_handler)


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
    try:
        db.incrementTimesUsed(words[message]["id"])
    except Exception as error:
        print("couldn't increment times used")
        print(words[message])
        print(error)
    for word in words[message]["messages"]:
        context.bot.send_message(update.effective_chat.id, word)


message_handler = MessageHandler(Filters.all, message)
dispatcher.add_handler(message_handler)

updater.idle()
