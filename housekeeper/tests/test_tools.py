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


import unittest

from housekeeper.tools import (
    list_in_list,
    pathname_replace,
    pathname_split,
)


class SplitTest(unittest.TestCase):
    def test_absolute(self):
        self.assertEqual(
            pathname_split('/a'),
            ['', 'a']
        )

        self.assertEqual(
            pathname_split('/a/b'),
            ['', 'a', 'b']
        )

    def test_absolute_leading(self):
        self.assertEqual(
            pathname_split('/a/'),
            ['', 'a']
        )

        self.assertEqual(
            pathname_split('/a/b/'),
            ['', 'a', 'b']
        )

    def test_relative(self):
        self.assertEqual(
            pathname_split('a/b'),
            ['a', 'b']
        )

    def test_relative_leading(self):
        self.assertEqual(
            pathname_split('a/b/'),
            ['a', 'b']
        )

    def test_multiple_slashes(self):
        self.assertEqual(
            pathname_split('a//b/'),
            ['a', 'b']
        )


class ListInListTest(unittest.TestCase):
    def test_empty_stack(self):
        self.assertEqual(
            list_in_list([1], []),
            -1
        )

    def test_empty_needle(self):
        self.assertEqual(
            list_in_list([], [1]),
            0
        )

    def test_needle_is_stack(self):
        self.assertEqual(
            list_in_list([1], [1]),
            0
        )

    def test_needle_bigger_than_stack(self):
        self.assertEqual(
            list_in_list([1, 2], [1]),
            -1
        )

    def test_needle_at_start(self):
        self.assertEqual(
            list_in_list([1, 2], [1, 2, 3, 4]),
            0
        )

    def test_needle_at_end(self):
        self.assertEqual(
            list_in_list([3, 4], [1, 2, 3, 4]),
            2
        )

    def test_needle_at_middle(self):
        self.assertEqual(
            list_in_list([2, 3], [1, 2, 3, 4]),
            1
        )


class ReplacePathTest(unittest.TestCase):
    def test_base_case(self):
        self.assertEqual(
            pathname_replace('/oldroot', '/newroot', '/oldroot/file'),
            '/newroot/file'
        )

    def test_leading_slash_on_repl(self):
        self.assertEqual(
            pathname_replace('/oldroot', '/newroot/', '/oldroot/file'),
            '/newroot/file'
        )

    def test_base_and_path_equal(self):
        self.assertEqual(
            pathname_replace('/oldroot', '/newroot', '/oldroot'),
            '/newroot'
        )

    def test_base_and_path_equal_with_leadings(self):
        self.assertEqual(
            pathname_replace('/oldroot', '/newroot', '/oldroot/'),
            '/newroot'
        )

        self.assertEqual(
            pathname_replace('/oldroot/', '/newroot', '/oldroot/'),
            '/newroot'
        )
