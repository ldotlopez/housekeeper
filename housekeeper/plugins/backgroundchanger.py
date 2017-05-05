from housekeeper import pluginlib


import os
import random
import re
import subprocess


from appkit import store


__ME__ = 'background-changer'

SETTINGS_NS = __ME__
DIRECTORIES_KEY = __ME__ + ".directories"


class API:
    def __init__(self, directories=None):
        self._dirs = set()
        for d in directories or []:
            self.add_directory(d)

    @property
    def platform(self):
        x = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()

        if x == 'gnome':
            return 'gnome'

        msg = 'Unknow platform'
        raise APIError(msg)

    def add_directory(self, directory):
        directory = os.path.expanduser(directory)
        self._dirs.add(directory)

    def random(self):
        imgs = []
        for d in self._dirs:
            d = os.path.expanduser(d)
            for (path, dirs, files) in os.walk(d):
                tmp = filter(self._is_image,
                             files)
                tmp = map(lambda f: os.path.join(path, f),
                          tmp)
                imgs.extend(tmp)

        if not imgs:
            msg = "No images availables. Maybe it's a permission problem?"
            raise APIError(msg)

        return random.choice(imgs)

    def update(self, path):
        platform = self.platform

        if platform == 'gnome':
            cmd = ['/usr/bin/gsettings', 'set', 'org.gnome.desktop.background',
                   'picture-uri', path]

        else:
            msg = "Unknow platform"
            raise APIError(msg)

        try:
            subprocess.check_call(cmd)
        except subprocess.CalledProcessError as e:
            msg = "Error in subprocess {cmdl}"
            msg = msg.format(' '.join(map(lambda x: "'{}'".format(x), cmd)))
            raise APIError(msg)

    def refresh(self):
        choice = self.random()
        self.update(choice)
        return choice

    def _is_image(self, filename):
        return re.search(r'\.(jpe?g|gif|tiff?|png)$', filename, re.IGNORECASE)


class APIError(Exception):
    pass


class Task(pluginlib.Task):
    __extension_name__ = 'background-changer'
    INTERVAL = '15M'

    def execute(self, app):
        logger = app.logger.getChild(__ME__)

        try:
            dirs = app.settings.get(DIRECTORIES_KEY)

        except store.KeyNotFoundError as e:
            msg = "Plugin not configured, check {key} value"
            msg = msg.format(key=DIRECTORIES_KEY)

            raise pluginlib.ConfigurationError(msg) from e

        choice = API(directories=dirs).refresh()

        logger = app.logger.getChild(__ME__)
        msg = "Background updated with {path}"
        msg = msg.format(path=choice)
        logger.info(msg)


class Command(pluginlib.Command):
    __extension_name__ = __ME__

    HELP = 'Change desktop background'
    ARGUMENTS = (
        pluginlib.argument(
            '-d', '--directory',
            action='append',
            dest='dirs',
            help='Choose random background from directory',
            required=False
        ),
    )

    def __init__(self, settings, *args, **kwargs):
        super().__init__(settings, *args, **kwargs)
        self.settings = settings

    def execute(self, app, arguments):
        logger = app.logger.getChild(__ME__)

        try:
            dirs = (arguments.dirs or
                    self.settings.get(__ME__ + '.directories', []))

        except store.KeyNotFoundError as e:
            msg = "Plugin not configured, check {key} value"
            msg = msg.format(key=DIRECTORIES_KEY)

            raise pluginlib.ConfigurationError(msg) from e

        api = API(directories=dirs)
        try:
            choice = api.refresh()
        except APIError as e:
            raise pluginlib.ExtensionError(str(e)) from e

        logger = app.logger.getChild(__ME__)
        msg = "Background updated with {path}"
        msg = msg.format(path=choice)
        logger.info(msg)


__housekeeper_extensions__ = [
    Command,
    Task
]
