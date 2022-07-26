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


class TgLoggerHandler(logging.Handler):
	def emit(self, record):
		msg = self.format(record)
		return send_log_channel(msg)


tg_handler = TgLoggerHandler()
tg_handler.setLevel(logging.ERROR)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)


logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.DEBUG, handlers=[tg_handler, stream_handler] 
                    )