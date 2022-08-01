import datetime
import json
import logging
import os
import time
import requests

from queue import Queue
from datetime import date
from typing import List

queue = Queue()

def get_diretorio_log():
  """Works for create log after run bot
  """
  # defina o nome do diretório a ser criado
  path = './messager_telegram/{}/{}/{}'.format(date.today().year, date.today().month, date.today().day)
  try:
    if not os.path.isdir(path):
      os.makedirs(path)
  except OSError as e:
    logging.exception(e)
    raise
  return path

logging.basicConfig(
    filename='{}/{}.log'.format(
        get_diretorio_log(),
        datetime.datetime.now().strftime('%Y%m%d')
    ), 
    level=(logging.INFO), 
    format='%(asctime)s %(threadName)s %(levelname)s %(module)s %(lineno)d %(funcName)s => %(message)s'
)

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# ██████╗ ██╗   ██╗
# ██╔══██╗╚██╗ ██╔╝
# ██████╔╝ ╚████╔╝ 
# ██╔══██╗  ╚██╔╝  
# ██████╔╝   ██║   
# ╚═════╝    ╚═╝          
# ██╗     ███████╗ ██████╗ ███╗   ███╗ █████╗  ██████╗██╗  ██╗ █████╗ ██████╗  ██████╗ ██████╗ ███████╗
# ██║     ██╔════╝██╔═══██╗████╗ ████║██╔══██╗██╔════╝██║  ██║██╔══██╗██╔══██╗██╔═══██╗██╔══██╗██╔════╝
# ██║     █████╗  ██║   ██║██╔████╔██║███████║██║     ███████║███████║██║  ██║██║   ██║██║  ██║███████╗
# ██║     ██╔══╝  ██║   ██║██║╚██╔╝██║██╔══██║██║     ██╔══██║██╔══██║██║  ██║██║   ██║██║  ██║╚════██║
# ███████╗███████╗╚██████╔╝██║ ╚═╝ ██║██║  ██║╚██████╗██║  ██║██║  ██║██████╔╝╚██████╔╝██████╔╝███████║
# ╚══════╝╚══════╝ ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝  ╚═════╝ ╚═════╝ ╚══════╝
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

horarios = ['12:08', '12:09', '12:10', '12:11']

class TelegramMessager():
    ''' (en) Class responsible for sending messages to users on telegram
  To use the methods, plese use threads with the methods present in the class!
    
 (pt) Classe responsável por enviar mensagens para usuários no telegram
 Para utulizar os métodos gere threads com os métodos presentes na classe !
 
 
 TOKEN_BOT: Telegram bot (get via bot father)
 chat_id: user_id or group id that you want to send messages to
 schedule_time: exactly time, that you want to send messages, format: ['15:15', '20:20', '21:30', '22:30']
 
 
 '''
    # DO NOT CHANGE THE SAMPLE_MESSAGE
    sample_msg = '''Hello world!'''
 
    def __init__(self, TOKEN_BOT: str, chat_id: int = None, schedule_time: List[str]=None):
        self.TOKEN_BOT = TOKEN_BOT
        self.chat_id = chat_id
        self.schedule_time = schedule_time

    def th_add_message_to_queue(self, msg=sample_msg, keyboard_inline=None) -> None:
        ''' msg: Message that you want to send to user or group telegram
 keyboard_inline: keyboard_inline JSON format:
 
 sample_keyboard = {
                 "inline_keyboard": [
                    [
                         {"text": "Plano Básico 💎", "callback_data": "1" },
                         {"text": "Plano Plus 💎", "callback_data": "2"}
                    ],
                    [
                         {"text": "Salas Sinais 💎", "callback_data": "3"}
                    ]
                 ]
             } '''
        log.info('Queue initialized...')
        while True:
            hour_minute = datetime.datetime.now().strftime('%H:%M')
            if not self.schedule_time:
                print("Please pass schedule_time like ['15:15', '20:20', '21:30', '22:30'] ")
            if hour_minute in self.schedule_time:
                try:
                    log.info('Trying to send message via queue')
                    queue.put((self.chat_id, msg, keyboard_inline))
                    time.sleep(60)
                except Exception as e:
                    log.error(e)
                
            time.sleep(1)
            
    def th_send_message_queue(self) -> None:
        while True:
           
                try:
                    chat_id, msg, keyboard = queue.get()
                    log.info('Trying to send message...')
                    if keyboard:
                        url = f"https://api.telegram.org/bot{self.TOKEN_BOT}/sendMessage"

                        payload = {
            "text": msg,
            "parse_mode": "MARKDOWN",
            "disable_web_page_preview": True,
            "disable_notification": False,
            "reply_to_message_id": None,
            "chat_id": str(chat_id),
            "reply_markup": json.dumps(keyboard)
        }
                        headers = {
            "Accept": "application/json",
            "User-Agent": "Telegram Bot SDK - (https://github.com/irazasyed/telegram-bot-sdk)",
            "Content-Type": "application/json"
        }               
                        response = requests.post(url, json=payload, headers=headers)
                        log.info('Message sent with success!')
                    else:
                        url = f"https://api.telegram.org/bot{self.TOKEN_BOT}/sendMessage?chat_id={chat_id}&text={msg}"
                        log.info(f'{url}')
                        response = requests.get(url)
                        log.info('Message sent with success!')
                except Exception as e:
                    log.error(e)
                    print(e)
                    
                queue.task_done()