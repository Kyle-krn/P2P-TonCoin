import requests
from data import config
import logging
import urllib.parse

def send_log_channel(msg):
	"""Отправляет лог с ошибкой в канал"""
	while len(msg) > 4000:
			msg = msg.split('\n')
			msg = "\n".join(msg[1:])
	while '<' in msg:
		msg = msg.replace('', '<')
	while '>' in msg:
		msg = msg.replace('', '>')
	return requests.get(f'https://api.telegram.org/bot{config.BOT_TOKEN}/sendMessage?chat_id={config.LOGGER_CHANEL_ID}&text={urllib.parse.quote(msg)}') 
    # await bot.send_message(-config.DEBUG_CHANNEL_ID, str(msg), parse_mode=types.ParseMode.HTML)


class TgLoggerHandler(logging.Handler):
	def emit(self, record):
		msg = self.format(record)
		
		# print("\n"*20, f'https://api.telegram.org/bot{config.BOT_TOKEN}/sendMessage?chat_id=390442593&text={urllib.parse.quote(msg)}', "\n"*5, len(msg), "\n"*20)
		# requests.get(f'https://api.telegram.org/bot{config.BOT_TOKEN}/sendMessage?chat_id=390442593&text={urllib.parse.quote(msg)}') 
		return send_log_channel(msg)



tg_handler = TgLoggerHandler()
tg_handler.setLevel(logging.ERROR)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)


logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.DEBUG, handlers=[tg_handler, stream_handler] 
                    )