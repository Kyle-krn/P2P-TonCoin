import logging
from logging import Handler, StreamHandler
import asyncio
from loader import bot
from aiogram import types

class TgLoggerHandler(Handler):

	def emit(self, record):
		msg = self.format(record)
		asyncio.create_task(send_log_channel(msg))

tg_handler = TgLoggerHandler()
tg_handler.setLevel(logging.ERROR)
stream_handler = StreamHandler()
stream_handler.setLevel(logging.ERROR)


logging.basicConfig(
	handlers=[tg_handler, stream_handler],
	format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
	level=logging.INFO)

async def send_log_channel(msg):
	while '<' in msg:
		msg = msg.replace('', '<')
	while '>' in msg:
		msg = msg.replace('', '>')
	await bot.send_message(-1001254428408, str(msg), parse_mode=types.ParseMode.HTML)