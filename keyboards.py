from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


def main_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🔍 Проверить"), KeyboardButton(text="📝 Подать жалобу")],
        [KeyboardButton(text="❓ FAQ"), KeyboardButton(text="📢 Канал")],
    ], resize_keyboard=True)


def check_method_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 По @username", callback_data="check_username")],
        [InlineKeyboardButton(text="🆔 По User ID", callback_data="check_id")],
        [InlineKeyboardButton(text="📱 По номеру телефона", callback_data="check_phone")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_main")],
    ])


def subscribe_kb(channel_link: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Подписаться на канал", url=channel_link)],
        [InlineKeyboardButton(text="✅ Я подписался", callback_data="check_subscription")],
    ])


def cancel_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]
    ])


def report_proof_kb(report_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Одобрить", callback_data=f"approve_{report_id}")],
        [InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{report_id}")],
    ])


def admin_panel_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Ожидающие жалобы", callback_data="admin_pending")],
        [InlineKeyboardButton(text="🗃 Скам-база", callback_data="admin_scambase")],
        [InlineKeyboardButton(text="🗑 Удалить из базы", callback_data="admin_delete")],
        [InlineKeyboardButton(text="➕ Добавить вручную", callback_data="admin_add")],
    ])


def skip_field_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏭ Пропустить", callback_data="skip_field")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")],
    ])


def finish_proof_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Готово, отправить", callback_data="finish_proof")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")],
    ])
