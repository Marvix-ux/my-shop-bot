import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from fastapi import Request
from fastapi.responses import JSONResponse

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

users = {}

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    if user_id not in users:
        users[user_id] = {"balance": 0}

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="💳 Пополнить баланс", callback_data="topup")],
        [types.InlineKeyboardButton(text="🎁 Промокоды", callback_data="promo")],
        [types.InlineKeyboardButton(text="👤 Профиль", callback_data="profile")],
        [types.InlineKeyboardButton(text="🛒 Все товары", callback_data="shop")],
    ])

    await message.answer(
        f"👋 Добро пожаловать!\n💰 Баланс: {users[user_id]['balance']} ₽",
        reply_markup=keyboard
    )

@dp.callback_query(lambda c: c.data == "profile")
async def profile_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    balance = users.get(user_id, {}).get("balance", 0)
    await callback.message.answer(f"👤 ID: {user_id}\n💰 Баланс: {balance} ₽")
    await callback.answer()

@dp.callback_query(lambda c: c.data == "promo")
async def promo_handler(callback: types.CallbackQuery):
    await callback.message.answer("📩 Отправьте промокод:")
    await callback.answer()

@dp.message()
async def text_handler(message: types.Message):
    user_id = message.from_user.id
    text = message.text.strip().upper()
    promos = {"APPLEDLC": 10, "FIXBOT2026": 20, "DILDO": 1, "КРУТОЙ": 5}

    if text in promos:
        if user_id not in users:
            users[user_id] = {"balance": 0}
        users[user_id]["balance"] += promos[text]
        await message.answer(f"🎉 Промокод активирован!\n💰 Баланс: {users[user_id]['balance']} ₽")
    else:
        await message.answer("❌ Промокод не найден.")

async def handler(request: Request):
    try:
        body = await request.json()
        update = types.Update(**body)
        await dp.feed_update(bot, update)
        return JSONResponse({"ok": True})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)})

app = handler
