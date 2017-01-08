# !/usr/bin/env python3
# -*- coding: utf-8 -*-
import config
import logging
from time import sleep
from queue import Queue
from threading import Thread
from core import telegram


# format answer message
def queue_answer(chat_id, text, parse_mode=None, disable_web_page_preview=None, disable_notification=None,
                 reply_markup=None):
    q.put((chat_id, text, parse_mode, disable_web_page_preview, disable_notification, reply_markup))


# telegram chat worker
def handler():
    offset = 0
    while True:
        sleep(config.TELEGRAM_UPDATE_INTERVAL)
        u = tg.getUpdates(offset=offset + 1, limit=100, timeout=0, allowed_updates=["message", "inline_query",
                                                                                    "chosen_inline_result",
                                                                                    "callback_query"])
        if not tg.method_errors(u):
            for item in u["result"]:
                data = tg.parse(item)
                offset = item["update_id"]

                # here you can do anythig with parsed data in data dict
                if "/start" in data["text"]:
                    queue_answer(chat_id=data["chat_id"], text="*Hello!*", parse_mode="Markdown")


# message send queue worker
def worker():
    while True:
        additional_params = {}
        chat_id, text, parse_mode, disable_web_page_preview, disable_notification, reply_markup = q.get()

        if parse_mode:
            additional_params["parse_mode"] = parse_mode
        if disable_web_page_preview:
            additional_params["disable_web_page_preview"] = True
        if disable_notification:
            additional_params["disable_notification"] = True
        if reply_markup:
            additional_params["reply_markup"] = reply_markup

        tg.sendMessage(chat_id=chat_id, text=text, **additional_params)
        q.task_done()
        sleep(config.TELEGRAM_SENDMESSAGE_INTERVAL)


if __name__ == "__main__":
    # logging
    logging.basicConfig(level=config.LOGLEVEL, format=config.LOGFORMAT)
    file_handler = logging.FileHandler("bot.log")
    file_handler.setFormatter(logging.Formatter(config.LOGFORMAT))
    logging.getLogger().addHandler(file_handler)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)
    logging.getLogger("requests.packages.urllib3.connectionpool").setLevel(logging.WARNING)

    # telegram daemon
    tg = telegram.API(token=config.TELEGRAM_TOKEN)
    th = Thread(target=handler)
    th.daemon = True
    th.start()

    # message to send queue
    q = Queue()
    mt = Thread(target=worker)
    mt.start()

    mt.join()
    th.join()
