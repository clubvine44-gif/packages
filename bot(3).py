import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

TOKEN = "8678852008:AAGZeO7cKJWT1vNugKy8wkuII-wotKDZe70"
PROXY = "http://127.0.0.1:3128"
OPENROUTER_KEY = "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"
MODEL = "google/gemma-4-26b-a4b-it:free"
LYUDA_ID = 5679074450

session = AiohttpSession(proxy=PROXY)
bot = Bot(token=TOKEN, session=session)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

class Order(StatesGroup):
    name = State()
    service = State()
    budget = State()

def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="\U0001f310 \u0421\u0430\u0439\u0442\u044b", callback_data="info_sites"),
         InlineKeyboardButton(text="\U0001f916 \u0411\u043e\u0442\u044b \u0441 \u0418\u0418", callback_data="info_bots")],
        [InlineKeyboardButton(text="\U0001f4b0 \u0426\u0435\u043d\u044b", callback_data="prices"),
         InlineKeyboardButton(text="\U0001f4c2 \u041f\u0440\u0438\u043c\u0435\u0440\u044b \u0440\u0430\u0431\u043e\u0442", callback_data="portfolio")],
        [InlineKeyboardButton(text="\U0001f4ac \u0421\u043f\u0440\u043e\u0441\u0438\u0442\u044c \u0418\u0418-\u043a\u043e\u043d\u0441\u0443\u043b\u044c\u0442\u0430\u043d\u0442\u0430", callback_data="ask_ai")],
        [InlineKeyboardButton(text="\U0001f4cb \u041e\u0441\u0442\u0430\u0432\u0438\u0442\u044c \u0437\u0430\u044f\u0432\u043a\u0443", callback_data="order")],
        [InlineKeyboardButton(text="\U0001f469 \u041c\u0435\u043d\u0435\u0434\u0436\u0435\u0440 \u041b\u044e\u0434\u0430", url="https://t.me/LyudmilaVadimovna1")]
    ])

def back_btn():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="\u2b05 \u0413\u043b\u0430\u0432\u043d\u043e\u0435 \u043c\u0435\u043d\u044e", callback_data="back_main")]
    ])

def after_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="\U0001f4cb \u041e\u0441\u0442\u0430\u0432\u0438\u0442\u044c \u0437\u0430\u044f\u0432\u043a\u0443", callback_data="order")],
        [InlineKeyboardButton(text="\U0001f4ac \u0421\u043f\u0440\u043e\u0441\u0438\u0442\u044c \u0418\u0418-\u043a\u043e\u043d\u0441\u0443\u043b\u044c\u0442\u0430\u043d\u0442\u0430", callback_data="ask_ai")],
        [InlineKeyboardButton(text="\u2b05 \u0413\u043b\u0430\u0432\u043d\u043e\u0435 \u043c\u0435\u043d\u044e", callback_data="back_main")]
    ])

