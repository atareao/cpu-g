#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# --BETA--
#################################################################
#    CPU-G version 0.9 beta, Fotis Tsamis, October 2009.        #
#################################################################
#    CPU-G is a program that displays information about your CPU,
#    RAM, Motherboard and some general information about your System.
#    Copyright © 2009  Fotis Tsamis <ftsamis at gmail dot com>.
#
#    This program is free software: you can redistribute it and/or
#    modify it under the terms of the GNU General Public License
#    as published by the Free Software Foundation, either version 3
#    of the License, or any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied
#    warranty of MERCHANTABILITY or FITNESS FOR A
#    PARTICULAR PURPOSE.
#    See the GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public
#    License along with this program.
#    If not, see <http://www.gnu.org/licenses/>.

import os
import re
import sys
import comun
import platform
import subprocess
from gi.repository import Gtk
from gi.repository import GObject
from comun import _


class Investigator():

    def readfile(self, filename):
        try:
            f = open(filename, 'r')
            data = f.read()
            f.close()
            return data
        except Exception as e:
            print(e)
            return 'N/A'

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
                return '64-bit'
            else:
                return '32-bit'

    def sysdevcpu(self, core, level, kind):
        coresinsysdev = str(
            len(re.findall("'cpu[0-9]'",
                           str(os.listdir("/sys/devices/system/cpu/")))))
        if coresinsysdev == self.cpuinfo('coresnum'):
            cores_matching = True
        else:
            # FIXME: Wrong text. (?)
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
        elif index == range(indexes)[-1]:
            return 'N/A'

    def distro(self):
        try:
            values = platform.linux_distribution()
        except AttributeError:
            values = platform.dist()
        if len(values) != 0:
            return "%s %s %s" % (values[0], values[1], values[2])
        else:
            return self.readfile('/etc/issue').strip()

    def gccver(self):
        gcc_version = os.popen('gcc -dumpversion').read().strip()
        if gcc_version != '':
            return gcc_version
        else:
            return 'N/A'

    def xver(self):
        command = subprocess.Popen(
            ['Xorg', '-version'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        stdout, stderr = command.communicate()
        return re.findall("X\.Org X Server (.*)", stderr.decode())[0]

    def raminfo(self):
        data = self.readfile('/proc/meminfo')
        values = {'total': int(re.findall('^MemTotal:\s*([0-9]*)',
                                          data, re.M)[0]) / 1024,
                  'free': int(re.findall('^MemFree:\s*([0-9]*)',
                                         data, re.M)[0]) / 1024,
                  'buffers': int(re.findall('^Buffers:\s*([0-9]*)',
                                            data, re.M)[0]) / 1024,
                  'cached': int(re.findall('^Cached:\s*([0-9]*)',
                                           data, re.M)[0]) / 1024,
                  'used': 0,
                  'active': int(re.findall('^Active:\s*([0-9]*)',
                                           data, re.M)[0]) / 1024,
                  'inactive': int(re.findall('^Inactive:\s*([0-9]*)',
                                             data, re.M)[0]) / 1024,
                  'cached': int(re.findall('^Cached:\s*([0-9]*)',
                                           data, re.M)[0]) / 1024
                  }
        values['free'] = values['free'] + \
            values['buffers'] + values['cached']
        values['used'] = values['total'] - values['free']
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
        card_logo = os.popen("lspci | grep \'VGA\'").read()
        # Intel
        if re.findall("Intel\s*", card_logo):
          label = 'intel.png'
        # ATI
        # ATI Technologies replace to ATI. See bug
        # https://bugs.launchpad.net/cpug/+bug/959115
        elif re.findall("ATI\s*", card_logo):
          label = 'ati.png'
        # nVidia
        elif re.findall("nVidia\s*", card_logo):
          label = 'nvidia.png'
        else:
          label = 'unknown.png'
        return os.path.join(comun.GRAPHICCARDDIR, label)

    # Graphic tab
    def open_gl(self, var):
        open_gl_ = os.popen('glxinfo').read()
        print(open_gl_)
        vga = os.popen("lspci | grep 'VGA' | cut -d ':' -f 3").read()
        print(vga)
        if var == 'vendor':
            if open_gl_ != '':
                return re.findall("OpenGL vendor string: (.*)", open_gl_)[0]
            else:
                return 'N/A'
        elif var == 'renderer':
            if open_gl_ != '':
                return re.findall("OpenGL renderer string: (.*)", open_gl_)[0]
            else:
                return 'N/A'
        elif var == 'version':
            if open_gl_ != '':
                return re.findall("OpenGL version string: (.*)", open_gl_)[0]
            else:
                return 'N/A'
        elif var == 'VGA':
            if vga != '':
                return vga
            else:
                return 'N/A'
    # End Graphic Tab


class CPUG(Gtk.Window):
    """Description"""
    def __init__(self):
        Gtk.Window.__init__(self)
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.set_title(comun.APP)
        self.set_default_size(500, 400)
        self.set_resizable(False)
        self.set_icon_from_file(comun.ICON)
        self.connect('destroy', self.close_application)
        vbox = Gtk.VBox(spacing=5)
        vbox.set_border_width(5)
        self.add(vbox)
        notebook = Gtk.Notebook()
        vbox.add(notebook)
        #
        vbox1 = Gtk.VBox(spacing=5)
        vbox1.set_border_width(5)
        notebook.append_page(vbox1, Gtk.Label.new(_('Processor')))
        frame11 = Gtk.Frame.new(_('General'))
        vbox1.pack_start(frame11, True, True, 0)
        table11 = Gtk.Table(3, 3, False)
        frame11.add(table11)
        label = Gtk.Label(_('Vendor'))
        label.set_alignment(0, 0.5)
        table11.attach(label, 0, 1, 0, 1,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.vendor = Gtk.Entry()
        table11.attach(self.vendor, 1, 2, 0, 1,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        label = Gtk.Label(_('Model'))
        label.set_alignment(0, 0.5)
        table11.attach(label, 0, 1, 1, 2,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.model = Gtk.Entry()
        table11.attach(self.model, 1, 2, 1, 2,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        label = Gtk.Label(_('Core Speed'))
        label.set_alignment(0, 0.5)
        table11.attach(label, 0, 1, 2, 3,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.core_speed = Gtk.Entry()
        table11.attach(self.core_speed, 1, 2, 2, 3,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.processor_image = Gtk.Image()
        table11.attach(self.processor_image, 2, 3, 0, 3,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        frame12 = Gtk.Frame.new(_('CPU'))
        vbox1.pack_start(frame12, True, True, 0)
        table12 = Gtk.Table(3, 6, False)
        frame12.add(table12)
        label = Gtk.Label(_('Family'))
        label.set_alignment(0, 0.5)
        table12.attach(label, 0, 1, 0, 1,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.family = Gtk.Entry()
        self.family.set_width_chars(4)
        table12.attach(self.family, 1, 2, 0, 1,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        label = Gtk.Label(_('Model'))
        label.set_alignment(0, 0.5)
        table12.attach(label, 2, 3, 0, 1,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.cpu_model = Gtk.Entry()
        self.cpu_model.set_width_chars(4)
        table12.attach(self.cpu_model, 3, 4, 0, 1,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        label = Gtk.Label(_('Stepping'))
        label.set_alignment(0, 0.5)
        table12.attach(label, 4, 5, 0, 1,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.stepping = Gtk.Entry()
        self.stepping.set_width_chars(4)
        table12.attach(self.stepping, 5, 6, 0, 1,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        label = Gtk.Label(_('Flags'))
        label.set_alignment(0, 0.5)
        table12.attach(label, 0, 1, 1, 2,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.flags = Gtk.Entry()
        table12.attach(self.flags, 1, 6, 1, 2,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        label = Gtk.Label(_('Bogomips'))
        label.set_alignment(0, 0.5)
        table12.attach(label, 0, 1, 2, 3,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.bogomips = Gtk.Entry()
        table12.attach(self.bogomips, 1, 3, 2, 3,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        label = Gtk.Label(_('Width'))
        label.set_alignment(0, 0.5)
        table12.attach(label, 3, 4, 2, 3,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.width = Gtk.Entry()
        self.width.set_width_chars(4)
        table12.attach(self.width, 4, 6, 2, 3,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)

        frame13 = Gtk.Frame.new(_('Cache'))
        vbox1.pack_start(frame13, True, True, 0)
        table13 = Gtk.Table(4, 2, False)
        frame13.add(table13)
        label = Gtk.Label(_('L1 Data'))
        label.set_alignment(0, 0.5)
        table13.attach(label, 0, 1, 0, 1,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.l1data = Gtk.Entry()
        table13.attach(self.l1data, 1, 2, 0, 1,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        label = Gtk.Label(_('L1 Instruction'))
        label.set_alignment(0, 0.5)
        table13.attach(label, 0, 1, 1, 2,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.l1instruction = Gtk.Entry()
        table13.attach(self.l1instruction, 1, 2, 1, 2,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        label = Gtk.Label(_('Level 2'))
        label.set_alignment(0, 0.5)
        table13.attach(label, 0, 1, 2, 3,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.level2 = Gtk.Entry()
        table13.attach(self.level2, 1, 2, 2, 3,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        label = Gtk.Label(_('Level 3'))
        label.set_alignment(0, 0.5)
        table13.attach(label, 0, 1, 3, 4,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.level3 = Gtk.Entry()
        table13.attach(self.level3, 1, 2, 3, 4,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)

        frame14 = Gtk.Frame.new(_('Core selection'))
        vbox1.pack_start(frame14, True, True, 0)
        table14 = Gtk.Table(1, 3, False)
        frame14.add(table14)
        label = Gtk.Label(_('Number of cores'))
        label.set_alignment(0, 0.5)
        table14.attach(label, 0, 1, 0, 1,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.number_of_cores = Gtk.Entry()
        self.number_of_cores.set_width_chars(4)
        table14.attach(self.number_of_cores, 1, 2, 0, 1,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.core = Gtk.ComboBox()
        cell1 = Gtk.CellRendererText()
        self.core.pack_start(cell1, True)
        self.core.add_attribute(cell1, 'text', 0)
        self.core.connect('changed', self.on_core_changed)
        table14.attach(self.core, 2, 3, 0, 1,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        vbox2 = Gtk.VBox(spacing=5)
        vbox2.set_border_width(5)
        notebook.append_page(vbox2, Gtk.Label.new(_('Motherboard')))
        frame21 = Gtk.Frame.new(_('Board'))
        vbox2.pack_start(frame21, True, True, 0)
        table21 = Gtk.Table(2, 2, False)
        frame21.add(table21)
        label = Gtk.Label(_('Vendor'))
        label.set_alignment(0, 0.5)
        table21.attach(label, 0, 1, 0, 1,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.motherboard_vendor = Gtk.Entry()
        table21.attach(self.motherboard_vendor, 1, 2, 0, 1,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        label = Gtk.Label(_('Model'))
        label.set_alignment(0, 0.5)
        table21.attach(label, 0, 1, 1, 2,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.motherboard_model = Gtk.Entry()
        table21.attach(self.motherboard_model, 1, 2, 1, 2,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        frame22 = Gtk.Frame.new(_('Bios'))
        vbox2.pack_start(frame22, True, True, 0)
        table22 = Gtk.Table(3, 2, False)
        frame22.add(table22)
        label = Gtk.Label(_('Vendor'))
        label.set_alignment(0, 0.5)
        table22.attach(label, 0, 1, 0, 1,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.bios_vendor = Gtk.Entry()
        table22.attach(self.bios_vendor, 1, 2, 0, 1,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        label = Gtk.Label(_('Version'))
        label.set_alignment(0, 0.5)
        table22.attach(label, 0, 1, 1, 2,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.bios_version = Gtk.Entry()
        table22.attach(self.bios_version, 1, 2, 1, 2,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        label = Gtk.Label(_('Date'))
        label.set_alignment(0, 0.5)
        table22.attach(label, 0, 1, 2, 3,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.bios_date = Gtk.Entry()
        table22.attach(self.bios_date, 1, 2, 2, 3,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        vbox3 = Gtk.VBox(spacing=5)
        vbox3.set_border_width(5)
        notebook.append_page(vbox3, Gtk.Label.new(_('RAM')))
        frame31 = Gtk.Frame.new()
        vbox3.pack_start(frame31, True, True, 0)
        table31 = Gtk.Table(8, 2, False)
        frame31.add(table31)
        label = Gtk.Label(_('Total'))
        label.set_alignment(0, 0.5)
        table31.attach(label, 0, 1, 0, 1,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.ram_total = Gtk.Entry()
        table31.attach(self.ram_total, 1, 2, 0, 1,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        label = Gtk.Label(_('Used'))
        label.set_alignment(0, 0.5)
        table31.attach(label, 0, 1, 1, 3,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.ram_used = Gtk.Entry()
        table31.attach(self.ram_used, 1, 2, 1, 2,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.ram_used_progress = Gtk.LevelBar()
        self.ram_used_progress.set_min_value(0)
        self.ram_used_progress.set_max_value(1)
        self.ram_used_progress.set_value(0.5)
        table31.attach(self.ram_used_progress, 1, 2, 2, 3,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        label = Gtk.Label(_('Free'))
        label.set_alignment(0, 0.5)
        table31.attach(label, 0, 1, 3, 5,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.ram_free = Gtk.Entry()
        table31.attach(self.ram_free, 1, 2, 3, 4,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.ram_free_progress = Gtk.LevelBar()
        self.ram_free_progress.set_min_value(0)
        self.ram_free_progress.set_max_value(1)
        self.ram_free_progress.set_value(0.5)
        table31.attach(self.ram_free_progress, 1, 2, 4, 5,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        label = Gtk.Label(_('Active'))
        label.set_alignment(0, 0.5)
        table31.attach(label, 0, 1, 5, 6,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.ram_active = Gtk.Entry()
        table31.attach(self.ram_active, 1, 2, 5, 6,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        label = Gtk.Label(_('Inactive'))
        label.set_alignment(0, 0.5)
        table31.attach(label, 0, 1, 6, 7,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.ram_inactive = Gtk.Entry()
        table31.attach(self.ram_inactive, 1, 2, 6, 7,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        label = Gtk.Label(_('Cached'))
        label.set_alignment(0, 0.5)
        table31.attach(label, 0, 1, 7, 8,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.ram_cached = Gtk.Entry()
        table31.attach(self.ram_cached, 1, 2, 7, 8,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        vbox4 = Gtk.VBox(spacing=5)
        vbox4.set_border_width(5)
        notebook.append_page(vbox4, Gtk.Label.new(_('System')))
        frame41 = Gtk.Frame.new()
        vbox4.pack_start(frame41, True, True, 0)
        table41 = Gtk.Table(7, 2, False)
        frame41.add(table41)
        label = Gtk.Label(_('Hostname'))
        label.set_alignment(0, 0.5)
        table41.attach(label, 0, 1, 0, 1,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.hostname = Gtk.Entry()
        table41.attach(self.hostname, 1, 2, 0, 1,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        label = Gtk.Label(_('Architecture'))
        label.set_alignment(0, 0.5)
        table41.attach(label, 0, 1, 1, 2,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.architecture = Gtk.Entry()
        table41.attach(self.architecture, 1, 2, 1, 2,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        label = Gtk.Label(_('Kernel'))
        label.set_alignment(0, 0.5)
        table41.attach(label, 0, 1, 2, 3,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.kernel = Gtk.Entry()
        table41.attach(self.kernel, 1, 2, 2, 3,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        label = Gtk.Label(_('Distribution'))
        label.set_alignment(0, 0.5)
        table41.attach(label, 0, 1, 3, 4,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.distribution = Gtk.Entry()
        table41.attach(self.distribution, 1, 2, 3, 4,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        label = Gtk.Label(_('GCC Version'))
        label.set_alignment(0, 0.5)
        table41.attach(label, 0, 1, 4, 5,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.gcc_version = Gtk.Entry()
        table41.attach(self.gcc_version, 1, 2, 4, 5,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        label = Gtk.Label(_('Uptime'))
        label.set_alignment(0, 0.5)
        table41.attach(label, 0, 1, 5, 6,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.uptime = Gtk.Entry()
        table41.attach(self.uptime, 1, 2, 5, 6,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        label = Gtk.Label(_('Xorg version'))
        label.set_alignment(0, 0.5)
        table41.attach(label, 0, 1, 6, 7,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.xorg_version = Gtk.Entry()
        table41.attach(self.xorg_version, 1, 2, 6, 7,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        vbox5 = Gtk.VBox(spacing=5)
        vbox5.set_border_width(5)
        notebook.append_page(vbox5, Gtk.Label.new(_('Graphic')))
        frame51 = Gtk.Frame.new()
        vbox5.pack_start(frame51, True, True, 0)
        table51 = Gtk.Table(4, 2, False)
        frame51.add(table51)
        label = Gtk.Label(_('Graphic Controller'))
        label.set_alignment(0, 0.5)
        table51.attach(label, 0, 1, 0, 1,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.graphic_controller = Gtk.Entry()
        table51.attach(self.graphic_controller, 1, 2, 0, 1,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        label = Gtk.Label(_('OpenGL Vendor'))
        label.set_alignment(0, 0.5)
        table51.attach(label, 0, 1, 1, 2,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.opengl_vendor = Gtk.Entry()
        table51.attach(self.opengl_vendor, 1, 2, 1, 2,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        label = Gtk.Label(_('OpenGL renderer'))
        label.set_alignment(0, 0.5)
        table51.attach(label, 0, 1, 2, 3,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.opengl_renderer = Gtk.Entry()
        table51.attach(self.opengl_renderer, 1, 2, 2, 3,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        label = Gtk.Label(_('OpenGL version'))
        label.set_alignment(0, 0.5)
        table51.attach(label, 0, 1, 3, 4,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.opengl_version = Gtk.Entry()
        table51.attach(self.opengl_version, 1, 2, 3, 4,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.graphic_card_logo = Gtk.Image()
        table51.attach(self.graphic_card_logo, 0, 1, 4, 6,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)

        vbox6 = Gtk.VBox(spacing=5)
        vbox6.set_border_width(5)
        notebook.append_page(vbox6, Gtk.Label.new(_('About')))
        frame61 = Gtk.Frame.new()
        vbox6.pack_start(frame61, True, True, 0)
        table61 = Gtk.Table(9, 1, False)
        frame61.add(table61)
        logo = Gtk.Image()
        logo.set_from_file(comun.ICON)
        table61.attach(logo, 0, 1, 0, 1,
                       xoptions=Gtk.AttachOptions.EXPAND,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        label = Gtk.Label()
        label.set_markup('<span color="black" font_desc="Ubuntu 32">%s</span>'
                         % ('<b>CPU-G</b>'))
        table61.attach(label, 0, 1, 1, 2,
                       xoptions=Gtk.AttachOptions.EXPAND,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        label = Gtk.Label()
        label.set_markup('<span font_desc="Ubuntu 18">%s</span>'
                         % (comun.VERSION))
        table61.attach(label, 0, 1, 2, 3,
                       xoptions=Gtk.AttachOptions.EXPAND,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        cpug_description = """
CPU-G is an application that shows useful
information about your CPU, RAM, Motherboard
and some general information about your system
"""
        label = Gtk.Label()
        label.set_markup('<span font_desc="Ubuntu 14">%s</span>'
                         % (cpug_description))
        table61.attach(label, 0, 1, 3, 4,
                       xoptions=Gtk.AttachOptions.EXPAND,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        mcopyright = """
Copyright © 2009-2010 Fotis Tsamis <ftsamis@gmail.com>
Michael Schmöller <schmoemi@users.sourceforge.net>
Copyright © 2012 Michał Głowienka <eloaders@yahoo.com>
Copyright © 2012 Michał Olber
Copyright © 2016 Lorenzo Carbonell
"""
        label = Gtk.Label()
        label.set_markup('<span font_desc="Ubuntu 12">%s</span>'
                         % (mcopyright))
        table61.attach(label, 0, 1, 4, 8,
                       xoptions=Gtk.AttachOptions.EXPAND,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        label = Gtk.LinkButton(uri='http://www.atareao.es')
        label.set_label('http://www.atareao.es')
        table61.attach(label, 0, 1, 8, 9,
                       xoptions=Gtk.AttachOptions.EXPAND,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.update_info()
        self.show_all()

    def uptime_update(self):
        self.uptime.set_text(Investigator().uptime())
        return True

    def ram_update(self):
        values = Investigator().raminfo()
        self.ram_total.set_text(str(redon(values['total'])))
        self.ram_used.set_text(str(redon(values['used'])))
        self.ram_used_progress.set_value(values['used']/values['total'])
        self.ram_free.set_text(str(redon(values['free'])))
        self.ram_free_progress.set_value(values['free']/values['total'])
        self.ram_active.set_text(str(redon(values['active'])))
        self.ram_inactive.set_text(str(redon(values['inactive'])))
        self.ram_cached.set_text(str(redon(values['cached'])))
        return True

    def close_application(self, widget):
        print("Quit")
        sys.exit(0)

    def on_core_changed(self, widget):
        coren = get_selected_value_in_combo(self.core)
        self.update_info_for_core(coren)

    def update_info(self):
        inv = Investigator()
        coresnum = int(inv.cpuinfo('coresnum'))
        model = Gtk.ListStore(int)
        for i in range(0, coresnum):
            model.append([i])
        self.core.set_model(model)
        select_value_in_combo(self.core, 0)
        self.number_of_cores.set_text(str(coresnum))
        self.update_info_for_core(0)
        self.motherboard_vendor.set_text(inv.mobo('board_vendor'))
        self.motherboard_model.set_text(inv.mobo('board_name'))
        self.bios_vendor.set_text(inv.mobo('bios_vendor'))
        self.bios_version.set_text(inv.mobo('bios_version'))
        self.bios_date.set_text(inv.mobo('bios_date'))
        self.ram_update()
        GObject.timeout_add(1000, self.ram_update)
        self.uptime_update()
        GObject.timeout_add(1000 * 60, self.uptime_update)
        self.hostname.set_text(os.uname()[1])
        self.architecture.set_text(os.uname()[4])
        self.kernel.set_text(os.uname()[2])
        self.xorg_version.set_text(inv.xver())
        self.gcc_version.set_text(inv.gccver())
        self.distribution.set_text(inv.distro())
        #
        self.graphic_controller.set_text(inv.open_gl('VGA'))
        self.opengl_vendor.set_text(inv.open_gl('vendor'))
        self.opengl_renderer.set_text(inv.open_gl('renderer'))
        self.opengl_version.set_text(inv.open_gl('version'))
        self.graphic_card_logo.set_from_file(inv.get_graphic_card_logo())

    def update_info_for_core(self, i):
        inv = Investigator()
        self.vendor.set_text(inv.cpuinfo('vendor', i))
        self.model.set_text(inv.cpuinfo('model', i))
        self.core_speed.set_text(inv.cpuinfo('corespeed', i))
        self.family.set_text(inv.cpuinfo('family', i))
        self.cpu_model.set_text(inv.cpuinfo('modelnumber', i))
        self.stepping.set_text(inv.cpuinfo('stepping', i))
        self.flags.set_text(inv.cpuinfo('flags', i))
        self.bogomips.set_text(inv.cpuinfo('bogomips', i))
        self.width.set_text(inv.cpuinfo('width', i))
        self.l1data.set_text(inv.sysdevcpu(i, 1, 'Data'))
        self.l1instruction.set_text(inv.sysdevcpu(i, 1, 'Instruction'))
        self.level2.set_text(inv.sysdevcpu(i, 2, 'Unified'))
        self.level3.set_text(inv.sysdevcpu(i, 3, 'Unified'))
        print(os.path.join(comun.LOGOSDIR,inv.logo(i)))
        self.processor_image.set_from_file(os.path.join(comun.LOGOSDIR,
                                                        inv.logo(i)))


def redon(value):
    return(int(value * 10.0)/10.)


def select_value_in_combo(combo, value):
    model = combo.get_model()
    for i, item in enumerate(model):
        if value == item[0]:
            combo.set_active(i)
            return
    combo.set_active(0)


def get_selected_value_in_combo(combo):
    model = combo.get_model()
    return model.get_value(combo.get_active_iter(), 0)


if __name__ == '__main__':
    import psutil
    print(psutil.cpu_times())
    print(psutil.cpu_count())
    print(psutil.virtual_memory())
    print(psutil.swap_memory())
    print(psutil.disk_partitions())
    print(psutil.disk_usage('/'))
    #exit(0)
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
    cpug = CPUG()
    Gtk.main()
    exit(0)
