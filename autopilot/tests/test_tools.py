import unittest

from autopilot.tools import (
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
