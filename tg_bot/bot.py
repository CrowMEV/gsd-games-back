import asyncio
import logging
import sys

import httpx
import redis
from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from settings import settings


redis_client = redis.Redis()
redis_client.from_url(settings.dsn)  # type:ignore


logging.basicConfig(level=logging.INFO)

form_router = Router()
dp = Dispatcher()


@form_router.message(CommandStart())
async def command_start(message: Message) -> None:
    await message.answer("Рад приветствовать! Я - чатбот платформы GSDgames.")
    await message.answer("Введите свою почту и пароль через пробел:")


@form_router.message(F.text)
async def get_user(message: Message) -> None:
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

    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp.include_router(form_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
