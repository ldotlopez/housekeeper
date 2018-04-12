#!/usr/bin/env python3


import argparse
import asyncio
import configparser
import dbm
import functools
import json
import logging
import os
import sys
from os import path


import aiotg


UNDEF = object()


def log(fn):
    @functools.wraps(fn)
    def _wrapper(*args, **kwargs):
        print(fn)
        return fn(*args, **kwargs)

    return _wrapper


def require(level):
    def _require(fn):
        @functools.wraps(fn)
        async def _wrapper(tg, chat, *args, **kwargs):
            if level == 'admin' and chat.sender['id'] not in tg.administrators:
                return (await chat.send_text('Not allowed'))

            return (await fn(tg, chat, *args, **kwargs))

        return _wrapper

    return _require


def sync(coro):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)


class State:
    SEP = '.'

    def __init__(self, path):
        self._db = dbm.open(path, 'c')

    def _normalize_key(self, key):
        if not isinstance(key, (list, bytes, str)):
            raise TypeError(key)

        if isinstance(key, bytes):
            key = key.decode('ascii')

        if isinstance(key, str):
            key = key.split(self.SEP)

        key = (str(x).strip(self.SEP) for x in key)
        key = (x for x in key if x)

        return self.SEP.join(key).encode('ascii')

    def children(self, prefix=''):
        if prefix is '':
            yield from set([
                x.split(self.SEP)[0]
                for x in self._db.keys()
            ])

        else:
            prefix = prefix + self.SEP
            yield from set([
                x.split(self.SEP)[0]
                for x in self._db.keys()
            ])

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


class Users:
    def __init__(self, state):
        self.state = state

    def get(self, id):
        return self.state.get(
            ['users', id],
            None)

    def register(self, user):
        return self.state.set(
            ['users', user['id']],
            user)


class HKTelegram(aiotg.Bot):
    def __init__(self, token, state, administrators=None):
        super().__init__(api_token=token)

        self.logger = logging.getLogger()
        self.administrators = administrators or []
        self.users = Users(state)

    # @log
    # async def _do_start(self, chat, match,):
    #     user_key = 'user/' + str(chat.sender['id'])
    #     user_data = {
    #         'seen': False
    #     }

    #     user_data = self.state.get(user_key, user_data)
    #     if not user_data['seen']:
    #         await chat.send_text("Nice to meet you")
    #         user_data['seen'] = True
    #         self.state.set(user_key, user_data)

    #     else:
    #         await chat.send_text("Nice to see you again")

    # @require('admin')
    # @log
    # async def _do_stop(self, chat, match):
    #     await chat.send_text('OK')

    @log
    async def _do_registrations(self, chat, match):
        user = self.users.get(chat.sender['id'])

        if not user:
            self.users.register(chat.sender)
            text = "Nice to meet you {username}"
            text = text.format(**user)
            chat.send_text(text)

            climsg = 'NEW_USER {id}:{username}'
            climsg = climsg.format(**user)

        else:
            text = "Nice to see you again {username}"
            text = text.format(**user)
            chat.send_text(text)

    @log
    def run(self):
        self.add_command('start', self._do_start)
        self.add_command('stop', self._do_stop)
        super().run()

    @log
    def listen(self):
        self.add_command('start', self._do_registrations)
        super().run()


def load_profile(cp, profile=None):
    if profile is None:
        profile = cp.get('DEFAULTS', 'profile')

    return profile, {
        'token': cp.get(profile, 'token'),
        'administrators': [
            int(x.strip()) for x in
            cp.get(profile, 'administrators', fallback='').split(',')]
    }


def main():
    import sys

    configfile = path.expanduser('~/.config/hk-telegram.ini')

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-c', '--config',
        default=configfile,
        help="Config file")
    parser.add_argument(
        '-p', '--profile',
        default=None)
    parser.add_argument(
        '--listen',
        action='store_true'
    )
    parser.add_argument(
        'message',
        nargs='?')
    args = parser.parse_args(sys.argv[1:])

    cp = configparser.ConfigParser()
    cp.read(args.config)

    profile, tg_params = load_profile(cp, args.profile)

    statefile = path.expanduser(
        '~/.local/share/hk-telegram/' + profile + '/state')
    os.makedirs(path.dirname(statefile), exist_ok=True)

    tg_params['state'] = State(path=statefile)
    bot = HKTelegram(**tg_params)

    if args.listen:
        print("Listening for '/start's")
        bot.listen()


if __name__ == '__main__':
    main()
