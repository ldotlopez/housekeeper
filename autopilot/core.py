import abc
import os


import yaml
from appkit import (
    application,
    cache,
    cron,
    store,
    logging,
    utils
)


def user_path(*args, **kwargs):
    kwargs['prog'] = 'autopilot'
    return utils.user_path(*args, **kwargs)


class YAMLStore(store.Store):
    def __init__(self, *args, logger=None, **kwargs):
        super().__init__(*args, **kwargs)
        if not logger:
            logger = logging.NullLogger()

        self.logger = logger

    def dump(self, stream):
        buff = yaml.dump(self.get(None))
        stream.write(buff)

    def load(self, stream):
        buff = stream.read()
        data = yaml.load(buff)
        data = store.flatten_dict(data)
        for (k, v) in data.items():
            self.set(k, v)


class CronManager(cron.CronManager):
    @property
    def state_file(self):
        pathname = user_path(utils.UserPathType.DATA, 'state.json')
        os.makedirs(os.path.dirname(pathname), exist_ok=True)
        return pathname

    def load_state(self):
        state = store.Store()

        try:
            with open(self.state_file) as fh:
                state.load(fh)

        except FileNotFoundError:
            pass

        return state

    def save_state(self, state):
        with open(self.state_file, 'w+') as fh:
            state.dump(fh)

    def load_checkpoint(self, task):
        store = self.load_state()

        key = 'cron.taskstate.{}'.format(task.__extension_name__)
        ret = store.get(key, default={})

        return ret

    def save_checkpoint(self, task, checkpoint):
        store = self.load_state()

        for (k, v) in checkpoint.items():
            k = 'cron.taskstate.{name}.{key}'.format(
                name=task.__extension_name__,
                key=k)

            store.set(k, v)

        self.save_state(store)


class CronService(CronManager, application.Service):
    __extension_name__ = 'cron'


import sys

class Core(application.CommandlineApplicationMixin,
           application.ServiceApplicationMixin,
           application.BaseApplication):
    def __init__(self):
        # Initialize external modules
        logging.setLevel(logging.Level.WARNING)

        # super()
        pluginpath = os.path.dirname(os.path.realpath(__file__)) + "/plugins"
        super().__init__('autopilot', pluginpath=pluginpath)
        self.register_extension_point(Callable)
        self.register_extension_class(CronService)
        self.register_extension_class(cron.CronCommand)

        # Read command line
        app_parser = self.build_argument_parser()
        app_args, dummy = app_parser.parse_known_args(sys.argv[1:])

        # Read config files
        self.settings = YAMLStore()
        configfiles = [user_path(utils.UserPathType.CONFIG, 'autopilot.yml')]
        configfiles.extend(getattr(app_args, 'config-files', []))
        for cf in configfiles:
            try:
                with open(cf) as fh:
                    self.settings.load(fh)

            except FileNotFoundError:
                msg = "Config file «{path}» not found"
                msg = msg.format(path=cf)
                self.logger.warning(msg)

        # Apply command line arguments: debug level
        cf_log_level = self.settings.get('log-level', None)
        if cf_log_level:
            try:
                level = getattr(logging.Level, cf_log_level, None)
                logging.setLevel(level)
            except AttributeError:
                msg = "Invalid «log-level={level}» key in settings"
                msg = msg.format(level=cf_log_level)
                self.logger.error(msg)
        else:
            level = logging.getLevel()
            diff = app_args.verbose - app_args.quiet
            logging.setLevel(logging.Level.incr(level, n=diff))

        # Initialize cache
        self.cache = cache.DiskCache(
            basedir=user_path(utils.UserPathType.CACHE))

    def get_extension(self, extension_point, name, *args, **kwargs):
        msg = "Calling extension «{}.{}::{}» (args={}, kwargs={})"
        msg = msg.format(
            extension_point.__module__,
            extension_point.__name__,
            name,
            repr(args),
            repr(kwargs))
        self.logger.debug(msg)

        cls = self._get_extension_class(extension_point, name)
        if issubclass(cls, AutopilotExtension):
            ret = cls(self.settings, *args, **kwargs)
        else:
            ret = super().get_extension(extension_point, name, *args, **kwargs)

        return ret

    def notify(self, summary, body=None, asset=None, actions=None):
        print("*{}*".format(summary))
        if body:
            print(body)

        for (label, callable_, args, kwargs) in actions:
            callable_ = self.get_extension(Callable, callable_)
            print("{label}: {desc}".format(
                label=label,
                desc=callable_.stringify()))


class AutopilotExtension:
    def __init__(self, settings, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__extension_name__)
        self.settings = settings


class Callable(AutopilotExtension, application.Extension):
    @abc.abstractmethod
    def call(self, *args, **kwargs):
        raise NotImplementedError()

    @abc.abstractmethod
    def stringify(self, *args, **kwargs):
        raise NotImplementedError()
