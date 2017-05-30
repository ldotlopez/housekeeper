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


import dbus


class HKDbusInterface:
    def __new__(cls, name, path, iface, bus='session'):
        if bus == 'session':
            bus = dbus.SessionBus()
        elif bus == 'system':
            bus = dbus.SystemBus()
        else:
            raise ValueError(bus)

        proxy = bus.get_object(name, path)
        iface = dbus.Interface(proxy, iface)

        setattr(iface,
                'Properties',
                HKDBusPropertiesProxy(iface))

        return iface


class HKDBusPropertiesProxy:
    def __init__(self, iface):
        self.iface_name = iface.dbus_interface
        self.props = dbus.Interface(iface.proxy_object, 'org.freedesktop.DBus.Properties')

    def Set(self, *args, **kwargs):
        return self.props.Set(self.iface_name, *args, **kwargs)

    def Get(self, *args, **kwargs):
        return dbus2py(self.props.Get(self.iface_name, *args, **kwargs))

    def GetAll(self, *args, **kwargs):
        return dbus2py(self.props.GetAll(self.iface_name, *args, **kwargs))


def dbus2py(x):
    if isinstance(x, dbus.Dictionary):
        return {dbus2py(k): dbus2py(v) for (k, v) in x.items()}

    elif isinstance(x, dbus.Array):
        return [dbus2py(e) for e in x]

    elif isinstance(x, (dbus.Int16, dbus.Int32, dbus.Int64,
                        dbus.UInt16, dbus.UInt32, dbus.UInt64)):
        return int(x)

    elif isinstance(x, (dbus.Double,)):
        return float(x)

    elif isinstance(x, (dbus.String, dbus.ObjectPath)):
        return str(x)

    elif isinstance(x, dbus.Boolean):
        return bool(x)

    raise ValueError(x)