SYSTEM_PROMPT = (
    "\u0422\u044b \u0432\u0435\u0436\u043b\u0438\u0432\u044b\u0439 \u043a\u043e\u043d\u0441\u0443\u043b\u044c\u0442\u0430\u043d\u0442 \u043a\u043e\u043c\u043f\u0430\u043d\u0438\u0438 WebForge AI \u0438\u0437 \u041a\u0438\u0441\u043b\u043e\u0432\u043e\u0434\u0441\u043a\u0430. "
    "\u041e\u0442\u0432\u0435\u0447\u0430\u0439 \u043a\u0440\u0430\u0442\u043a\u043e, \u043f\u043e \u0434\u0435\u043b\u0443, \u0431\u0435\u0437 \u043b\u0438\u0448\u043d\u0435\u0439 \u0432\u043e\u0434\u044b. "
    "\u041a\u043e\u043c\u043f\u0430\u043d\u0438\u044f \u0434\u0435\u043b\u0430\u0435\u0442 \u0441\u0430\u0439\u0442\u044b \u0438 Telegram-\u0431\u043e\u0442\u043e\u0432 \u0434\u043b\u044f \u043c\u0430\u043b\u043e\u0433\u043e \u0431\u0438\u0437\u043d\u0435\u0441\u0430 \u043f\u043e\u0434 \u043a\u043b\u044e\u0447. "
    "\u0426\u0435\u043d\u044b: \u043b\u0435\u043d\u0434\u0438\u043d\u0433 \u043e\u0442 4500 \u0440\u0443\u0431 \u0437\u0430 3 \u0434\u043d\u044f, \u0441\u0430\u0439\u0442-\u0432\u0438\u0437\u0438\u0442\u043a\u0430 \u043e\u0442 5000 \u0440\u0443\u0431, "
    "\u0431\u043e\u0442 \u0441 \u0418\u0418 \u043e\u0442 10000 \u0440\u0443\u0431 \u0437\u0430 7-10 \u0434\u043d\u0435\u0439, \u0430\u0431\u043e\u043d\u0435\u043d\u0442\u043a\u0430 1500-2500 \u0440\u0443\u0431/\u043c\u0435\u0441. "
    "\u041c\u0435\u043d\u0435\u0434\u0436\u0435\u0440 @LyudmilaVadimovna1. "
    "\u0412\u0410\u0416\u041d\u041e: \u043d\u0438\u043a\u043e\u0433\u0434\u0430 \u043d\u0435 \u0438\u0441\u043f\u043e\u043b\u044c\u0437\u0443\u0439 \u0437\u0432\u0435\u0437\u0434\u043e\u0447\u043a\u0438, \u0440\u0435\u0448\u0435\u0442\u043a\u0438, \u043f\u043e\u0434\u0447\u0435\u0440\u043a\u0438\u0432\u0430\u043d\u0438\u044f \u0438 \u043e\u0431\u0440\u0430\u0442\u043d\u044b\u0435 \u043a\u0430\u0432\u044b\u0447\u043a\u0438. "
    "\u0422\u043e\u043b\u044c\u043a\u043e \u043e\u0431\u044b\u0447\u043d\u044b\u0439 \u0442\u0435\u043a\u0441\u0442. "
    "\u041d\u0435 \u0432\u044b\u0434\u0443\u043c\u044b\u0432\u0430\u0439 \u0446\u0435\u043d\u044b \u0438 \u0443\u0441\u043b\u0443\u0433\u0438 \u043a\u043e\u0442\u043e\u0440\u044b\u0445 \u043d\u0435\u0442. "
    "\u0415\u0441\u043b\u0438 \u043d\u0435 \u0437\u043d\u0430\u0435\u0448\u044c \u043e\u0442\u0432\u0435\u0442\u0430 - \u043d\u0430\u043f\u0440\u0430\u0432\u044c \u043a \u043c\u0435\u043d\u0435\u0434\u0436\u0435\u0440\u0443 @LyudmilaVadimovna1."
)

async def call_ai(question: str) -> str:
    try:
        async with aiohttp.ClientSession() as s:
            async with s.post(
                "https://openrouter.ai/api/v1/chat/completions",
                proxy=PROXY,
                headers={"Authorization": f"Bearer {OPENROUTER_KEY}", "Content-Type": "application/json"},
                json={
                    "model": MODEL,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": question}
                    ],
                    "max_tokens": 350
                },
                timeout=aiohttp.ClientTimeout(total=25)
            ) as r:
                data = await r.json()
                answer = data["choices"][0]["message"]["content"]
                for ch in ["*", "_", "`", "#"]:
                    answer = answer.replace(ch, "")
                return answer.strip()
    except Exception:
        return "\u041d\u0435 \u0443\u0434\u0430\u043b\u043e\u0441\u044c \u043f\u043e\u043b\u0443\u0447\u0438\u0442\u044c \u043e\u0442\u0432\u0435\u0442. \u041d\u0430\u043f\u0438\u0448\u0438\u0442\u0435 \u043c\u0435\u043d\u0435\u0434\u0436\u0435\u0440\u0443: @LyudmilaVadimovna1"

@dp.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "\u041f\u0440\u0438\u0432\u0435\u0442! \u042f \u0431\u043e\u0442 \u043a\u043e\u043c\u043f\u0430\u043d\u0438\u0438 WebForge AI.\n\n"
        "\u041c\u044b \u0438\u0437 \u041a\u0438\u0441\u043b\u043e\u0432\u043e\u0434\u0441\u043a\u0430 \u0438 \u0434\u0435\u043b\u0430\u0435\u043c \u0441\u0430\u0439\u0442\u044b \u0438 Telegram-\u0431\u043e\u0442\u043e\u0432 \u0434\u043b\u044f \u043c\u0430\u043b\u043e\u0433\u043e \u0431\u0438\u0437\u043d\u0435\u0441\u0430 \u043f\u043e\u0434 \u043a\u043b\u044e\u0447.\n\n"
        "\u0412\u044b\u0431\u0435\u0440\u0438\u0442\u0435 \u0440\u0430\u0437\u0434\u0435\u043b \u0438\u043b\u0438 \u0437\u0430\u0434\u0430\u0439\u0442\u0435 \u0432\u043e\u043f\u0440\u043e\u0441 \u043d\u0430\u0448\u0435\u043c\u0443 \u0418\u0418-\u043a\u043e\u043d\u0441\u0443\u043b\u044c\u0442\u0430\u043d\u0442\u0443:",
        reply_markup=main_menu()
    )

