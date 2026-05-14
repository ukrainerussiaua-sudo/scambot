from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards import cancel_kb, skip_field_kb, finish_proof_kb, subscribe_kb, main_menu_kb
from database import create_pending_report, update_report_moderation_msg
from utils import is_subscribed, format_report_for_moderation
from keyboards import report_proof_kb
from config import CHANNEL_LINK, MODERATION_GROUP_ID

router = Router()


class ReportStates(StatesGroup):
    target_info = State()       # ID или @username нарушителя
    target_phone = State()      # телефон (опционально)
    description = State()       # описание мошенничества
    report_text = State()       # слова пострадавшего
    proof_media = State()       # фото/видео доказательства


@router.message(F.text == "📝 Подать жалобу")
async def report_start(message: Message, bot: Bot, state: FSMContext):
    subscribed = await is_subscribed(bot, message.from_user.id)
    if not subscribed:
        await message.answer("Подпишитесь на канал для использования бота.", reply_markup=subscribe_kb(CHANNEL_LINK))
        return

    await state.set_state(ReportStates.target_info)
    await message.answer(
        "📝 <b>Подача жалобы</b>\n\n"
        "Шаг 1/5 — Введите данные нарушителя:\n"
        "• @username или Telegram ID\n\n"
        "<i>Пример: @username или 123456789</i>",
        reply_markup=cancel_kb(),
        parse_mode="HTML"
    )


