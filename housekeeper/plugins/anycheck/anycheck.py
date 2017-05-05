#!/usr/bin/env python3
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


import copy
import time
import random

import anydo.api


def is_delayed(task, now=None):
    if now is None:
        now = int(time.time())

    due = task.get('dueDate', None)
    if due is None:
        return False
    else:
        return now >= due


def rewrite_task(task, category_map=None):
    ret = copy.deepcopy(task)
    if category_map is None:
        category_map = dict()

    try:
        ret['category'] = category_map[ret['categoryId']]
    except KeyError:
        ret['category'] = '???'

    try:
        ret['dueDate'] = int(task['dueDate'] / 1000)
    except (KeyError, TypeError):
        ret['dueDate'] = None

    return ret


def is_subtask(task):
    return task.get('parentGlobalTaskId') is not None


def is_relevant(task):
    return (
        not is_subtask(task) and  # Strip subtasks
        task.get('status').lower() == 'unchecked')


def debug_format(task):
    return 'delayed:{delayed} list:{list} is_sub:{sub} title:{title}'.format(
        delayed='yes' if is_delayed(task) else 'no',
        list=task['category'],
        sub='yes' if is_subtask(task) else 'no',
        title=task['title'])


def build_sample(tasks, n=3):
    ret = []

    tasks = tasks.copy()
    n = min(len(tasks), n)

    for dummy in range(n):
        choice = random.randint(0, len(tasks) - 1)
        ret.append(tasks.pop(choice))

    return '\n'.join("- " + t['title'] for t in ret)


def get_delayed_tasks(username, password):
    api = anydo.api.AnyDoAPI(username, password)

    category_map = {cat['id']: cat['name']
                    for cat in api.get_all_categories()}

    tasks = api.get_all_tasks()
    tasks = map(lambda task: rewrite_task(task, category_map), tasks)
    tasks = filter(is_relevant, tasks)
    tasks = filter(lambda t: is_delayed(t), tasks)
    tasks = list(tasks)
    return tasks


def main(username, password):
    try:
        import gi
    except ImportError:
        import pgi
        pgi.install_as_gi()
        import gi

    gi.require_version('Notify', '0.7')
    from gi.repository import Notify

    tasks = get_delayed_tasks(username, password)
    if not tasks:
        return

    summary = "You have {n} tasks pending.".format(
        n=len(tasks))
    body = "Some of them are:\n{sample}".format(
        sample=build_sample(tasks))

    print(summary + "\n" + body)

    Notify.init('anyreport')
    notif = Notify.Notification(summary=summary, body=body)
    notif.show()


if __name__ == '__main__':
    import sys
    main(*sys.argv)
