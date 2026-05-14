from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from config import CHANNEL_ID


async def is_subscribed(bot: Bot, user_id: int) -> bool:
    """Проверить подписку пользователя на канал"""
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status not in ("left", "kicked", "banned")
    except TelegramBadRequest:
        return False
    except Exception:
        return False


def format_scammer_card(record: dict) -> str:
    """Форматировать карточку скамера"""
    lines = ["🚫 <b>МОШЕННИК НАЙДЕН В БАЗЕ</b>\n"]

    if record.get("telegram_id"):
        lines.append(f"🆔 ID: <code>{record['telegram_id']}</code>")
    if record.get("username"):
        lines.append(f"👤 Username: @{record['username']}")
    if record.get("phone"):
        lines.append(f"📱 Телефон: <code>{record['phone']}</code>")

    lines.append("")
    lines.append("🔴 <b>Репутация: мошенник.</b>")
    lines.append("Добавлен в скам-базу. Сделки недопустимы.")

    if record.get("description"):
        lines.append(f"\n📄 <b>Описание:</b>\n{record['description']}")

    if record.get("report_text"):
        lines.append(f"\n💬 <b>От пострадавшего:</b>\n<i>{record['report_text']}</i>")

    return "\n".join(lines)


def format_clean_card(query: str) -> str:
    """Форматировать карточку чистого пользователя"""
    return (
        f"🔎 Результат проверки: <code>{query}</code>\n\n"
        "⚪ <b>Репутация: чист.</b>\n"
        "Жалоб и скама не зафиксировано. Соблюдайте бдительность при сотрудничестве."
    )


def format_report_for_moderation(report: dict) -> str:
    """Форматировать жалобу для группы модерации"""
    lines = [
        "📨 <b>НОВАЯ ЖАЛОБА НА МОДЕРАЦИЮ</b>",
        f"🆔 ID жалобы: <code>{report['id']}</code>",
        f"👤 От: @{report.get('username', 'нет')} (<code>{report['user_id']}</code>)",
        "",
    ]

    if report.get("target_telegram_id"):
        lines.append(f"🎯 Цель (ID): <code>{report['target_telegram_id']}</code>")
    if report.get("target_username"):
        lines.append(f"🎯 Цель (@): @{report['target_username']}")
    if report.get("target_phone"):
        lines.append(f"📱 Телефон: <code>{report['target_phone']}</code>")

    lines.append(f"\n📄 <b>Описание:</b>\n{report['description']}")

    if report.get("report_text"):
        lines.append(f"\n💬 <b>Текст жалобы:</b>\n<i>{report['report_text']}</i>")

    count = len(report.get("proof_file_ids") or [])
    lines.append(f"\n📎 Доказательств: {count} шт.")

    return "\n".join(lines)
