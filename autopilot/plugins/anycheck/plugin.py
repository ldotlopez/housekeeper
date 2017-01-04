from autopilot import core
from autopilot.plugins.anycheck import anycheck


from appkit import (
    application,
    cache,
    cron
)


import webbrowser


class AnyCheckCallable(core.Callable):
    __extension_name__ = 'anychecker.openwebapp'

    def call(self, *args, **kwargs):
        webbrowser.open_new('http://www.any.do')

    def stringify(self, *args, **kwargs):
        return "Open in a webbrowser http://www.any.do"


class AnyCheckCronTask(core.AutopilotExtension, cron.CronTask):
    __extension_name__ = 'anycheck'
    interval = '4H'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        u = self.settings.get('anycheck.username', None)
        p = self.settings.get('anycheck.password', None)

        if not u or not p:
            msg = "Please check username/password in your configuration"
            raise application.ConfigurationError(msg)

        self.config = dict(username=u, password=p)

    def execute(self, app):
        try:
            anytasks = app.cache.get('anycheck.tasks', delta=self.interval)

        except cache.CacheMissError:
            anytasks = anycheck.get_delayed_tasks(**self.config)
            app.cache.set('anycheck.tasks', anytasks)

        if not anytasks:
            return

        summary = "You have {n} tasks pending.".format(
            n=len(anytasks))

        body = "Some of them are:\n{sample}".format(
            sample=anycheck.build_sample(anytasks))

        app.notify(
            summary, body,
            actions=[
                ('Open Any.do', 'anychecker.openwebapp', None, None)
            ]
        )

__autopilot_extensions__ = [
    AnyCheckCallable,
    AnyCheckCronTask
]