@dp.message(Command("help"))
async def help_cmd(message: types.Message):
    await message.answer(
        "\u041a\u043e\u043c\u0430\u043d\u0434\u044b:\n/start - \u0433\u043b\u0430\u0432\u043d\u043e\u0435 \u043c\u0435\u043d\u044e\n/price - \u0446\u0435\u043d\u044b\n/order - \u043e\u0441\u0442\u0430\u0432\u0438\u0442\u044c \u0437\u0430\u044f\u0432\u043a\u0443\n\n"
        "\u0418\u043b\u0438 \u043f\u0440\u043e\u0441\u0442\u043e \u043d\u0430\u043f\u0438\u0448\u0438\u0442\u0435 \u0432\u043e\u043f\u0440\u043e\u0441 - \u0418\u0418-\u043a\u043e\u043d\u0441\u0443\u043b\u044c\u0442\u0430\u043d\u0442 \u043e\u0442\u0432\u0435\u0442\u0438\u0442.",
        reply_markup=back_btn()
    )

@dp.message(Command("price"))
async def price_cmd(message: types.Message):
    await message.answer(
        "\u041d\u0430\u0448\u0438 \u0446\u0435\u043d\u044b:\n\n"
        "\u041b\u0435\u043d\u0434\u0438\u043d\u0433 - \u043e\u0442 4500 \u0440\u0443\u0431, \u0441\u0440\u043e\u043a 3 \u0434\u043d\u044f\n"
        "\u0421\u0430\u0439\u0442-\u0432\u0438\u0437\u0438\u0442\u043a\u0430 - \u043e\u0442 5000 \u0440\u0443\u0431\n"
        "\u0411\u043e\u0442 \u0441 \u0418\u0418 - \u043e\u0442 10000 \u0440\u0443\u0431, \u0441\u0440\u043e\u043a 7-10 \u0434\u043d\u0435\u0439\n\n"
        "\u0410\u0431\u043e\u043d\u0435\u043d\u0442\u043a\u0430: 1500-2500 \u0440\u0443\u0431/\u043c\u0435\u0441\n\n"
        "\u0415\u0441\u0442\u044c \u0432\u043e\u043f\u0440\u043e\u0441\u044b? \u041d\u0430\u043f\u0438\u0448\u0438\u0442\u0435 @LyudmilaVadimovna1",
        reply_markup=after_menu()
    )

@dp.message(Command("order"))
async def order_cmd(message: types.Message, state: FSMContext):
    await state.set_state(Order.name)
    await message.answer(
        "\u041e\u0441\u0442\u0430\u0432\u044c\u0442\u0435 \u0437\u0430\u044f\u0432\u043a\u0443. \u0428\u0430\u0433 1 \u0438\u0437 3:\n\n\u041a\u0430\u043a \u0432\u0430\u0441 \u0437\u043e\u0432\u0443\u0442?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="\u041e\u0442\u043c\u0435\u043d\u0430", callback_data="back_main")]])
    )

