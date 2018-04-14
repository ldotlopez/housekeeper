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
import appkit.utils


UNDEF = object()


class ArgumentsError(Exception):
    pass


class ConfigurationError(Exception):
    pass


def log(fn):
    @functools.wraps(fn)
    def _wrapper(*args, **kwargs):
        if os.environ.get('HK_DEBUG', ''):
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

        return json.loads(ret.decode('ascii'))

    def delete(self, key):
        key = self._normalize_key(key)
        del(self._db[key])

        self._db[key] = value


class Users:
    def __init__(self, state):
        self.state = state

    def get(self, id):
        return self.state.get(
            'users/{}'.format(id),
            None)

    def register(self, user):
        return self.state.set(
            'users/{}'.format(user['id']),
            user)


class HKTelegram(aiotg.Bot):
    def __init__(self, token, state, administrators=None):
        super().__init__(api_token=token)

        self.logger = logging.getLogger()
        self.administrators = administrators or []
        self.users = Users(state)

    @log
    async def _do_registrations(self, chat, match):
        user = self.users.get(chat.sender['id'])

        if not user:
            user = chat.sender
            self.users.register(user)
            text = "Nice to meet you {username}"
            text = text.format(**user)
            chat.send_text(text)

            climsg = 'NEW_USER {id}:{username}'
            climsg = climsg.format(**user)
            print(climsg)

        else:
            text = "Nice to see you again {username}"
            text = text.format(**user)
            chat.send_text(text)

            climsg = 'RETUNING_USER {id}:{username}'
            climsg = climsg.format(**user)
            print(climsg)

    @log
    def run(self):
        self.add_command('start', self._do_start)
        self.add_command('stop', self._do_stop)
        super().run()

    @log
    async def send(self, id, message):
        await self.private(id).send_text(message)

    @log
    def send_and_stop(self, id, message):
        sync(self.send(id, message))
        asyncio.get_event_loop().call_soon(self.stop)

    @log
    def listen(self):
        self.add_command('start', self._do_registrations)
        super().run()


def load_profile(configfile, profile=None):
    cp = configparser.ConfigParser()
    cp.read(configfile)

    if profile is None:
        profile = cp.get('DEFAULTS', 'profile', fallback=None)

    if profile is None:
        err = "Missing [DEFAULTS]:profile key"
        raise ConfigurationError(err)

    opts = {}
    for (opt, fallback) in [
            ('token', configparser._UNSET),
            ('administrators', '')]:

        try:
            opts[opt] = cp.get(profile, opt, fallback=fallback)
        except KeyError:
            err = "Missing [{}}:{} key"
            err = err.format(profile, opt)
            raise ConfigurationError(err)

    opts['state'] = State(
        appkit.utils.user_path(appkit.utils.UserPathType.DATA,
                               prog="hk-telegram",
                               create=True) +
        '/' + profile + '-state')

    opts['administrators'] = [
        x.strip() for x in
        opts['administrators'].split(',')
    ]

    return profile, opts


def main():
    import sys

    configfile = appkit.utils.prog_config_file(prog='hk-telegram')

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
        action='store_true')
    parser.add_argument(
        '--send-to',
        help='Send message to someone')
    parser.add_argument(
        'message',
        nargs='?')

    args = parser.parse_args(sys.argv[1:])
    if args.listen and args.send_to:
        errmsg = 'Options --listen and --send-to are mutually exclusive'
        raise ArgumentsError(errmsg)

    if not args.listen and not args.send_to:
        errmsg = 'One of --listen or --send-to options is required'
        raise ArgumentsError(errmsg)

    if args.send_to and not args.message:
        errmsg = 'Missing message'
        raise ArgumentsError(errmsg)

    profile, tg_params = load_profile(args.config, args.profile)
    bot = HKTelegram(**tg_params)

    if args.listen:
        print("Listening for '/start's")
        bot.listen()

    elif args.send_to:
        bot.send_and_stop(args.send_to, args.message)


if __name__ == '__main__':
    main()
