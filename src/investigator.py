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

import gi
try:
    gi.require_version('Gdk', '3.0')
except Exception as e:
    print(e)
    exit(-1)
from gi.repository import Gdk
import os
import re
import sys
import platform
import subprocess
import shlex
import comun
import psutil
from comun import _

BATTERY_DIR = '/sys/class/power_supply/BAT0'


class Investigator():
    def readfile(self, filename):
        try:
            f = open(filename, 'r')
            data = f.read()
            f.close()
            if data.endswith('\n'):
                data = data[:-1]
            return data
        except Exception as e:
            print(e)
            return _('N/A')

    def get_window_manager(self):
        try:
            ans = self.execute('/usr/bin/wmctrl -m')
            res = ans[6:ans.find('\n')]
        except:
            res = _('N/A')
        return res

    def resolution(self):
        s = Gdk.Screen.get_default()
        return '%dx%d' % (s.get_width(), s.get_height())

    def desktop_environment(self):
        # From http://stackoverflow.com/questions/2035657/\
        # what-is-my-current-desktop-environment
        # and http://ubuntuforums.org/showthread.php?t=652320
        # and http://ubuntuforums.org/showthread.php?t=652320
        # and http://ubuntuforums.org/showthread.php?t=1139057
        if sys.platform in ["win32", "cygwin"]:
            return "windows"
        elif sys.platform == "darwin":
            return "mac"
        else:  # Most likely either a POSIX system or something not much common
            desktop_session = os.environ.get("DESKTOP_SESSION")
            # easier to match if we doesn't have  to deal with caracter cases
            if desktop_session is not None:
                desktop_session = desktop_session.lower()
                if desktop_session in ["gnome", "unity", "cinnamon", "mate",
                                       "xfce4", "lxde", "fluxbox", "blackbox",
                                       "openbox", "icewm", "jwm",
                                       "afterstep", "trinity", "kde",
                                       "lightdm-xsession"]:
                    return desktop_session
                # ## Special cases ##
                # Canonical sets $DESKTOP_SESSION to Lubuntu rather than
                # LXDE if using LXDE.
                # There is no guarantee that they will not do the same with
                # the other desktop environments.
                elif "xfce" in desktop_session or\
                        desktop_session.startswith("xubuntu"):
                    return "xfce4"
                elif desktop_session.startswith("ubuntu"):
                    return "unity"
                elif desktop_session.startswith("lubuntu"):
                    return "lxde"
                elif desktop_session.startswith("kubuntu"):
                    return "kde"
                elif desktop_session.startswith("razor"):  # e.g. razorkwin
                    return "razor-qt"
                elif desktop_session.startswith("wmaker"):  # eg. wmaker-common
                    return "windowmaker"
            if os.environ.get('KDE_FULL_SESSION') == 'true':
                return "kde"
            elif os.environ.get('GNOME_DESKTOP_SESSION_ID'):
                if "deprecated" not in os.environ.get(
                        'GNOME_DESKTOP_SESSION_ID'):
                    return "gnome2"
            # From http://ubuntuforums.org/showthread.php?t=652320
            elif self.is_running("xfce-mcs-manage"):
                return "xfce4"
            elif self.is_running("ksmserver"):
                return "kde"
        return "unknown"

    def convert2int(value):
        try:
            return int(value)
        except Exception as e:
            return value

    def is_running(self, process):
        # From http://www.bloggerpolis.com/2011/05/\
        # how-to-check-if-a-process-is-running-using-python/
        # and http://richarddingwall.name/2009/06/18/\
        # windows-equivalents-of-ps-and-kill-commands/
        try:  # Linux/Unix
            s = subprocess.Popen(["/bin/ps", "axw"], stdout=subprocess.PIPE,
                universal_newlines=True)
        except Exception as e:  # Windows
            print(e)
            return False
        for x in s.stdout:
            if re.search(process, x):
                return True
        return False

    def logo(self, core):
        model = self.cpuinfo("model", core)
        vendor = self.cpuinfo("vendor", core)
        if vendor == 'AMD':
            label = 'amd.png'
        elif vendor == 'Intel':
            label = 'intel.png'
        # AMDs
        if re.match("AMD Athlon\(tm\) 64 X2.*", model)\
                or re.match("AMD Athlon\(tm\) X2.*", model):
            label = 'AMD-AthlonX2.png'
        elif re.match("AMD Sempron\(tm\).*", model):
            label = 'AMD-Sempron.png'
        elif re.match("Mobile AMD Sempron\(tm\).*", model):
            label = 'AMD-Sempron-Mobile.png'
        elif re.match("Dual-Core AMD Opteron\(tm\).*", model)\
                or re.match("AMD Opteron\(tm\).*", model):
            label = 'AMD-Opteron.png'
        elif re.match("AMD Athlon\(tm\) XP.*", model):
            label = 'AMD-AthlonXP.png'
        elif re.match("AMD Athlon\(tm\) 64 Processor.*", model):
            label = 'AMD-Athlon64.png'
        elif re.match("AMD Phenom\(tm\).*", model):
            label = 'AMD-Phenom.png'
        # Intels
        elif re.match("Intel\(R\) Core\(TM\)2 Duo.*", model):
            label = 'Intel-Core2Duo.png'
        elif re.match("Intel\(R\) Core\(TM\)2 Quad.*", model):
            label = 'Intel-Core2Quad.png'
        elif re.match("Intel\(R\) Core\(TM\)2 CPU.*", model):
            label = 'Intel-Core2Quad.png'
        elif re.match("Intel\(R\) Atom\(TM\) CPU.*", model):
            label = 'Intel-Atom.png'
        elif re.match("Intel\(R\) Core\(TM\)2 Extreme CPU.*", model):
            label = 'Intel-Core2Extreme.png'
        elif re.match("Intel\(R\) Xeon\(TM\).*", model):
            label = 'Intel-Xeon.png'
        elif re.match(".*Pentium II.*", model):
            label = 'Intel-Pentium2.png'
        elif re.match("Intel\(R\) Pentium\(R\) Dual CPU.*", model):
            label = 'Intel-PentiumDual.png'
        return label

    def hostname(self):
        ans = self.readfile('/etc/hostname')
        if ans.endswith('\n'):
            ans = ans[:-1]
        return ans

    def battery_info(self, data='manufacturer'):
        info = 0
        if data == 'manufacturer':
            info = self.readfile(os.path.join(BATTERY_DIR, 'manufacturer'))
        elif data == 'model_name':
            info = self.readfile(os.path.join(BATTERY_DIR, 'model_name'))
        elif data == 'serial_number':
            info = self.readfile(os.path.join(BATTERY_DIR, 'serial_number'))
        elif data == 'technology':
            info = self.readfile(os.path.join(BATTERY_DIR, 'technology'))
        elif data == 'status':
            info = self.readfile(os.path.join(BATTERY_DIR, 'status'))
        elif data == 'capacity':
            info = Investigator.convert2int(
                self.readfile(os.path.join(BATTERY_DIR, 'capacity')))
        elif data == 'capacity-level':
            info = self.readfile(os.path.join(BATTERY_DIR, 'capacity_level'))
        elif data == 'voltage-now':
            info = Investigator.convert2int(
                self.readfile(os.path.join(BATTERY_DIR, 'voltage_now')))
        elif data == 'voltage-min-design':
            info = Investigator.convert2int(
                self.readfile(os.path.join(BATTERY_DIR, 'voltage_min_design')))
        elif data == 'charge-now':
            info = Investigator.convert2int(
                self.readfile(os.path.join(BATTERY_DIR, 'charge_now')))
        elif data == 'current-now':
            info = Investigator.convert2int(
                self.readfile(os.path.join(BATTERY_DIR, 'current_now')))
        elif data == 'charge-full':
            info = Investigator.convert2int(
                self.readfile(os.path.join(BATTERY_DIR, 'charge_full')))
        elif data == 'charge-full-design':
            info = Investigator.convert2int(
                self.readfile(os.path.join(BATTERY_DIR, 'charge_full_design')))
        elif data == 'cycle-count':
            info = Investigator.convert2int(
                self.readfile(os.path.join(BATTERY_DIR, 'cycle_count')))
        elif data == 'present':
            info = (self.readfile(os.path.join(BATTERY_DIR,
                                               'present')) == 1)
        elif data == 'exists':
            info = os.path.exists(BATTERY_DIR)
        return info

    def cpuinfo(self, var, core=0):
        info = self.readfile("/proc/cpuinfo")

        if var == 'vendor':
            vendor = re.findall("vendor_id\s*:\s*(.*)", info)
            if vendor[core] == 'AuthenticAMD':
                vendor[core] = 'AMD'
            elif vendor[core] == 'GenuineIntel':
                vendor[core] = 'Intel'
            return vendor[core]
        elif var == 'corespeed':
            return re.findall("cpu MHz\s*:\s*(.*)", info)[core] + ' MHz'
        elif var == 'model':
            return re.findall("model name\s*:\s*(.*)", info)[core]
        elif var == 'cache':
            return re.findall("cache size\s*:\s*(.*)", info)[core]
        elif var == 'modelnumber':
            return re.findall("model\s*:\s*(.*)", info)[core]
        elif var == 'family':
            return re.findall("cpu family\s*:\s*(.*)", info)[core]
        elif var == 'stepping':
            return re.findall("stepping\s*:\s*(.*)", info)[core]
        elif var == 'coresnum':
            return str(len(re.findall("processor\s*:\s*(.*)", info)))
        elif var == 'flags':
            return re.findall("flags\s*:\s*(.*)", info)[core]
        elif var == 'bogomips':
            return re.findall("bogomips\s*:\s*(.*)", info)[core]
        elif var == 'width':
            if re.findall(' lm(?![-a-zA-Z0-9_])',
                          re.findall("flags\s*:(.*)", info)[core]):
                width = '64-bit'
            else:
                width = '32-bit'
            return width

    def sysdevcpu(self, core, level, kind):
        coresinsysdev = str(
            len(re.findall("'cpu[0-9]'",
                           str(os.listdir("/sys/devices/system/cpu/")))))
        if coresinsysdev == self.cpuinfo('coresnum'):
            cores_matching = True
        else:
            print("Error: Cannot decide if the cores are %s or %s.\n" +
                  "Using the lowest value as the real cores number." %
                  (self.cpuinfo('coresnum'), coresinsysdev))
        path = '/sys/devices/system/cpu/cpu%i/cache/' % (core)
        indexes = len(
            re.findall("'index[0-9]*'", str(os.listdir(path))))
        for index in range(indexes):
            levelpath = path + 'index%i/level' % (index)
            typepath = path + 'index%i/type' % (index)
            size = path + 'index%i/size' % (index)
            # os.chdir(newpath)
            if self.readfile(levelpath).strip() == str(level) and\
                    self.readfile(typepath).strip() == kind:
                return self.readfile(size).strip()
        return _('N/A')

    def distro(self):
        try:
            values = platform.linux_distribution()
        except AttributeError:
            values = platform.dist()
        if len(values) == 3:
            return "%s %s %s" % (values[0], values[1], values[2])
        return self.readfile('/etc/issue').strip()

    def get_distro_logo(self):
        distro = self.distro().split()[0].lower() + '.png'
        logo = os.path.join(comun.DISTROSDIR, distro)
        if os.path.exists(logo):
            return logo
        return None

    def gccver(self):
        gcc_version = self.execute('/usr/bin/gcc -dumpversion').strip()
        if gcc_version == '':
            gcc_version = _('N/A')
        return gcc_version

    def xver(self):
        xver_version = self.execute('/usr/bin/apt-cache show xorg')
        ans = re.findall("Version: 1:(.*)\+", xver_version)
        if ans:
            return ans[0]
        return _('N/A')

    def raminfo(self):
        mem = psutil.virtual_memory()
        values = {'total': mem.total/1024/1024,
                  'available': mem.available/1024/1024,
                  'percent': mem.percent,
                  'used': mem.used/1024/1024,
                  'free': mem.free/1024/1024,
                  'active': mem.active/1024/1024,
                  'inactive': mem.inactive/1024/1024,
                  'buffers': mem.buffers/1024/1024,
                  'cached': mem.cached/1024/1024,
                  }
        return values

    def swapinfo(self):
        mem = psutil.swap_memory()
        values = {'total': mem.total/1024/1024,
                  'used': mem.used/1024/1024,
                  'free': mem.free/1024/1024,
                  'sin': mem.sin/1024/1024,
                  'sout': mem.sout/1024/1024,
                  }
        return values

    def disksinfo(self):
        values = []
        disk_partitions = psutil.disk_partitions(all=False)
        for partition in disk_partitions:
            usage = psutil.disk_usage(partition.mountpoint)
            device = {'device': partition.device,
                      'mountpoint': partition.mountpoint,
                      'fstype': partition.fstype,
                      'opts': partition.opts,
                      'total': usage.total,
                      'used': usage.used,
                      'free': usage.free,
                      'percent': usage.percent
                      }
            values.append(device)
        values = sorted(values, key=lambda device: device['device'])
        return values

    def mobo(self, var):
        # var can be: board_vendor, board_name, bios_vendor,
        # bios_version, bios_date, or chassis_type
        return self.readfile('/sys/devices/virtual/dmi/id/' + var).strip()

    def uptime(self):
        total = int(self.readfile('/proc/uptime').split('.')[0])
        days = int(total / 86400)
        hours = int((total / 3600) - (days * 24))
        minutes = int((total / 60) - ((days * 1440) + (hours * 60)))
        return "%i days, %i hours, %i minutes" % (days, hours, minutes)

    def get_graphic_card_logo(self):
        card_logo = self.execute('/usr/bin/lspci', 'VGA(.*)')
        if card_logo is not None:
            # Intel
            if re.findall("Intel\s*", card_logo):
                label = 'intel.png'
            # ATI
            # ATI Technologies replace to ATI. See bug
            # https://bugs.launchpad.net/cpug/+bug/959115
            elif re.findall("ATI\s*", card_logo):
                label = 'ati.png'
            # nVidia
            # elif re.findall("nVidia\s*", card_logo):
            elif re.findall("nVidia\s*", card_logo, re.I):
                label = 'nvidia.png'
            else:
                label = 'unknown.png'
        else:
            label = 'unknown.png'
        return os.path.join(comun.GRAPHICCARDDIR, label)

    # Graphic tab
    def open_gl(self, var):
        open_gl_ = self.execute('/usr/bin/glxinfo')
        vga = self.execute('/usr/bin/lspci', 'VGA[^:]*:(.*)')
        if var == 'vendor':
            if open_gl_ != '':
                return re.findall("OpenGL vendor string: (.*)", open_gl_)[0]
            return _('N/A')
        elif var == 'renderer':
            if open_gl_ != '':
                return re.findall("OpenGL renderer string: (.*)", open_gl_)[0]
            return _('N/A')
        elif var == 'version':
            if open_gl_ != '':
                return re.findall("OpenGL version string: (.*)", open_gl_)[0]
            return _('N/A')
        elif var == 'VGA':
            if vga is not None:
                return vga
            return _('N/A')
    # End Graphic Tab

    def execute(self, command, parser=None):
        command_with_args = shlex.split(command)
        execution = subprocess.Popen(command_with_args, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
        stdout, stderr = execution.communicate()
        if parser is None:
            result = stdout.decode()
        else:
            matches = re.search(parser, stdout.decode())
            if matches.groups():
                result = matches.group(1)
            else:
                result = None
        return result

if __name__ == '__main__':
    print(psutil.cpu_times())
    print(psutil.cpu_count())
    print(psutil.virtual_memory())
    print(psutil.swap_memory())
    print(psutil.disk_partitions())
    print(psutil.disk_usage('/'))
    # exit(0)
    inv = Investigator()
    print(inv.cpuinfo)
    # board_vendor, board_name, bios_vendor, bios_version, bios_date,\
    # chassis_type
    print(inv.cpuinfo('coresnum'))
    for i in range(0, int(inv.cpuinfo('coresnum'))):
        print(inv.cpuinfo('vendor', i))
        print(inv.cpuinfo('corespeed', i))
        print(inv.cpuinfo('model', i))
        print(inv.cpuinfo('cache', i))
        print(inv.cpuinfo('modelnumber', i))
        print(inv.cpuinfo('family', i))
        print(inv.cpuinfo('stepping', i))
        print(inv.cpuinfo('flags', i))
        print(inv.cpuinfo('bogomips', i))
        print(inv.cpuinfo('width', i))
        print(inv.logo(i))
        print(inv.sysdevcpu(i, 1, 'Data'))
        print(inv.sysdevcpu(i, 1, 'Instruction'))
        print(inv.sysdevcpu(i, 2, 'Unified'))
        print(inv.sysdevcpu(i, 3, 'Unified'))
    print(inv.mobo('board_vendor'))
    print(inv.mobo('board_name'))
    print(inv.mobo('bios_vendor'))
    print(inv.mobo('bios_version'))
    print(inv.mobo('chassis_type'))
    print(inv.raminfo())
    print(inv.distro())
    print(inv.xver())
    print(inv.gccver())
    print(inv.disksinfo())
    print(inv.get_window_manager())

    exit(0)