@dp.callback_query(F.data == "back_main")
async def back_main(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.answer(
        "\u0413\u043b\u0430\u0432\u043d\u043e\u0435 \u043c\u0435\u043d\u044e:",
        reply_markup=main_menu()
    )
    await call.answer()

@dp.callback_query(F.data == "info_sites")
async def info_sites(call: types.CallbackQuery):
    await call.message.answer(
        "\u0421\u0430\u0439\u0442\u044b \u043f\u043e\u0434 \u043a\u043b\u044e\u0447:\n\n"
        "\u041b\u0435\u043d\u0434\u0438\u043d\u0433 - \u043e\u0434\u043d\u043e\u0441\u0442\u0440\u0430\u043d\u0438\u0447\u043d\u044b\u0439 \u043f\u0440\u043e\u0434\u0430\u044e\u0449\u0438\u0439 \u0441\u0430\u0439\u0442, \u043e\u0442 4500 \u0440\u0443\u0431, \u0441\u0440\u043e\u043a 3 \u0434\u043d\u044f\n"
        "\u0421\u0430\u0439\u0442-\u0432\u0438\u0437\u0438\u0442\u043a\u0430 - \u043c\u043d\u043e\u0433\u043e\u0441\u0442\u0440\u0430\u043d\u0438\u0447\u043d\u044b\u0439 \u0441\u0430\u0439\u0442 \u043e \u0432\u0430\u0441 \u0438 \u0432\u0430\u0448\u0438\u0445 \u0443\u0441\u043b\u0443\u0433\u0430\u0445, \u043e\u0442 5000 \u0440\u0443\u0431\n\n"
        "\u0412\u0441\u0435 \u0441\u0430\u0439\u0442\u044b \u0430\u0434\u0430\u043f\u0442\u0438\u0440\u043e\u0432\u0430\u043d\u044b \u043f\u043e\u0434 \u043c\u043e\u0431\u0438\u043b\u044c\u043d\u044b\u0435 \u0443\u0441\u0442\u0440\u043e\u0439\u0441\u0442\u0432\u0430.\n"
        "\u0414\u0435\u043b\u0430\u0435\u043c \u0434\u043b\u044f \u0441\u0430\u043b\u043e\u043d\u043e\u0432 \u043a\u0440\u0430\u0441\u043e\u0442\u044b, \u043a\u0430\u0444\u0435, \u0433\u043e\u0441\u0442\u0435\u0432\u044b\u0445 \u0434\u043e\u043c\u043e\u0432, \u0447\u0430\u0441\u0442\u043d\u044b\u0445 \u043c\u0430\u0441\u0442\u0435\u0440\u043e\u0432.",
        reply_markup=after_menu()
    )
    await call.answer()

@dp.callback_query(F.data == "info_bots")
async def info_bots(call: types.CallbackQuery):
    await call.message.answer(
        "Telegram-\u0431\u043e\u0442\u044b \u0441 \u0418\u0418:\n\n"
        "\u0411\u043e\u0442 \u0440\u0430\u0431\u043e\u0442\u0430\u0435\u0442 \u0437\u0430 \u0432\u0430\u0441 24/7 - \u043e\u0442\u0432\u0435\u0447\u0430\u0435\u0442 \u043d\u0430 \u0432\u043e\u043f\u0440\u043e\u0441\u044b, \u043f\u0440\u0438\u043d\u0438\u043c\u0430\u0435\u0442 \u0437\u0430\u044f\u0432\u043a\u0438, \u043a\u043e\u043d\u0441\u0443\u043b\u044c\u0442\u0438\u0440\u0443\u0435\u0442 \u043a\u043b\u0438\u0435\u043d\u0442\u043e\u0432.\n\n"
        "\u0421\u0442\u043e\u0438\u043c\u043e\u0441\u0442\u044c \u043e\u0442 10000 \u0440\u0443\u0431, \u0441\u0440\u043e\u043a 7-10 \u0434\u043d\u0435\u0439.\n\n"
        "\u041f\u043e\u0434\u0445\u043e\u0434\u0438\u0442 \u0434\u043b\u044f: \u0441\u0430\u043b\u043e\u043d\u043e\u0432 \u043a\u0440\u0430\u0441\u043e\u0442\u044b, \u043a\u0430\u0444\u0435, \u0433\u043e\u0441\u0442\u0435\u0432\u044b\u0445 \u0434\u043e\u043c\u043e\u0432, \u0447\u0430\u0441\u0442\u043d\u044b\u0445 \u043c\u0430\u0441\u0442\u0435\u0440\u043e\u0432 \u0438 \u043b\u044e\u0431\u043e\u0433\u043e \u043c\u0430\u043b\u043e\u0433\u043e \u0431\u0438\u0437\u043d\u0435\u0441\u0430.",
        reply_markup=after_menu()
    )
    await call.answer()

@dp.callback_query(F.data == "prices")
async def prices(call: types.CallbackQuery):
    await call.message.answer(
        "\u041d\u0430\u0448\u0438 \u0446\u0435\u043d\u044b:\n\n"
        "\u041b\u0435\u043d\u0434\u0438\u043d\u0433 - \u043e\u0442 4500 \u0440\u0443\u0431, \u0441\u0440\u043e\u043a 3 \u0434\u043d\u044f\n"
        "\u0421\u0430\u0439\u0442-\u0432\u0438\u0437\u0438\u0442\u043a\u0430 - \u043e\u0442 5000 \u0440\u0443\u0431\n"
        "\u0411\u043e\u0442 \u0441 \u0418\u0418 - \u043e\u0442 10000 \u0440\u0443\u0431, \u0441\u0440\u043e\u043a 7-10 \u0434\u043d\u0435\u0439\n\n"
        "\u0410\u0431\u043e\u043d\u0435\u043d\u0442\u0441\u043a\u043e\u0435 \u043e\u0431\u0441\u043b\u0443\u0436\u0438\u0432\u0430\u043d\u0438\u0435: 1500-2500 \u0440\u0443\u0431/\u043c\u0435\u0441\n\n"
        "\u0415\u0441\u0442\u044c \u0432\u043e\u043f\u0440\u043e\u0441\u044b? \u041d\u0430\u043f\u0438\u0448\u0438\u0442\u0435 \u043c\u0435\u043d\u0435\u0434\u0436\u0435\u0440\u0443 @LyudmilaVadimovna1",
        reply_markup=after_menu()
    )
    await call.answer()

@dp.callback_query(F.data == "portfolio")
async def portfolio(call: types.CallbackQuery):
    await call.message.answer(
        "\u041f\u0440\u0438\u043c\u0435\u0440\u044b \u043d\u0430\u0448\u0438\u0445 \u0440\u0430\u0431\u043e\u0442:\n\n"
        "\u0414\u0435\u043c\u043e-\u0441\u0430\u0439\u0442 \u0434\u043b\u044f \u0441\u0430\u043b\u043e\u043d\u0430 \u043a\u0440\u0430\u0441\u043e\u0442\u044b 1:\nhttps://clubvine44-gif.github.io/demo-salon-1\n\n"
        "\u0414\u0435\u043c\u043e-\u0441\u0430\u0439\u0442 \u0434\u043b\u044f \u0441\u0430\u043b\u043e\u043d\u0430 \u043a\u0440\u0430\u0441\u043e\u0442\u044b 2:\nhttps://clubvine44-gif.github.io/salon-demo2/\n\n"
        "\u0425\u043e\u0442\u0438\u0442\u0435 \u0442\u0430\u043a\u043e\u0439 \u0436\u0435 \u0441\u0430\u0439\u0442 \u0438\u043b\u0438 \u0431\u043e\u0442 \u0434\u043b\u044f \u0441\u0432\u043e\u0435\u0433\u043e \u0431\u0438\u0437\u043d\u0435\u0441\u0430?",
        reply_markup=after_menu()
    )
    await call.answer()

@dp.callback_query(F.data == "ask_ai")
async def ask_ai_prompt(call: types.CallbackQuery):
    await call.message.answer(
        "\u0417\u0430\u0434\u0430\u0439\u0442\u0435 \u043b\u044e\u0431\u043e\u0439 \u0432\u043e\u043f\u0440\u043e\u0441 \u043e \u043d\u0430\u0448\u0438\u0445 \u0443\u0441\u043b\u0443\u0433\u0430\u0445 - \u0418\u0418-\u043a\u043e\u043d\u0441\u0443\u043b\u044c\u0442\u0430\u043d\u0442 \u043e\u0442\u0432\u0435\u0442\u0438\u0442 \u043f\u0440\u044f\u043c\u043e \u0441\u0435\u0439\u0447\u0430\u0441:",
        reply_markup=back_btn()
    )
    await call.answer()

@dp.callback_query(F.data == "order")
async def order_start(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(Order.name)
    await call.message.answer(
        "\u041e\u0441\u0442\u0430\u0432\u044c\u0442\u0435 \u0437\u0430\u044f\u0432\u043a\u0443. \u0428\u0430\u0433 1 \u0438\u0437 3:\n\n\u041a\u0430\u043a \u0432\u0430\u0441 \u0437\u043e\u0432\u0443\u0442?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="\u041e\u0442\u043c\u0435\u043d\u0430", callback_data="back_main")]])
    )
    await call.answer()

@dp.message(Order.name)
async def order_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Order.service)
    await message.answer(
        f"\u041e\u0442\u043b\u0438\u0447\u043d\u043e, {message.text}! \u0428\u0430\u0433 2 \u0438\u0437 3:\n\n\u0427\u0442\u043e \u0432\u0430\u0441 \u0438\u043d\u0442\u0435\u0440\u0435\u0441\u0443\u0435\u0442?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="\u0421\u0430\u0439\u0442", callback_data="svc_site")],
            [InlineKeyboardButton(text="\u0411\u043e\u0442 \u0441 \u0418\u0418", callback_data="svc_bot")],
            [InlineKeyboardButton(text="\u0421\u0430\u0439\u0442 + \u0431\u043e\u0442", callback_data="svc_both")]
        ])
    )

