import json
import time
import pytz
from datetime import datetime
from aiogram import Bot, types
import aiogram.utils.exceptions
from aiogram.dispatcher import Dispatcher

config = json.loads(open('config.json').read())
bot = Bot(token=config["bot-token"])
dp = Dispatcher(bot)


async def send_logs(text):
    for user in config["log-uids"]:
        num = len(open('accounts.txt').read().split("\n"))
        try:
            await bot.send_message(chat_id=user,
                                   text=f"|--> <u><b>ФАРМ</b></u>.\n|\n|--> <b>Аккаунтов</b>: <u>{num}</u>.\n|\n|--> <b>Текст</b>: <code>{text}</code>", parse_mode="html")
        except aiogram.utils.exceptions.RetryAfter as e:
            time.sleep(e.timeout)
        except Exception as e:
            print(e)
            pass


@dp.message_handler(commands=["stats"])
async def stats(message: types.Message):
    if message.from_user.id in config["log-uids"]:
        with open("stats.json", "r") as stats_file:
            stats = json.load(stats_file)
            await message.reply(f"""<b>|-- СТАТИСТИКА --|</b>



<b>Закончено аккаунтов</b>
<u>{stats["done"]}</u>

<b>Среднее время на аккаунт</b>
<u>{stats["time"]}</u>

<b>Было отправлено монет</b>
<u>{stats["total"]}</u>

<b>Неудачных фармов</b>
<u>{stats["unsuccess"]}</u>

<b>Последний фарм</b>
{stats["last"]}

<b>Время сейчас</b>
{datetime.now(pytz.timezone("Europe/Moscow")).strftime("<u>%d/%m/%Y</u> <b>-|-</b> <u>%H:%M:%S</u>")}""", parse_mode="html")
