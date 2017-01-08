# !/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import config


def start(**kwargs):
    if kwargs["name"]:
        name = re.sub("<[^>]+>", "", kwargs["name"])
    elif kwargs["username"]:
        name = re.sub("<[^>]+>", "", kwargs["username"])
    else:
        name = "Аноним"
    text = ["Привет <b>{name}</b>! Вот что я умею:".format(name=name)]
    for k, v in config.TELEGRAM_COMMANDS.items():
        text.append("/{cmd} - {description}".format(cmd=k, description=v["description"]))
    return {"chat_id": kwargs["chat_id"], "text": "\n".join(text), "parse_mode": "HTML"}
