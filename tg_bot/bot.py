import asyncio
import logging
import sys

import httpx
import redis
from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from settings import settings


redis_client = redis.Redis()
redis_client.from_url(settings.dsn)  # type:ignore


API_TOKEN = settings.API_TOKEN
logging.basicConfig(level=logging.INFO)

bot = Bot(
    token=API_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
form_router = Router()
dp = Dispatcher()


@form_router.message(CommandStart())
async def command_start(message: Message) -> None:
    kb = [
        [types.KeyboardButton(text="Показать список игр")],
        [types.KeyboardButton(text="Войти в личный кабинет")],
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer(
        "Рад приветствовать! Я - чатбот платформы GSDgames.",
        reply_markup=keyboard,
    )


@form_router.message(F.text == "Показать список игр")
async def get_list_games(message: Message) -> None:
    # response = httpx.get(f"{settings.BACKEND_URL}games/")
    # list_games = response.json()
    # data = json.loads(list_games)
    list_games = [
        {
            "title": "detail",
            "description": "Worker thing than mouth produce.",
            "rule_description": "Security all for student perhaps mission.",
            "price": 2840,
            "image": "media/test-image.jpg",
        },
        {
            "title": "rich",
            "description": "Develop series own draw add.",
            "rule_description": "Partner seek study.",
            "price": 6355,
            "image": "media/test-image.jpg",
        },
        {
            "title": "issue",
            "description": "Treat citizen difference worry.",
            "rule_description": "End race loss both.",
            "price": 9698,
            "image": "media/test-image.jpg",
        },
    ]
    titles = [game["title"] for game in list_games]
    games = []
    for title in titles:
        button = types.InlineKeyboardButton(
            text=str(title), callback_data=f"name_game:{title}"
        )
        games.append(button)

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[games])
    await message.answer("Выберите игру:", reply_markup=keyboard)
    # await message.answer(f"{list_games}")


async def info_game_on_name(name_game):
    list_games = [
        {
            "title": "detail",
            "description": "Worker thing than mouth produce.",
            "rule_description": "Security all for student perhaps mission.",
            "price": 2840,
            "image": "media/test-image.jpg",
        },
        {
            "title": "rich",
            "description": "Develop series own draw add.",
            "rule_description": "Partner seek study.",
            "price": 6355,
            "image": "media/test-image.jpg",
        },
        {
            "title": "issue",
            "description": "Treat citizen difference worry.",
            "rule_description": "End race loss both.",
            "price": 9698,
            "image": "media/test-image.jpg",
        },
    ]
    titles = [game["title"] for game in list_games]
    for title in titles:
        if title == name_game:
            index = titles.index(title)
            game = list_games[index]
            return game


@form_router.callback_query(lambda x: x.data == "name_game:detail")
async def callback_handler(callback: types.CallbackQuery):
    _, title = callback.data.split(":", 1)  # type:ignore[union-attr]
    game = await info_game_on_name(title)
    await callback.message.answer(  # type:ignore[union-attr]
        text=f"**{game['title']}**\n\n"
        f"Описание: {game['description']}\n"
        f"Цена: {game['price']}\n"
        f"Правила: {game['rule_description']}",
    )


@form_router.callback_query(lambda x: x.data == "name_game:rich")
async def callback_handler_2(callback: types.CallbackQuery):
    _, title = callback.data.split(":", 1)  # type:ignore[union-attr]
    game = await info_game_on_name(title)
    await callback.message.answer(  # type:ignore[union-attr]
        text=f"**{game['title']}**\n\n"
        f"Описание: {game['description']}\n"
        f"Цена: {game['price']}\n"
        f"Правила: {game['rule_description']}",
    )


@form_router.callback_query(lambda x: x.data == "name_game:issue")
async def callback_handler_3(callback: types.CallbackQuery):
    _, title = callback.data.split(":", 1)  # type:ignore[union-attr]
    game = await info_game_on_name(title)
    await callback.message.answer(  # type:ignore[union-attr]
        text=f"**{game['title']}**\n\n"
        f"Описание: {game['description']}\n"
        f"Цена: {game['price']}\n"
        f"Правила: {game['rule_description']}",
    )


@form_router.message(F.text == "Войти в личный кабинет")
async def register_user(message: Message) -> None:
    assert message.text is not None
    email, password = message.text.split(" ")
    response = httpx.post(
        f"{settings.BACKEND_URL}users/login",
        json={"email": email, "password": password},
    )
    token = response.json()["token"]

    user_tg_id = str(message.from_user.id)  # type:ignore
    redis_client.set(user_tg_id, token)
    await message.answer("Вы успешно вошли в личный кабинет!")


async def main():

    dp.include_router(form_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    asyncio.run(main())
