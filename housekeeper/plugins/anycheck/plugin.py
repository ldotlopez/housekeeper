# -*- coding: utf-8 -*-

# Copyright (C) 2015 Luis López <luis@cuarentaydos.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301,
# USA.


from housekeeper import pluginlib
from housekeeper.plugins.anycheck import anycheck


from appkit import cache


import webbrowser


class Callable(pluginlib.Callable):
    __extension_name__ = 'anychecker.openwebapp'

    def call(self, *args, **kwargs):
        webbrowser.open_new('http://www.any.do')

    def stringify(self, *args, **kwargs):
        return "Open in a webbrowser http://www.any.do"


class Task(pluginlib.Task):
    __extension_name__ = 'anycheck'
    INTERVAL = '4H'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        u = self.settings.get('anycheck.username', None)
        p = self.settings.get('anycheck.password', None)

        if not u or not p:
            msg = "Please check username/password in your configuration"
            raise pluginlib.ConfigurationError(msg)

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

__housekeeper_extensions__ = [
    Callable,
    Task
]
