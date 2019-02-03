#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# CPU-G is a program that displays information about your CPU,
# RAM, Motherboard and some general information about your System.
#
# Copyright © 2009  Fotis Tsamis <ftsamis at gmail dot com>.
# Copyright © 2016-2019  Lorenzo Carbonell (aka atareao)
# <lorenzo.carbonell.cerezo at gmail dot com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import dbus
from collections import namedtuple
from functools import partial
from comun import _

def convert(dbus_obj):
    """Converts dbus_obj from dbus type to python type.
    :param dbus_obj: dbus object.
    :returns: dbus_obj in python type.
    """
    _isinstance = partial(isinstance, dbus_obj)
    ConvertType = namedtuple('ConvertType', 'pytype dbustypes')

    pyint = ConvertType(int, (dbus.Byte, dbus.Int16, dbus.Int32, dbus.Int64,
                              dbus.UInt16, dbus.UInt32, dbus.UInt64))
    pybool = ConvertType(bool, (dbus.Boolean, ))
    pyfloat = ConvertType(float, (dbus.Double, ))
    pylist = ConvertType(lambda _obj: list(map(convert, dbus_obj)),
                         (dbus.Array, ))
    pytuple = ConvertType(lambda _obj: tuple(map(convert, dbus_obj)),
                          (dbus.Struct, ))
    types_str = (dbus.ObjectPath, dbus.Signature, dbus.String)
    pystr = ConvertType(str, types_str)

    pydict = ConvertType(
        lambda _obj: dict(zip(map(convert, dbus_obj.keys()),
                              map(convert, dbus_obj.values())
                              )
                          ),
        (dbus.Dictionary, )
    )

    for conv in (pyint, pybool, pyfloat, pylist, pytuple, pystr, pydict):
        if any(map(_isinstance, conv.dbustypes)):
            return conv.pytype(dbus_obj)
        return dbus_obj


class BatteryDriver():
    def __init__(self):
        bus = dbus.SystemBus()
        bat0_object = bus.get_object(
            'org.freedesktop.UPower',
            '/org/freedesktop/UPower/devices/battery_BAT0')
        self.__statistics = bat0_object.get_dbus_method(
            'GetStatistics',
            'org.freedesktop.UPower.Device')
        self.__history = bat0_object.get_dbus_method(
            'GetHistory',
            'org.freedesktop.UPower.Device')
        self.bat0 = dbus.Interface(bat0_object,
                                   'org.freedesktop.DBus.Properties')

    def __get(self, parameter):
        return self.bat0.Get('org.freedesktop.UPower.Device', parameter)

    def get_native_path(self):
        return self.__get('NativePath')

    def get_vendor(self):
        return self.__get('Vendor')

    def get_model(self):
        return self.__get('Model')

    def get_serial(self):
        return self.__get('Serial')

    def get_update_time(self):
        return self.__get('UpdateTime')

    def get_type(self):
        ans = self.__get('Type')
        if ans == 0:
            return _('Unknown')
        elif ans == 1:
            return _('Line Power')
        elif ans == 2:
            return _('Battery')
        elif ans == 3:
            return _('Ups')
        elif ans == 4:
            return _('Monitor')
        elif ans == 5:
            return _('Mouse')
        elif ans == 6:
            return _('Keyboard')
        elif ans == 7:
            return _('Pda')
        elif ans == 8:
            return _('Phone')
        return _('Unknown')

    def get_power_supply(self):
        return convert(self.__get('PowerSupply'))

    def get_has_history(self):
        return convert(self.__get('HasHistory'))

    def get_online(self):
        return convert(self.__get('Online'))

    def get_energy(self):
        return convert(self.__get('Energy'))  # Wh

    def get_energy_empty(self):
        return self.__get('EnergyEmpty')

    def get_energy_full(self):
        return self.__get('EnergyFull')

    def get_energy_full_design(self):
        return self.__get('EnergyFullDesign')

    def get_energy_rate(self):
        return self.__get('EnergyRate')

    def get_voltage(self):  # v
        return self.__get('Voltage')

    def get_time_to_empty(self):  # s
        return self.__get('TimeToEmpty')

    def get_time_to_full(self):  # s
        return self.__get('TimeToFull')

    def get_percentage(self):
        return self.__get('Percentage')

    def get_is_present(self):
        return convert(self.__get('IsPresent'))

    def get_state(self):
        ans = self.__get('State')
        if ans == 0:
            return _('Unknown')
        elif ans == 1:
            return _('Charging')
        elif ans == 2:
            return _('Discharging')
        elif ans == 3:
            return _('Empty')
        elif ans == 4:
            return _('Fully charged')
        elif ans == 5:
            return _('Pending charge')
        elif ans == 6:
            return _('Pending discharge')
        return _('Unknown')

    def get_capacity(self):  # < 75% renew battery
        return self.__get('Capacity')

    def get_technology(self):
        ans = self.__get('Technology')
        if ans == 0:
            return _('Unknown')
        elif ans == 1:
            return _('Lithium ion')
        elif ans == 2:
            return _('Lithium polymer')
        elif ans == 3:
            return _('Lithium iron phosphate')
        elif ans == 4:
            return _('Lead acid')
        elif ans == 5:
            return _('Nickel cadmium')
        elif ans == 6:
            return _('Nickel metal hydride')
        return _('Unknown')

    def get_statistics_discharging(self):
        return convert(self.__statistics('discharging'))

    def get_statistics_charging(self):
        return convert(self.__statistics('charging'))

    def get_history_rate(self, ndata=1000):
        '''
        time: The time value in seconds from the gettimeofday() method.
        value: the rate in W.
        state: The state of the device, for instance charging or discharging.
        '''
        return convert(self.__history('rate', 0, ndata))

    def get_history_charge(self, ndata=1000):
        '''
        time: The time value in seconds from the gettimeofday() method.
        value: the charge in %.
        state: The state of the device, for instance charging or discharging.
        '''
        return convert(self.__history('charge', 0, ndata))


if __name__ == '__main__':
    bd = BatteryDriver()
    print(bd.get_native_path())
    print(bd.get_vendor())
    print(bd.get_model())
    print(bd.get_serial())
    print(bd.get_update_time())
    print(bd.get_type())
    print(bd.get_power_supply())
    print(bd.get_has_history())
    print(bd.get_online())
    print(bd.get_energy())
    print(bd.get_energy_empty())
    print(bd.get_energy_full())
    print(bd.get_energy_full_design())
    print(bd.get_energy_rate())
    print(bd.get_voltage())
    print(bd.get_time_to_empty())
    print(bd.get_time_to_full())
    print(bd.get_percentage())
    print(bd.get_is_present())
    print(bd.get_state())
    print(bd.get_capacity())
    print(bd.get_technology())
    print(bd.get_statistics_discharging())
    print(bd.get_statistics_charging())
    print(bd.get_history_rate())
    print(bd.get_history_charge())
