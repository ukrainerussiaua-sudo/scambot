from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards import check_method_kb, cancel_kb, subscribe_kb, main_menu_kb
from database import check_scam_by_id, check_scam_by_username, check_scam_by_phone, log_search
from utils import is_subscribed, format_scammer_card, format_clean_card
from config import CHANNEL_LINK

router = Router()

# Изображения (положи эти файлы рядом с ботом или используй file_id после первой отправки)
SCAM_BANNER_PATH = "media/scam_banner.jpg"    # красная картинка МОШЕННИК
CLEAN_BANNER_PATH = "media/clean_banner.jpg"  # золотая картинка чистый


class CheckStates(StatesGroup):
    waiting_username = State()
    waiting_id = State()
    waiting_phone = State()


@router.message(F.text == "🔍 Проверить")
async def check_start(message: Message, bot: Bot):
    subscribed = await is_subscribed(bot, message.from_user.id)
    if not subscribed:
        await message.answer("Подпишитесь на канал для использования бота.", reply_markup=subscribe_kb(CHANNEL_LINK))
        return

    await message.answer(
        "🔍 <b>Проверка по скам-базе</b>\n\nВыберите способ поиска:",
        reply_markup=check_method_kb(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "check_username")
async def check_by_username(call: CallbackQuery, state: FSMContext):
    await state.set_state(CheckStates.waiting_username)
    await call.message.edit_text(
        "👤 Введите <b>@username</b> пользователя для проверки:",
        reply_markup=cancel_kb(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "check_id")
async def check_by_id(call: CallbackQuery, state: FSMContext):
    await state.set_state(CheckStates.waiting_id)
    await call.message.edit_text(
        "🆔 Введите <b>Telegram ID</b> пользователя для проверки:\n\n"
        "<i>Пример: 123456789</i>",
        reply_markup=cancel_kb(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "check_phone")
async def check_by_phone(call: CallbackQuery, state: FSMContext):
    await state.set_state(CheckStates.waiting_phone)
    await call.message.edit_text(
        "📱 Введите <b>номер телефона</b> для проверки:\n\n"
        "<i>Пример: +79991234567</i>",
        reply_markup=cancel_kb(),
        parse_mode="HTML"
    )


async def send_result(message: Message, found: list, query: str):
    """Отправить результат проверки"""
    if found:
        record = found[0]
        text = format_scammer_card(record)
        proof_ids = record.get("proof_file_ids") or []
        proof_types = record.get("proof_types") or []

        try:
            await message.answer_photo(
                photo=FSInputFile(SCAM_BANNER_PATH),
                caption=text,
                parse_mode="HTML"
            )
        except:
            await message.answer(text, parse_mode="HTML")

        # Отправить доказательства если есть
        if proof_ids:
            await message.answer(f"📎 <b>Доказательства ({len(proof_ids)} шт.):</b>", parse_mode="HTML")
            for i, fid in enumerate(proof_ids[:10]):
                try:
                    ptype = proof_types[i] if i < len(proof_types) else "photo"
                    if ptype == "video":
                        await message.answer_video(fid)
                    else:
                        await message.answer_photo(fid)
                except:
                    pass
    else:
        text = format_clean_card(query)
        try:
            await message.answer_photo(
                photo=FSInputFile(CLEAN_BANNER_PATH),
                caption=text,
                parse_mode="HTML"
            )
        except:
            await message.answer(text, parse_mode="HTML")

    await message.answer("Главное меню:", reply_markup=main_menu_kb())


@router.message(CheckStates.waiting_username)
async def process_username(message: Message, state: FSMContext):
    await state.clear()
    query = message.text.strip().lstrip("@")
    found = await check_scam_by_username(query)
    await log_search(message.from_user.id, f"@{query}", bool(found))
    await send_result(message, found, f"@{query}")


@router.message(CheckStates.waiting_id)
async def process_id(message: Message, state: FSMContext):
    text = message.text.strip()
    if not text.isdigit():
        await message.answer("❌ Введите корректный числовой ID.", reply_markup=cancel_kb())
        return

    await state.clear()
    tg_id = int(text)
    found = await check_scam_by_id(tg_id)
    await log_search(message.from_user.id, str(tg_id), bool(found))
    await send_result(message, found, str(tg_id))


@router.message(CheckStates.waiting_phone)
async def process_phone(message: Message, state: FSMContext):
    await state.clear()
    phone = message.text.strip()
    found = await check_scam_by_phone(phone)
    await log_search(message.from_user.id, phone, bool(found))
    await send_result(message, found, phone)
