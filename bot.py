import os
from telegram.ext import Updater


updater = Updater(token=os.environ["BOT_TOKEN"], use_context=True)

updater.bot.set_my_commands([("start", "تعريف بالبوت"), ("list", "عرض الأقسام")])

dispatcher = updater.dispatcher
