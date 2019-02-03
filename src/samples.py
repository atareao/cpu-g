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

import subprocess
import shlex
import re


def execute(command):
    command_with_args = shlex.split(command)
    execution = subprocess.Popen(command_with_args, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
    stdout, stderr = execution.communicate()
    return stdout.decode()

if __name__ == '__main__':
    result = execute('/usr/bin/lspci')
    print(result)
    print(re.findall(result, '.*VGA(.*)', re.M))
    m = re.search('VGA(.*)', result)
    print(len(m.groups()))
    print(m.group(1))
