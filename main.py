import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram import Router, F

from config import BOT_TOKEN, CHANNEL_LINK, FAQ_TEXT
from keyboards import main_menu_kb, subscribe_kb
from utils import is_subscribed
import report
import check
import moderation

logging.basicConfig(level=logging.INFO)

main_router = Router()


@main_router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot):
    subscribed = await is_subscribed(bot, message.from_user.id)
    if not subscribed:
        await message.answer(
            "👋 Добро пожаловать!\n\nДля использования бота подпишитесь на наш канал.",
            reply_markup=subscribe_kb(CHANNEL_LINK)
        )
        return

    await message.answer(
        "👋 <b>Добро пожаловать в скам-базу!</b>\n\n"
        "Здесь вы можете:\n"
        "🔍 Проверить пользователя по базе мошенников\n"
        "📝 Подать жалобу на мошенника\n\n"
        "Выберите действие:",
        reply_markup=main_menu_kb(),
        parse_mode="HTML"
    )


@main_router.callback_query(F.data == "check_subscription")
async def check_sub(call: CallbackQuery, bot: Bot):
    subscribed = await is_subscribed(bot, call.from_user.id)
    if subscribed:
        await call.message.edit_text(
            "✅ Подписка подтверждена!\n\nДобро пожаловать!",
        )
        await call.message.answer(
            "👋 <b>Добро пожаловать в скам-базу!</b>\n\nВыберите действие:",
            reply_markup=main_menu_kb(),
            parse_mode="HTML"
        )
    else:
        await call.answer("❌ Вы ещё не подписались на канал!", show_alert=True)


@main_router.callback_query(F.data == "cancel")
async def cancel_action(call: CallbackQuery, state=None):
    if state:
        await state.clear()
    await call.message.edit_text("❌ Действие отменено.")
    await call.message.answer("Главное меню:", reply_markup=main_menu_kb())


@main_router.callback_query(F.data == "back_main")
async def back_main(call: CallbackQuery):
    await call.message.edit_text(
        "Выберите действие:",
        reply_markup=None
    )
    await call.message.answer("Главное меню:", reply_markup=main_menu_kb())


@main_router.message(F.text == "❓ FAQ")
async def faq(message: Message):
    await message.answer(FAQ_TEXT, parse_mode="HTML")


@main_router.message(F.text == "📢 Канал")
async def channel_link(message: Message):
    await message.answer(
        f"📢 Наш канал: {CHANNEL_LINK}",
        reply_markup=subscribe_kb(CHANNEL_LINK)
    )


async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(main_router)
    dp.include_router(report.router)
    dp.include_router(check.router)
    dp.include_router(moderation.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