@dp.callback_query(F.data.startswith("svc_"), Order.service)
async def order_service(call: types.CallbackQuery, state: FSMContext):
    svc_map = {"svc_site": "\u0421\u0430\u0439\u0442", "svc_bot": "\u0411\u043e\u0442 \u0441 \u0418\u0418", "svc_both": "\u0421\u0430\u0439\u0442 + \u0431\u043e\u0442"}
    await state.update_data(service=svc_map.get(call.data, call.data))
    await state.set_state(Order.budget)
    await call.message.answer(
        "\u0428\u0430\u0433 3 \u0438\u0437 3:\n\n\u041a\u0430\u043a\u043e\u0439 \u043f\u0440\u0438\u043c\u0435\u0440\u043d\u044b\u0439 \u0431\u044e\u0434\u0436\u0435\u0442?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="\u0434\u043e 5000 \u0440\u0443\u0431", callback_data="bgt_5k")],
            [InlineKeyboardButton(text="5000-15000 \u0440\u0443\u0431", callback_data="bgt_15k")],
            [InlineKeyboardButton(text="\u0431\u043e\u043b\u0435\u0435 15000 \u0440\u0443\u0431", callback_data="bgt_top")]
        ])
    )
    await call.answer()

@dp.callback_query(F.data.startswith("bgt_"), Order.budget)
async def order_budget(call: types.CallbackQuery, state: FSMContext):
    bgt_map = {"bgt_5k": "\u0434\u043e 5000 \u0440\u0443\u0431", "bgt_15k": "5000-15000 \u0440\u0443\u0431", "bgt_top": "\u0431\u043e\u043b\u0435\u0435 15000 \u0440\u0443\u0431"}
    data = await state.get_data()
    budget = bgt_map.get(call.data, call.data)
    await state.clear()
    summary = (
        "\u041d\u043e\u0432\u0430\u044f \u0437\u0430\u044f\u0432\u043a\u0430!\n\n"
        "\u0418\u043c\u044f: " + str(data.get("name")) + "\n"
        "\u0423\u0441\u043b\u0443\u0433\u0430: " + str(data.get("service")) + "\n"
        "\u0411\u044e\u0434\u0436\u0435\u0442: " + budget
    )
    try:
        await bot.send_message(LYUDA_ID, summary)
    except Exception:
        pass
    await call.message.answer(
        "\u0417\u0430\u044f\u0432\u043a\u0430 \u043f\u0440\u0438\u043d\u044f\u0442\u0430! \u041c\u0435\u043d\u0435\u0434\u0436\u0435\u0440 \u041b\u044e\u0434\u0430 \u0441\u0432\u044f\u0436\u0435\u0442\u0441\u044f \u0441 \u0432\u0430\u043c\u0438 \u0432 \u0431\u043b\u0438\u0436\u0430\u0439\u0448\u0435\u0435 \u0432\u0440\u0435\u043c\u044f.\n\n"
        "\u0418\u043b\u0438 \u043d\u0430\u043f\u0438\u0448\u0438\u0442\u0435 \u0441\u0440\u0430\u0437\u0443: @LyudmilaVadimovna1",
        reply_markup=main_menu()
    )
    await call.answer()

@dp.message()
async def free_text(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is not None:
        return
    await message.answer("\u0418\u0449\u0443 \u043e\u0442\u0432\u0435\u0442, \u043f\u043e\u0434\u043e\u0436\u0434\u0438\u0442\u0435 \u0441\u0435\u043a\u0443\u043d\u0434\u0443...")
    answer = await call_ai(message.text)
    await message.answer(
        answer,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="\u041e\u0441\u0442\u0430\u0432\u0438\u0442\u044c \u0437\u0430\u044f\u0432\u043a\u0443", callback_data="order")],
            [InlineKeyboardButton(text="\u0413\u043b\u0430\u0432\u043d\u043e\u0435 \u043c\u0435\u043d\u044e", callback_data="back_main")]
        ])
    )

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
