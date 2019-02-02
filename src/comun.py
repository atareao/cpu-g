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

import os
import sys
import locale
import gettext


def is_package():
    return __file__.find('src') < 0

######################################


APP = 'cpu-g'
APPNAME = 'CPU-G'

# check if running from source
if is_package():
    ROOTDIR = '/opt/extras.ubuntu.com/cpu-g/share'
    LANGDIR = os.path.join(ROOTDIR, 'locale-langpack')
    APPDIR = os.path.join(ROOTDIR, APP)
    CHANGELOG = os.path.join(APPDIR, 'changelog')
    ICONDIR = os.path.join(ROOTDIR, 'icons')
    ICON = os.path.join(ICONDIR, 'cpu-g.png')
    LOGOSDIR = os.path.join(APPDIR, 'logos')
    DISTROSDIR = os.path.join(APPDIR, 'distros')
    GRAPHICCARDDIR = os.path.join(APPDIR, 'graphic_card')
    BATTERY_MONITOR = os.path.join(ROOTDIR, 'monitor_battery.py')
else:
    ROOTDIR = os.path.dirname(__file__)
    LANGDIR = os.path.normpath(os.path.join(ROOTDIR, '../template1'))
    APPDIR = ROOTDIR
    DEBIANDIR = os.path.normpath(os.path.join(ROOTDIR, '../debian'))
    CHANGELOG = os.path.join(DEBIANDIR, 'changelog')
    ICON = os.path.normpath(os.path.join(ROOTDIR, '../data/icons/cpu-g.png'))
    LOGOSDIR = os.path.normpath(os.path.join(ROOTDIR, '../data/logos'))
    DISTROSDIR = os.path.normpath(os.path.join(ROOTDIR, '../data/distros'))
    GRAPHICCARDDIR = os.path.normpath(os.path.join(ROOTDIR,
                                                   '../data/graphic_card'))
    BATTERY_MONITOR = os.path.join(ROOTDIR, 'monitor_battery.py')

f = open(CHANGELOG, 'r')
line = f.readline()
f.close()
pos = line.find('(')
posf = line.find(')', pos)
VERSION = line[pos + 1:posf].strip()
if not is_package():
    VERSION = VERSION + '-src'

####
try:
    current_locale, encoding = locale.getdefaultlocale()
    language = gettext.translation(APP, LANGDIR, [current_locale])
    language.install()
    print(language)
    if sys.version_info[0] == 3:
        _ = language.gettext
    else:
        _ = language.ugettext
except Exception as e:
    print(e)
    _ = str
APPNAME = _(APPNAME)
