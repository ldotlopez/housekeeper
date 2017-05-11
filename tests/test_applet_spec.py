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


import functools
import inspect


class Applet:
    def validator(self, method, *args, **kwargs):
        raise NotImplementedError()

    @property
    def METHODS(self):
        x = [x for x in dir(self) if x != 'METHODS']
        x = [(x, getattr(self, x)) for x in x]
        x = [(name, member) for (name, member) in x
             if inspect.ismethod(member) and
                hasattr(member, '__hk_method__')]

        return [name for (name, _) in x]

    @staticmethod
    def method(fn):
        @functools.wraps(fn)
        def _fn(obj, *args, **kwargs):
            sig = inspect.signature(fn)
            params = [(k, v) for (k, v) in sig.parameters.items()]
            params = params[1:]  # Skip self
            kw_ = {}
            for value in args:
                kwname = params[0]
                kw_[kwname] = value
                params = params[1:]

            import ipdb; ipdb.set_trace(); pass
            return fn(obj, *args, **kwargs)

        _fn.__hk_method__  = True
        return _fn

method = Applet.method

# class Method:
#     def __init__(self, fn):
#         self.fn = fn

#     def __call__(self, *args, **kwargs):
#         import ipdb; ipdb.set_trace(); pass
#         return self.fn(*args, **kwargs)


# double = Method(lambda x: x*2)
# print(double(5))


class FooApplet(Applet):
    def __init__(self, name):
        self.name = name

    @method
    def say(self, message, dry_run=False):
        return '{} says {}'.format(self.name, message), dry_run

    def validator(method, *args, **kwargs):
        return {
            'message': kwargs['message'][:5],
            'dry_run': kwargs.get('dry_run', False)
        }


class SpecTest(unittest.TestCase):
    def test_method_decorator(self):
        applet = FooApplet('x')
        self.assertEqual(
            applet.say('hi'),
            'x says hi'
        )

        self.assertEqual(
            applet.METHODS,
            ['say']
        )

    def test_validator(self):
        applet = FooApplet('y')
        self.assertEqual(
            applet.say(message='1234567890'),
            ('y says 01234', False)
        )

if __name__ == '__main__':
    unittest.main()
