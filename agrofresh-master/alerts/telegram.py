from .models import TelegramNotificationSettings
from historical.models import Event
from urllib import request, parse
import asyncio
import json
import logging
import os
logger = logging.getLogger(__name__)


# https://github.com/butorov/sentry-telegram/blob/master/sentry_telegram/plugin.py
# https://github.com/sinarezaei/alerting/blob/master/alerting/clients.py

def bot_api_method(settings, method):
    # https://api.telegram.org/bot<token>/METHOD_NAME
    return f"https://api.telegram.org/bot{settings.api_token}/{method}"


def send_message(message):
    # TODO settings as argument?
    settings = TelegramNotificationSettings.load()
    if not settings.enabled:
        return

    chat_ids = [
        chat_id.strip()
        for chat_id in settings.receivers.split()
    ]

    url = bot_api_method(settings, "sendMessage")

    for chat_id in chat_ids:
        data = parse.urlencode({
            'chat_id': chat_id,
            'text': message,
        }).encode()
        http_post(url, data)


def get_updates(settings):
    if not isinstance(settings, TelegramNotificationSettings):
        return

    url = bot_api_method(settings, "getUpdates")
    response = http_get(url)

    if not isinstance(response, dict) and response.get('ok'):
        return

    for update in response.get("result", []):
        message = update.get("message", {})
        chat = message.get("chat", {})
        yield {
            "chat_id" : chat.get("id"),
            "first_name" : chat.get("first_name"),
            "text" : message.get("text", ""),
        }


def get_bot_info(settings):
    if not isinstance(settings, TelegramNotificationSettings):
        return

    url = bot_api_method(settings, "getMe")
    response = http_get(url)

    if not isinstance(response, dict) and response.get('ok'):
        return

    result = response.get("result", {})
    return {
        "bot_id" : result.get("id"),
        "first_name" : result.get("first_name"),
        "username" : result.get("username"),
    }


def process_response(resp):
    info = resp.info()
    raw_data = resp.read()
    logger.info(f"{resp._method} {resp.url} -> {resp.status} {resp.reason}")
    mimetype = info.get_content_type()
    encoding = info.get_content_charset('utf8')
    data = raw_data.decode(encoding)

    if mimetype == 'application/json':
        data = json.loads(data)

    logger.info(f"Response data: {mimetype} {data}")
    return data


def http_post(url, data=None):
    req = request.Request(url, method="POST", data=data)
    with request.urlopen(req) as resp:
        return process_response(resp)


def http_get(url, data=None):
    req = request.Request(url, method="GET", data=data)
    with request.urlopen(req) as resp:
        return process_response(resp)
