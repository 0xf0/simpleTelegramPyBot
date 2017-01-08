# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import logging

txt = {
    "token_not_set": "[-] telegram token not set",
    "requests_error": "[-] requests error: {e}",
    "method_error": "[-] got an error: {e}",
    "method_exception": "[-] got an exception: {e}\n\tdata: {data}"
}
log = logging.getLogger(__name__)


class API(object):
    def __init__(self, token=None, **kwargs):
        self.__token = token
        self.__method = kwargs.get("method", "")

    def __request(self, **kwargs):
        r = ""

        if self.__token:
            url = "https://api.telegram.org/bot{token}/{method}".format(token=self.__token, method=self.__method)
            try:
                r = requests.post(url, data=kwargs, timeout=10.0).json()
            except Exception as e:
                log.critical(txt["requests_error"].format(e=e))
        else:
            log.warning(txt["token_not_set"])
        return r

    def __getattr__(self, attr):
        method = ("{method}.{attr}".format(method=self.__method, attr=attr)).lstrip('.')
        return API(self.__token, method=method)

    def __call__(self, **kwargs):
        return self.__request(**kwargs)

    @staticmethod
    def parse(_m):
        if "message" in _m:
            m = _m["message"]
            first_name = m["from"]["first_name"] if "first_name" in m["from"] else ""
            last_name = m["from"]["last_name"] if "last_name" in m["from"] else ""
            username = m["from"]["username"] if "username" in m["from"] else ""

            data = {"chat_id": m["chat"]["id"],
                    "name": "{fname} {lname}".format(fname=first_name, lname=last_name),
                    "username": username,
                    "user_id": m["from"]["id"],
                    "type": m["chat"]["type"],
                    "date": m["date"],
                    "text": m["text"],
                    "ok": True}
        elif "callback_query" in _m:
            m = _m["callback_query"]
            first_name = m["from"]["first_name"] if "first_name" in m["from"] else ""
            last_name = m["from"]["last_name"] if "last_name" in m["from"] else ""
            username = m["from"]["username"] if "username" in m["from"] else ""

            data = {
                "chat_id": m["from"]["id"],
                "name": "{fname} {lname}".format(fname=first_name, lname=last_name),
                "username": username,
                "user_id": m["from"]["id"],
                "data": m["data"],
                "ok": True
            }
        else:
            data = _m

        return data

    @staticmethod
    def method_errors(data):
        try:
            if "ok" in data and data["ok"]:
                return False
            else:
                log.warning(txt["method_error"].format(e=data))
                return True
        except Exception as e:
            log.critical(txt["method_exception"].format(e=e, data=data))
            return True
