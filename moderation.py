from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, FSInputFile
from aiogram.filters import ChatMemberUpdatedFilter

from database import get_pending_report, update_report_status, add_to_scam_base
from config import CHANNEL_ID
from keyboards import report_proof_kb

import os

router = Router()

SCAM_BANNER_PATH = "media/scam_banner.jpg"


@router.callback_query(F.data.startswith("approve_"))
async def approve_report(call: CallbackQuery, bot: Bot):
    """Одобрить жалобу — добавить в базу и опубликовать в канале"""
    report_id = int(call.data.split("_")[1])
    report = await get_pending_report(report_id)

    if not report:
        await call.answer("❌ Жалоба не найдена.", show_alert=True)
        return

    if report["status"] != "pending":
        await call.answer("⚠️ Жалоба уже обработана.", show_alert=True)
        return

    # Добавить в скам-базу
    scam_data = {
        "telegram_id": report.get("target_telegram_id"),
        "username": report.get("target_username"),
        "phone": report.get("target_phone"),
        "description": report.get("description"),
        "report_text": report.get("report_text"),
        "proof_file_ids": report.get("proof_file_ids"),
        "proof_types": report.get("proof_types"),
        "added_by_user_id": report.get("user_id"),
    }
    await add_to_scam_base(scam_data)
    await update_report_status(report_id, "approved")

    # Сформировать публикацию в канал
    lines = ["🚫 <b>ВНИМАНИЕ — МОШЕННИК</b>\n"]
    if report.get("target_telegram_id"):
        lines.append(f"🆔 ID: <code>{report['target_telegram_id']}</code>")
    if report.get("target_username"):
        lines.append(f"👤 @{report['target_username']}")
    if report.get("target_phone"):
        lines.append(f"📱 {report['target_phone']}")

    lines.append("\n🔴 <b>Репутация: мошенник.</b>")
    lines.append("Добавлен в скам-базу. Сделки недопустимы.\n")

    if report.get("description"):
        lines.append(f"📄 <b>Описание:</b>\n{report['description']}")

    if report.get("report_text"):
        lines.append(f"\n💬 <b>От пострадавшего:</b>\n<i>{report['report_text']}</i>")

    channel_text = "\n".join(lines)
    proof_ids = report.get("proof_file_ids") or []
    proof_types = report.get("proof_types") or []

    try:
        # Публикуем в канал
        if os.path.exists(SCAM_BANNER_PATH):
            await bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=FSInputFile(SCAM_BANNER_PATH),
                caption=channel_text,
                parse_mode="HTML"
            )
        else:
            await bot.send_message(CHANNEL_ID, channel_text, parse_mode="HTML")

        # Доказательства в канал
        if proof_ids:
            for i, fid in enumerate(proof_ids[:10]):
                ptype = proof_types[i] if i < len(proof_types) else "photo"
                if ptype == "video":
                    await bot.send_video(CHANNEL_ID, fid)
                else:
                    await bot.send_photo(CHANNEL_ID, fid)

    except Exception as e:
        print(f"Ошибка публикации в канал: {e}")

    # Уведомить подавшего жалобу
    try:
        await bot.send_message(
            report["user_id"],
            f"✅ <b>Ваша жалоба #{report_id} одобрена!</b>\n"
            "Информация опубликована в канале.",
            parse_mode="HTML"
        )
    except:
        pass

    # Обновить кнопки в группе модерации
    admin_name = call.from_user.username or call.from_user.full_name
    try:
        await call.message.edit_reply_markup(reply_markup=None)
        await call.message.reply(f"✅ <b>Одобрено</b> администратором @{admin_name}", parse_mode="HTML")
    except:
        pass

    await call.answer("✅ Жалоба одобрена и опубликована в канале!")


@router.callback_query(F.data.startswith("reject_"))
async def reject_report(call: CallbackQuery, bot: Bot):
    """Отклонить жалобу"""
    report_id = int(call.data.split("_")[1])
    report = await get_pending_report(report_id)

    if not report:
        await call.answer("❌ Жалоба не найдена.", show_alert=True)
        return

    if report["status"] != "pending":
        await call.answer("⚠️ Жалоба уже обработана.", show_alert=True)
        return

    await update_report_status(report_id, "rejected")

    # Уведомить подавшего
    try:
        await bot.send_message(
            report["user_id"],
            f"❌ <b>Ваша жалоба #{report_id} отклонена.</b>\n"
            "Недостаточно доказательств или нарушение правил.",
            parse_mode="HTML"
        )
    except:
        pass

    admin_name = call.from_user.username or call.from_user.full_name
    try:
        await call.message.edit_reply_markup(reply_markup=None)
        await call.message.reply(f"❌ <b>Отклонено</b> администратором @{admin_name}", parse_mode="HTML")
    except:
        pass

    await call.answer("❌ Жалоба отклонена.")
