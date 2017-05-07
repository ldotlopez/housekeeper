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


import collections


def list_in_list(needle, stack):
    if needle == stack:
        return 0

    if not needle:
        return 0

    if not stack:
        return -1

    if len(needle) > len(stack):
        return -1

    needle_len = len(needle)
    for stack_idx in range(0, len(stack) - needle_len + 1):
        if stack[stack_idx:stack_idx+needle_len] == needle:
            return stack_idx

    return -1


def walk_collection(collection):
    if isinstance(collection, collections.Mapping):
        yield from ((k, v) for (k, v) in collection.items())
    else:
        yield from enumerate(collection)
