import os
import asyncio

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

#env
load_dotenv()
TG_TOKEN = os.getenv("BOT_TOKEN")
ADMIN = int(os.getenv("ADMIN_ID"))

#основа бота
bot = Bot(token=TG_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

class UserRegistration(StatesGroup):
    waiting_for_name = State()
    waiting_for_contact = State()
    waiting_for_task = State()

#старт меню
@router.message(Command("start"))
async def cmd_start(message: Message):
    builder = InlineKeyboardBuilder()
    builder.button(text="Прайс-лист", callback_data="price")
    builder.button(text="Частые вопросы (FAQ)", callback_data="faq")
    builder.button(text="Оставить заявку", callback_data="request")
    builder.adjust(1)
    await message.answer("Здравствуйте, вас приветствует бот студии веб-дизайна!", reply_markup=builder.as_markup())

#прайс
@router.callback_query(F.data == "price")
async def price(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("!!!Сюда вписать Прайс-лист!!!")

#вопросы
@router.callback_query(F.data == "faq")
async def faq(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("!!!Сюда вписать Частые вопросы!!!")

#заявка имя
@router.callback_query(F.data == "request")
async def request_name(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("Как вас зовут?")
    await state.set_state(UserRegistration.waiting_for_name)

#заявка контакты
@router.message(UserRegistration.waiting_for_name)
async def request_contact(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Как с вами можно связаться? (номер телефона или @username)")
    await state.set_state(UserRegistration.waiting_for_contact)

#заявка задача
@router.message(UserRegistration.waiting_for_contact)
async def request_task(message: Message, state: FSMContext):
    await state.update_data(contact=message.text)
    await message.answer("Опишите вашу задачу.")
    await state.set_state(UserRegistration.waiting_for_task)

#сообщение админу
@router.message(UserRegistration.waiting_for_task)
async def message_to_admin(message: Message, state: FSMContext):
    await state.update_data(task=message.text)

    user_data = await state.get_data()
    name = user_data.get("name")
    contact = user_data.get("contact")
    task = user_data.get("task")
    username = f"@{message.from_user.username}" if message.from_user.username else "Юзернейм отсутствует."

    user_info = (
        f"**Новая заявка на дизайн!**\n\n"
        f"Имя: {name}\n"
        f"Telegram: {username}\n"
        f"Контакты для связи: {contact}\n"
        f"Задача: {task}"
    )

    await bot.send_message(chat_id=ADMIN, text=user_info, parse_mode="Markdown")
    await message.answer("Спасибо, ваша заявка принята! Менеджер свяжется с вами в течение часа.")
    await state.clear()

async def main():
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())

