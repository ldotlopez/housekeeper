#!/usr/bin/env python3


import configparser
import dbm
import functools
import logging
import sys
from os import path
import json


from telegram.ext import CommandHandler, Updater


def reply(bot, update, **kwargs):
    bot.send_message(chat_id=update.message.chat_id, **kwargs)


def require(level):
    def _require(fn):
        @functools.wraps(fn)
        def _wrapper(tg, bot, update):
            sender = update.message.from_user.name
            if level == 'admin' and sender not in tg.admins:
                reply(bot, update, text='Not allowed')
                return

            return fn(tg, bot, update)

        return _wrapper

    return _require


def log(fn):
    @functools.wraps(fn)
    def _wrapper(*args, **kwargs):
        print(fn)
        return fn(*args, **kwargs)

    return _wrapper


UNDEF = object()


class State:
    def __init__(self, path):
        self._db = dbm.open(path, 'c')

    def _normalize_key(self, key):
        if isinstance(key, str):
            key = key.encode('ascii')

        if not isinstance(key, bytes):
            raise TypeError(key)

        return key

    def set(self, key, value):
        key = self._normalize_key(key)
        self._db[key] = json.dumps(value)

    def get(self, key, default=UNDEF):
        key = self._normalize_key(key)
        try:
            ret = self._db[key]
        except KeyError:
            if default is not UNDEF:
                return default
            else:
                raise

        return json.loads(ret)

    def delete(self, key):
        key = self._normalize_key(key)
        del(self._db[key])

        self._db[key] = value


class Tg:
    def __init__(self, token, state, admins=None, ):
        self.token = token
        self.admins = admins or []
        self.state = state
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger()
        self.updater = Updater(token=self.token)
        self.dispatcher = self.updater.dispatcher
        self.dispatcher.add_handler(
            CommandHandler('start', self._handle_start))
        self.dispatcher.add_handler(
            CommandHandler('stop', self._handle_stop))

    @log
    def _handle_start(self, bot, update):
        user_key = 'user/' + str(update.message.from_user.id)
        user_data = {
            'seen': False
        }

        user_data = self.state.get(user_key, user_data)
        if not user_data['seen']:
            reply(bot, update, text="Nice to meet you")
            user_data['seen'] = True
            self.state.set(user_key, user_data)

        else:
            reply(bot, update, text="Nice to see you again")

    @require('admin')
    @log
    def _handle_stop(self, bot, update):
        reply(bot, update, text="Stop")

    @log
    def run(self):
        print("Ready!")
        self.updater.start_polling()


def main():
    cp = configparser.ConfigParser()
    confpath = path.join(
        path.dirname(path.realpath(__file__)),
        'telegram.ini')
    cp.read(confpath)

    tg_state_path = path.join(
        path.dirname(path.realpath(__file__)),
        'telegram.db')

    tg_state = State(tg_state_path)
    tg_token = cp.get('telegram', 'token')
    tg_admins = [x.strip() for x in
                 cp.get('telegram', 'admins', fallback='').split(',')]

    tg = Tg(token=tg_token, admins=tg_admins, state=tg_state)
    tg.run()


if __name__ == '__main__':
    main()
