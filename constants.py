from telegram import ReplyKeyboardMarkup


class Messages:
    start = """أهلاً بك!
هذا البوت يقوم بعرض أكود الخصومات للمتاجر.
"""

    list_all = "قم باختيار المتجر"

    switched_to_admin = "تم التحويل إلى وضع الأدمن"
    switched_to_normal = "تم التحويل إلى الوضع العادي"
    already_in_mode = "أنت في هذا الوضع بالفعل"

    send_public_message = "إرسال رسالة عامة لكل المشتركين"

    update_words = "تحديث المتاجر"

    word_not_found = """هذا القسم غير موجود في قاعدة البيانات
يمكنك اختيار قسم من الأقسام المتاحة، أو جرب كتابة قسم آخر."""

    words_updated = "تم تحديث المتاجر بنجاح"

    enter_message = "قم بكتابة الرسالة المراد إرسالها "
    send_message_cancelled = "تم إلغاء وضع إرسال الرسالة"
    will_send_messages = "سيتم إرسال الرسائل"

    mode_cancelled = "تم الخروج من الوضع الحالي"

    prev_page = "الصفحة السابقة ⏮"
    next_page = "الصفحة التالية ⏭"

    edit_command_message = "تعديل رسالة لأمر"
    choose_command_to_change_message = "اختر الأمر المراد تعديل رسالته"
    enter_new_command_message = "أرسل الرسالة الجديدة للأمر"
    command_message_changed = "تم تحديث الرسالة بنجاح"

    command_does_not_exist = "هذا الأمر غير موجود"


class BotModes:
    normal = "normal"
    admin = "admin"


class Markups:
    admin = ReplyKeyboardMarkup(
        [
            [Messages.send_public_message],
            [Messages.update_words],
            [Messages.edit_command_message],
        ]
    )


class ConversationsStates:
    RECEIVED_MESSAGE = 0

    CHOOSED_COMMAND = 1
    RECEIVED_COMMAND_MESSAGE = 2