@router.message(ReportStates.target_info)
async def process_target_info(message: Message, state: FSMContext):
    text = message.text.strip()
    data = {}

    if text.startswith("@"):
        data["target_username"] = text.lstrip("@")
    elif text.isdigit():
        data["target_telegram_id"] = int(text)
    else:
        # Может быть и то и другое через пробел
        parts = text.split()
        for p in parts:
            if p.startswith("@"):
                data["target_username"] = p.lstrip("@")
            elif p.isdigit():
                data["target_telegram_id"] = int(p)

    if not data:
        await message.answer("❌ Введите корректный @username или числовой ID.", reply_markup=cancel_kb())
        return

    await state.update_data(**data)
    await state.set_state(ReportStates.target_phone)
    await message.answer(
        "Шаг 2/5 — Введите номер телефона нарушителя (если знаете):\n"
        "<i>Пример: +79991234567</i>",
        reply_markup=skip_field_kb(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "skip_field", ReportStates.target_phone)
async def skip_phone(call: CallbackQuery, state: FSMContext):
    await state.set_state(ReportStates.description)
    await call.message.edit_text(
        "Шаг 3/5 — Опишите суть мошенничества:\n"
        "<i>Что произошло? Как вас обманули?</i>",
        reply_markup=cancel_kb(),
        parse_mode="HTML"
    )


@router.message(ReportStates.target_phone)
async def process_phone(message: Message, state: FSMContext):
    await state.update_data(target_phone=message.text.strip())
    await state.set_state(ReportStates.description)
    await message.answer(
        "Шаг 3/5 — Опишите суть мошенничества:\n"
        "<i>Что произошло? Как вас обманули?</i>",
        reply_markup=cancel_kb(),
        parse_mode="HTML"
    )


@router.message(ReportStates.description)
async def process_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text.strip())
    await state.set_state(ReportStates.report_text)
    await message.answer(
        "Шаг 4/5 — Напишите текст от вашего лица (будет опубликован в канале):\n"
        "<i>Расскажите своими словами что случилось</i>",
        reply_markup=skip_field_kb(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "skip_field", ReportStates.report_text)
async def skip_report_text(call: CallbackQuery, state: FSMContext):
    await state.update_data(proof_file_ids=[], proof_types=[])
    await state.set_state(ReportStates.proof_media)
    await call.message.edit_text(
        "Шаг 5/5 — Прикрепите доказательства (фото/видео переписки):\n\n"
        "📎 Отправляйте по одному файлу. Когда закончите — нажмите <b>Готово</b>.",
        reply_markup=finish_proof_kb(),
        parse_mode="HTML"
    )


@router.message(ReportStates.report_text)
async def process_report_text(message: Message, state: FSMContext):
    await state.update_data(report_text=message.text.strip(), proof_file_ids=[], proof_types=[])
    await state.set_state(ReportStates.proof_media)
    await message.answer(
        "Шаг 5/5 — Прикрепите доказательства (фото/видео переписки):\n\n"
        "📎 Отправляйте по одному файлу. Когда закончите — нажмите <b>Готово</b>.",
        reply_markup=finish_proof_kb(),
        parse_mode="HTML"
    )


@router.message(ReportStates.proof_media, F.photo)
async def collect_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    ids = data.get("proof_file_ids", [])
    types = data.get("proof_types", [])
    ids.append(message.photo[-1].file_id)
    types.append("photo")
    await state.update_data(proof_file_ids=ids, proof_types=types)
    await message.answer(
        f"✅ Фото принято ({len(ids)} шт.). Добавьте ещё или нажмите <b>Готово</b>.",
        reply_markup=finish_proof_kb(),
        parse_mode="HTML"
    )


@router.message(ReportStates.proof_media, F.video)
async def collect_video(message: Message, state: FSMContext):
    data = await state.get_data()
    ids = data.get("proof_file_ids", [])
    types = data.get("proof_types", [])
    ids.append(message.video.file_id)
    types.append("video")
    await state.update_data(proof_file_ids=ids, proof_types=types)
    await message.answer(
        f"✅ Видео принято ({len(ids)} шт.). Добавьте ещё или нажмите <b>Готово</b>.",
        reply_markup=finish_proof_kb(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "finish_proof")
async def finish_report(call: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    await state.clear()

    if not data.get("description"):
        await call.answer("❌ Описание обязательно!", show_alert=True)
        return

    # Сохранить в БД
    report_data = {
        "user_id": call.from_user.id,
        "username": call.from_user.username,
        "target_telegram_id": data.get("target_telegram_id"),
        "target_username": data.get("target_username"),
        "target_phone": data.get("target_phone"),
        "description": data.get("description"),
        "report_text": data.get("report_text"),
        "proof_file_ids": data.get("proof_file_ids", []),
        "proof_types": data.get("proof_types", []),
    }

    report = await create_pending_report(report_data)

    if not report:
        await call.message.answer("❌ Ошибка при сохранении жалобы. Попробуйте позже.")
        return

    # Отправить в группу модерации
    mod_text = format_report_for_moderation(report)

    proof_ids = report.get("proof_file_ids") or []
    proof_types = report.get("proof_types") or []

    try:
        # Если есть фото — отправить как медиагруппу или первое фото с текстом
        if proof_ids and proof_types[0] == "photo":
            mod_msg = await bot.send_photo(
                chat_id=MODERATION_GROUP_ID,
                photo=proof_ids[0],
                caption=mod_text,
                parse_mode="HTML",
                reply_markup=report_proof_kb(report["id"])
            )
        elif proof_ids and proof_types[0] == "video":
            mod_msg = await bot.send_video(
                chat_id=MODERATION_GROUP_ID,
                video=proof_ids[0],
                caption=mod_text,
                parse_mode="HTML",
                reply_markup=report_proof_kb(report["id"])
            )
        else:
            mod_msg = await bot.send_message(
                chat_id=MODERATION_GROUP_ID,
                text=mod_text,
                parse_mode="HTML",
                reply_markup=report_proof_kb(report["id"])
            )

        # Отправить остальные доказательства
        if len(proof_ids) > 1:
            for i, fid in enumerate(proof_ids[1:], 1):
                ptype = proof_types[i] if i < len(proof_types) else "photo"
                if ptype == "video":
                    await bot.send_video(MODERATION_GROUP_ID, fid)
                else:
                    await bot.send_photo(MODERATION_GROUP_ID, fid)

        await update_report_moderation_msg(report["id"], mod_msg.message_id)

    except Exception as e:
        print(f"Ошибка отправки в модерацию: {e}")

    await call.message.edit_text(
        "✅ <b>Жалоба отправлена на модерацию!</b>\n\n"
        f"🆔 Номер жалобы: <code>{report['id']}</code>\n"
        "Модераторы рассмотрят обращение в течение 24 часов.",
        parse_mode="HTML"
    )
    await call.message.answer("Главное меню:", reply_markup=main_menu_kb())
