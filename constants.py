from telegram import ReplyKeyboardMarkup


class Messages:
    start = """أهلاً بك!
هذا البوت يقوم بعرض أكود الخصومات للمتاجر.
"""

    list_all = "قم باختيار القسم"

    switched_to_admin = "تم التحويل إلى وضع الأدمن"
    switched_to_normal = "تم التحويل إلى الوضع العادي"
    already_in_mode = "أنت في هذا الوضع بالفعل"

    word_not_found = """هذا القسم غير موجود في قاعدة البيانات
يمكنك اختيار قسم من الأقسام المتاحة، أو جرب كتابة قسم آخر."""

    words_updated = "تم تحديث الأقسام بنجاح"

    enter_message = "قم بكتابة الرسالة المراد إرسالها "
    send_message_cancelled = "تم إلغاء وضع إرسال الرسالة"
    will_send_messages = "سيتم إرسال الرسائل"

    mode_cancelled = "تم الخروج من الوضع الحالي"


class BotModes:
    normal = "normal"
    admin = "admin"


class Markups:
    admin = ReplyKeyboardMarkup([["إرسال رسالة عامة لكل المشتركين"], ["تحديث الأقسام"]])


class ConversationsStates:
    RECEIVED_MESSAGE = 0
