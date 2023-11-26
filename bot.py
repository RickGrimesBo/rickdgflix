import re
import sys
import asyncio
import logging
import humanize
from os import getenv
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F as MagicFilter
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.markdown import hbold

from utils import GdFlix
from exceptions import GdFlixError

load_dotenv()
BOT_TOKEN = "BOT_TOKEN"
GDFLIX_API_KEY= "API_KEY"
API_BASE_URI = "BASE_URI"
AUTH_USERS = ["AUTH_USERS"]

dp = Dispatcher()
gdflix = GdFlix(api_key=GDFLIX_API_KEY, base_uri=API_BASE_URI)

@dp.message(CommandStart()
async def start(message: Message) -> None:
    await message.answer(f"Hello, {hbold(message.from_user.full_name)}, welcome to google drive to gdflix url converter")

@dp.message(MagicFilter.text.regexp("http[s]*:\/\/.+") & MagicFilter.from_user.id.in_(AUTH_USERS))
async def gdrive(message: Message) -> None:
    if "folders" in message.text:
        return await message.reply("This seems like a folder url, which is not supported")
    if matched_url := re.search(r"https:\/\/drive\.google\.com\/(?:file(.*?)?\/d\/)([-\w]+)", message.text):
        file_id = matched_url.group(2)
        msg = await message.answer(f"Sending {file_id} to gdflix...")
        try:
            res = await gdflix.share_file(file_id)
            file_url = f"https://gdflix.live/file/{res.get('key')}"
            msg_text = ""
            if name := res.get("name"):
                msg_text += f"<b>File Name:</b> <i>{name}</i>\n"
            if size := res.get("size"):
                msg_text += f"<b>File Size:</b> <code>{humanize.naturalsize(size)}</code>\n"
            if created_date := res.get("create_at"):
                msg_text += f"<b>Created At:</b> <code>{created_date}</code>\n"
            if file_hash := res.get("md5"):
                msg_text += f"<b>Md5 Hash:</b> <code>{file_hash}</code>\n"
            if mime := res.get("mime"):
                msg_text += f"<b>Mime Type:</b> <i>{mime}</i>\n"
            await msg.edit_text(
                msg_text,
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[[InlineKeyboardButton(text="Gdflix Link 🔗", url=file_url)]]
                ),
            )
        except GdFlixError as err:
            await msg.edit_text(f"GDFLIX ERROR: {err}")
        except Exception:
            await msg.edit_text("UNKNOWN ERROR OCCURED")
    else: await message.answer("This url is not a valid gdrive url")

@dp.message()
async def evts(message: Message):
    await message.answer("idk who you are and what you need")

async def main() -> None:
    bot = Bot(BOT_TOKEN, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
