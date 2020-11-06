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
    gi.require_version('GLib', '2.0')
    gi.require_version('Gtk', '3.0')
except Exception as e:
    print(e)
    exit(-1)
from gi.repository import Gtk
from gi.repository import GObject
from gi.repository import GLib
import os
import locale
import comun
import time
import datetime
import sys
from matplotlib.figure import Figure
from matplotlib.backends.backend_gtk3cairo import FigureCanvasGTK3Cairo as\
    FigureCanvas
import matplotlib.ticker as ticker
from investigator import Investigator
from upower import BatteryDriver
from comun import _

locale.setlocale(locale.LC_ALL, '')


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
        vbox3 = Gtk.HBox(spacing=5)
        vbox3.set_border_width(5)
        notebook.append_page(vbox3, Gtk.Label.new(_('Memory')))
        frame31 = Gtk.Frame.new(_('Ram'))
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
        self.ram_total.set_tooltip_text(_('Total physical memory available.'))
        table31.attach(self.ram_total, 1, 2, 0, 1,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        label = Gtk.Label(_('Available'))
        label.set_alignment(0, 0.5)
        table31.attach(label, 0, 1, 1, 3,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.ram_available = Gtk.Entry()
        self.ram_available.set_tooltip_text(_('The actual amount of available\
 memory that can be given instantly to processes that request more memory in\
 bytes; this is calculated by summing different memory values (Mb)'))
        table31.attach(self.ram_available, 1, 2, 1, 2,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.ram_available_progress = Gtk.LevelBar()
        self.ram_available_progress.set_min_value(0)
        self.ram_available_progress.set_max_value(1)
        self.ram_available_progress.set_value(0.5)
        table31.attach(self.ram_available_progress, 1, 2, 2, 3,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        label = Gtk.Label(_('Used'))
        label.set_alignment(0, 0.5)
        table31.attach(label, 0, 1, 3, 5,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.ram_used = Gtk.Entry()
        self.ram_used.set_tooltip_text(_('Memory used, calculated differently\
 depending on the platform and designed for informational purposes only (Mb)'))
        table31.attach(self.ram_used, 1, 2, 3, 4,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.ram_used_progress = Gtk.LevelBar()
        self.ram_used_progress.set_min_value(0)
        self.ram_used_progress.set_max_value(1)
        self.ram_used_progress.set_value(0.5)
        table31.attach(self.ram_used_progress, 1, 2, 4, 5,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        label = Gtk.Label(_('Free'))
        label.set_alignment(0, 0.5)
        table31.attach(label, 0, 1, 5, 7,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.ram_free = Gtk.Entry()
        self.ram_free.set_tooltip_text(_('Memory not being used at all\
 (zeroed) that is readily available (Mb)'))
        table31.attach(self.ram_free, 1, 2, 5, 6,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.ram_free_progress = Gtk.LevelBar()
        self.ram_free_progress.set_min_value(0)
        self.ram_free_progress.set_max_value(1)
        self.ram_free_progress.set_value(0.5)
        table31.attach(self.ram_free_progress, 1, 2, 6, 7,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        label = Gtk.Label(_('Active'))
        label.set_alignment(0, 0.5)
        table31.attach(label, 0, 1, 7, 8,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.ram_active = Gtk.Entry()
        self.ram_active.set_tooltip_text(_('Memory currently in use or very\
 recently used, and so it is in RAM (Mb)'))
        table31.attach(self.ram_active, 1, 2, 7, 8,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        label = Gtk.Label(_('Inactive'))
        label.set_alignment(0, 0.5)
        table31.attach(label, 0, 1, 8, 9,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.ram_inactive = Gtk.Entry()
        self.ram_inactive.set_tooltip_text(_('Memory that is marked as not\
 used.'))
        table31.attach(self.ram_inactive, 1, 2, 8, 9,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        label = Gtk.Label(_('Buffers'))
        label.set_alignment(0, 0.5)
        table31.attach(label, 0, 1, 9, 10,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.ram_buffers = Gtk.Entry()
        self.ram_buffers.set_tooltip_text(_('Ccache for things like file\
 system metadata. (Mb)'))
        table31.attach(self.ram_buffers, 1, 2, 9, 10,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        label = Gtk.Label(_('Cached'))
        label.set_alignment(0, 0.5)
        table31.attach(label, 0, 1, 10, 11,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.ram_cached = Gtk.Entry()
        self.ram_cached.set_tooltip_text(_('Cache for various things (Mb)'))
        table31.attach(self.ram_cached, 1, 2, 10, 11,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        frame32 = Gtk.Frame.new(_('Swap'))
        vbox3.pack_start(frame32, True, True, 0)
        table32 = Gtk.Table(8, 2, False)
        frame32.add(table32)
        label = Gtk.Label(_('Total'))
        label.set_alignment(0, 0.5)
        table32.attach(label, 0, 1, 0, 1,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.swap_total = Gtk.Entry()
        self.swap_total.set_tooltip_text(_('Total physical memory available in\
 Mb.'))
        table32.attach(self.swap_total, 1, 2, 0, 1,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        label = Gtk.Label(_('Used'))
        label.set_alignment(0, 0.5)
        table32.attach(label, 0, 1, 1, 3,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.swap_used = Gtk.Entry()
        self.swap_used.set_tooltip_text(_('Used swap memory in Mb'))
        table32.attach(self.swap_used, 1, 2, 1, 2,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.swap_used_progress = Gtk.LevelBar()
        self.swap_used_progress.set_min_value(0)
        self.swap_used_progress.set_max_value(1)
        self.swap_used_progress.set_value(0.5)
        table32.attach(self.swap_used_progress, 1, 2, 2, 3,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        label = Gtk.Label(_('Free'))
        label.set_alignment(0, 0.5)
        table32.attach(label, 0, 1, 3, 5,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.swap_free = Gtk.Entry()
        self.swap_free.set_tooltip_text(_('Free swap memory in Mb'))
        table32.attach(self.swap_free, 1, 2, 3, 4,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.swap_free_progress = Gtk.LevelBar()
        self.swap_free_progress.set_min_value(0)
        self.swap_free_progress.set_max_value(1)
        self.swap_free_progress.set_value(0.5)
        table32.attach(self.swap_free_progress, 1, 2, 4, 5,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        label = Gtk.Label(_('Sin'))
        label.set_alignment(0, 0.5)
        table32.attach(label, 0, 1, 5, 6,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.swap_sin = Gtk.Entry()
        self.swap_sin.set_tooltip_text(_('The number of Mb the system has\
 swapped in from disk (cumulative)'))
        table32.attach(self.swap_sin, 1, 2, 5, 6,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        label = Gtk.Label(_('Sout'))
        label.set_alignment(0, 0.5)
        table32.attach(label, 0, 1, 6, 7,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.swap_sout = Gtk.Entry()
        self.swap_sout.set_tooltip_text(_('The number of Mb the system has\
 swapped out from disk (cumulative)'))
        table32.attach(self.swap_sout, 1, 2, 6, 7,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)

        vbox4 = Gtk.VBox(spacing=5)
        vbox4.set_border_width(5)
        notebook.append_page(vbox4, Gtk.Label.new(_('System')))
        frame41 = Gtk.Frame.new()
        vbox4.pack_start(frame41, True, True, 0)
        table41 = Gtk.Table(7, 3, False)
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
        label = Gtk.Label(_('GCC Version'))
        label.set_alignment(0, 0.5)
        table41.attach(label, 0, 1, 3, 4,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.gcc_version = Gtk.Entry()
        table41.attach(self.gcc_version, 1, 2, 3, 4,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        label = Gtk.Label(_('Uptime'))
        label.set_alignment(0, 0.5)
        table41.attach(label, 0, 1, 4, 5,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.uptime = Gtk.Entry()
        table41.attach(self.uptime, 1, 2, 4, 5,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        label = Gtk.Label(_('Xorg Server version'))
        label.set_alignment(0, 0.5)
        table41.attach(label, 0, 1, 5, 6,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.xorg_server_version = Gtk.Entry()
        table41.attach(self.xorg_server_version, 1, 2, 5, 6,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        label = Gtk.Label(_('Resolution'))
        label.set_alignment(0, 0.5)
        table41.attach(label, 0, 1, 6, 7,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.screen_resolution = Gtk.Entry()
        self.screen_resolution.set_width_chars(50)
        table41.attach(self.screen_resolution, 1, 2, 6, 7,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        label = Gtk.Label(_('Distribution'))
        label.set_alignment(0, 0.5)
        table41.attach(label, 0, 1, 7, 8,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.distribution = Gtk.Entry()
        table41.attach(self.distribution, 1, 2, 7, 8,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        label = Gtk.Label(_('Desktop environment'))
        label.set_alignment(0, 0.5)
        table41.attach(label, 0, 1, 8, 9,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.desktop_environment = Gtk.Entry()
        self.desktop_environment.set_width_chars(50)
        table41.attach(self.desktop_environment, 1, 2, 8, 9,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        label = Gtk.Label(_('Window manager'))
        label.set_alignment(0, 0.5)
        table41.attach(label, 0, 1, 9, 10,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.window_manager = Gtk.Entry()
        self.window_manager.set_width_chars(50)
        table41.attach(self.window_manager, 1, 2, 9, 10,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.distro_logo = Gtk.Image()
        table41.attach(self.distro_logo, 2, 3, 0, 10,
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
        self.battery_index = notebook.append_page(
            vbox6, Gtk.Label.new(_('Battery')))

        frame611 = Gtk.Frame.new()
        vbox6.pack_start(frame611, True, True, 0)
        table611 = Gtk.Table(8, 4, False)
        frame611.add(table611)
        label = Gtk.Label(_('Manufacturer'))
        label.set_alignment(0, 0.5)
        table611.attach(label, 0, 1, 0, 1,
                        xoptions=Gtk.AttachOptions.FILL,
                        yoptions=Gtk.AttachOptions.FILL,
                        xpadding=5, ypadding=5)
        self.battery_manufacturer = Gtk.Entry()
        self.battery_manufacturer.set_width_chars(30)
        table611.attach(self.battery_manufacturer, 1, 2, 0, 1,
                        xoptions=Gtk.AttachOptions.FILL,
                        yoptions=Gtk.AttachOptions.FILL,
                        xpadding=5, ypadding=5)
        label = Gtk.Label(_('Model name'))
        label.set_alignment(0, 0.5)
        table611.attach(label, 0, 1, 1, 2,
                        xoptions=Gtk.AttachOptions.FILL,
                        yoptions=Gtk.AttachOptions.FILL,
                        xpadding=5, ypadding=5)
        self.battery_model_name = Gtk.Entry()
        self.battery_model_name.set_width_chars(30)
        table611.attach(self.battery_model_name, 1, 2, 1, 2,
                        xoptions=Gtk.AttachOptions.FILL,
                        yoptions=Gtk.AttachOptions.FILL,
                        xpadding=5, ypadding=5)
        label = Gtk.Label(_('Serial number'))
        label.set_alignment(0, 0.5)
        table611.attach(label, 0, 1, 2, 3,
                        xoptions=Gtk.AttachOptions.FILL,
                        yoptions=Gtk.AttachOptions.FILL,
                        xpadding=5, ypadding=5)
        self.battery_serial_number = Gtk.Entry()
        self.battery_serial_number.set_width_chars(30)
        table611.attach(self.battery_serial_number, 1, 2, 2, 3,
                        xoptions=Gtk.AttachOptions.FILL,
                        yoptions=Gtk.AttachOptions.FILL,
                        xpadding=5, ypadding=5)
        label = Gtk.Label(_('Technology'))
        label.set_alignment(0, 0.5)
        table611.attach(label, 0, 1, 3, 4,
                        xoptions=Gtk.AttachOptions.FILL,
                        yoptions=Gtk.AttachOptions.FILL,
                        xpadding=5, ypadding=5)
        self.battery_technology = Gtk.Entry()
        self.battery_technology.set_width_chars(30)
        table611.attach(self.battery_technology, 1, 2, 3, 4,
                        xoptions=Gtk.AttachOptions.FILL,
                        yoptions=Gtk.AttachOptions.FILL,
                        xpadding=5, ypadding=5)
        label = Gtk.Label(_('Estimated time remaining'))
        label.set_alignment(0, 0.5)
        table611.attach(label, 0, 1, 4, 5,
                        xoptions=Gtk.AttachOptions.FILL,
                        yoptions=Gtk.AttachOptions.FILL,
                        xpadding=5, ypadding=5)
        self.battery_estimated_duration = Gtk.Entry()
        self.battery_estimated_duration.set_width_chars(30)
        table611.attach(self.battery_estimated_duration, 1, 2, 4, 5,
                        xoptions=Gtk.AttachOptions.FILL,
                        yoptions=Gtk.AttachOptions.FILL,
                        xpadding=5, ypadding=5)
        label = Gtk.Label(_('Estimated battery discharge time'))
        label.set_alignment(0, 0.5)
        table611.attach(label, 0, 1, 5, 6,
                        xoptions=Gtk.AttachOptions.FILL,
                        yoptions=Gtk.AttachOptions.FILL,
                        xpadding=5, ypadding=5)
        self.battery_data2 = Gtk.Entry()
        self.battery_data2.set_width_chars(30)
        table611.attach(self.battery_data2, 1, 2, 5, 6,
                        xoptions=Gtk.AttachOptions.FILL,
                        yoptions=Gtk.AttachOptions.FILL,
                        xpadding=5, ypadding=5)
        label = Gtk.Label(_('Battery level'))
        label.set_alignment(0, 0.5)
        table611.attach(label, 0, 1, 6, 8,
                        xoptions=Gtk.AttachOptions.FILL,
                        yoptions=Gtk.AttachOptions.FILL,
                        xpadding=5, ypadding=5)
        self.battery_level_value = Gtk.Entry()
        self.battery_level_value.set_width_chars(30)
        table611.attach(self.battery_level_value, 1, 2, 6, 7,
                        xoptions=Gtk.AttachOptions.FILL,
                        yoptions=Gtk.AttachOptions.FILL,
                        xpadding=5, ypadding=5)
        self.battery_level = Gtk.LevelBar()
        self.battery_level.set_min_value(0)
        self.battery_level.set_max_value(100)
        self.battery_level.set_value(30)
        table611.attach(self.battery_level, 1, 2, 7, 8,
                        xoptions=Gtk.AttachOptions.FILL,
                        yoptions=Gtk.AttachOptions.FILL,
                        xpadding=5, ypadding=5)
        label = Gtk.Label(_('Capacity level'))
        label.set_alignment(0, 0.5)
        table611.attach(label, 2, 3, 0, 1,
                        xoptions=Gtk.AttachOptions.FILL,
                        yoptions=Gtk.AttachOptions.FILL,
                        xpadding=5, ypadding=5)
        self.battery_capacity_level = Gtk.Entry()
        self.battery_capacity_level.set_width_chars(30)
        table611.attach(self.battery_capacity_level, 3, 4, 0, 1,
                        xoptions=Gtk.AttachOptions.FILL,
                        yoptions=Gtk.AttachOptions.FILL,
                        xpadding=5, ypadding=5)
        label = Gtk.Label(_('Voltage now'))
        label.set_alignment(0, 0.5)
        table611.attach(label, 2, 3, 1, 2,
                        xoptions=Gtk.AttachOptions.FILL,
                        yoptions=Gtk.AttachOptions.FILL,
                        xpadding=5, ypadding=5)
        self.battery_voltage_now = Gtk.Entry()
        self.battery_voltage_now.set_width_chars(30)
        table611.attach(self.battery_voltage_now, 3, 4, 1, 2,
                        xoptions=Gtk.AttachOptions.FILL,
                        yoptions=Gtk.AttachOptions.FILL,
                        xpadding=5, ypadding=5)
        label = Gtk.Label(_('Minimum voltage design'))
        label.set_alignment(0, 0.5)
        table611.attach(label, 2, 3, 2, 3,
                        xoptions=Gtk.AttachOptions.FILL,
                        yoptions=Gtk.AttachOptions.FILL,
                        xpadding=5, ypadding=5)
        self.battery_min_voltage_design = Gtk.Entry()
        self.battery_min_voltage_design.set_width_chars(30)
        table611.attach(self.battery_min_voltage_design, 3, 4, 2, 3,
                        xoptions=Gtk.AttachOptions.FILL,
                        yoptions=Gtk.AttachOptions.FILL,
                        xpadding=5, ypadding=5)
        label = Gtk.Label(_('Charge now'))
        label.set_alignment(0, 0.5)
        table611.attach(label, 2, 3, 3, 4,
                        xoptions=Gtk.AttachOptions.FILL,
                        yoptions=Gtk.AttachOptions.FILL,
                        xpadding=5, ypadding=5)
        self.battery_charge_now = Gtk.Entry()
        self.battery_charge_now.set_width_chars(30)
        table611.attach(self.battery_charge_now, 3, 4, 3, 4,
                        xoptions=Gtk.AttachOptions.FILL,
                        yoptions=Gtk.AttachOptions.FILL,
                        xpadding=5, ypadding=5)
        label = Gtk.Label(_('Charge full'))
        label.set_alignment(0, 0.5)
        table611.attach(label, 2, 3, 4, 5,
                        xoptions=Gtk.AttachOptions.FILL,
                        yoptions=Gtk.AttachOptions.FILL,
                        xpadding=5, ypadding=5)
        self.battery_charge_full = Gtk.Entry()
        self.battery_charge_full.set_width_chars(30)
        table611.attach(self.battery_charge_full, 3, 4, 4, 5,
                        xoptions=Gtk.AttachOptions.FILL,
                        yoptions=Gtk.AttachOptions.FILL,
                        xpadding=5, ypadding=5)
        label = Gtk.Label(_('Charge full design'))
        label.set_alignment(0, 0.5)
        table611.attach(label, 2, 3, 5, 6,
                        xoptions=Gtk.AttachOptions.FILL,
                        yoptions=Gtk.AttachOptions.FILL,
                        xpadding=5, ypadding=5)
        self.battery_charge_full_design = Gtk.Entry()
        self.battery_charge_full.set_width_chars(30)
        table611.attach(self.battery_charge_full_design, 3, 4, 5, 6,
                        xoptions=Gtk.AttachOptions.FILL,
                        yoptions=Gtk.AttachOptions.FILL,
                        xpadding=5, ypadding=5)
        label = Gtk.Label(_('Current now'))
        label.set_alignment(0, 0.5)
        table611.attach(label, 2, 3, 6, 7,
                        xoptions=Gtk.AttachOptions.FILL,
                        yoptions=Gtk.AttachOptions.FILL,
                        xpadding=5, ypadding=5)
        self.battery_current_now = Gtk.Entry()
        self.battery_current_now.set_width_chars(30)
        table611.attach(self.battery_current_now, 3, 4, 6, 7,
                        xoptions=Gtk.AttachOptions.FILL,
                        yoptions=Gtk.AttachOptions.FILL,
                        xpadding=5, ypadding=5)

        # add graph
        self.srolled_windows_for_plot = Gtk.ScrolledWindow()
        self.srolled_windows_for_plot.set_size_request(510, 310)
        vbox6.pack_start(self.srolled_windows_for_plot, True, True, 0)
        self.srolled_windows_for_plot.set_border_width(5)
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        canvas = FigureCanvas(self.fig)
        canvas.set_size_request(500, 300)
        self.srolled_windows_for_plot.add_with_viewport(canvas)

        vbox7 = Gtk.VBox(spacing=5)
        vbox7.set_border_width(5)
        notebook.append_page(vbox7, Gtk.Label.new(_('Disks')))
        srolled_windows_for_disks = Gtk.ScrolledWindow()
        srolled_windows_for_disks.set_size_request(510, 310)
        vbox7.pack_start(srolled_windows_for_disks, True, True, 0)
        srolled_windows_for_disks.set_border_width(5)
        self.vbox71 = Gtk.VBox(spacing=5)
        self.vbox71.set_border_width(5)
        srolled_windows_for_disks.add(self.vbox71)

        vbox99 = Gtk.VBox(spacing=5)
        vbox99.set_border_width(5)
        notebook.append_page(vbox99, Gtk.Label.new(_('About')))
        frame991 = Gtk.Frame.new()
        vbox99.pack_start(frame991, True, True, 0)
        table991 = Gtk.Table(9, 1, False)
        frame991.add(table991)
        logo = Gtk.Image()
        logo.set_from_file(comun.ICON)
        table991.attach(logo, 0, 1, 0, 1,
                        xoptions=Gtk.AttachOptions.EXPAND,
                        yoptions=Gtk.AttachOptions.FILL,
                        xpadding=5, ypadding=5)
        label = Gtk.Label()
        label.set_markup('<span color="black" font_desc="Ubuntu 32">%s</span>'
                         % ('<b>CPU-G</b>'))
        table991.attach(label, 0, 1, 1, 2,
                        xoptions=Gtk.AttachOptions.EXPAND,
                        yoptions=Gtk.AttachOptions.FILL,
                        xpadding=5, ypadding=5)
        label = Gtk.Label()
        label.set_markup('<span font_desc="Ubuntu 16">%s</span>'
                         % (comun.VERSION))
        table991.attach(label, 0, 1, 2, 3,
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
        table991.attach(label, 0, 1, 3, 4,
                        xoptions=Gtk.AttachOptions.EXPAND,
                        yoptions=Gtk.AttachOptions.FILL,
                        xpadding=5, ypadding=5)
        mcopyright = """
Copyright © 2009-2010 Fotis Tsamis
Copyright © Michael Schmöller
Copyright © 2012 Michał Głowienka
Copyright © 2012 Michał Olber
Copyright © 2016-2019 Lorenzo Carbonell
"""
        label = Gtk.Label()
        label.set_markup('<span font_desc="Ubuntu 12">%s</span>'
                         % (mcopyright))
        table991.attach(label, 0, 1, 4, 8,
                        xoptions=Gtk.AttachOptions.EXPAND,
                        yoptions=Gtk.AttachOptions.FILL,
                        xpadding=5, ypadding=5)
        label = Gtk.LinkButton(uri='https://www.atareao.es/aplicacion/\
cpu-g-donde-ver-hardware-instalado/')
        label.set_label('CPU-G')
        table991.attach(label, 0, 1, 8, 9,
                        xoptions=Gtk.AttachOptions.EXPAND,
                        yoptions=Gtk.AttachOptions.FILL,
                        xpadding=5, ypadding=5)
        self.ram_updater = 0
        self.uptime_updater = 0
        self.battery_updater = 0
        self.update_info()
        if self.exists_battery is True:
            self.read_data_for_battery_plot()
        else:
            widget = notebook.get_nth_page(self.battery_index)
            if widget is not None:
                notebook.detach_tab(widget)
        self.show_all()

    def read_data_for_battery_plot(self):
        bd = BatteryDriver()
        data = bd.get_history_charge()
        x = []
        y = []
        for element in data:
            x.append(element[0])
            y.append(element[1])
        self.ax.cla()
        self.ax.set_xlim(min(x), max(x))
        self.ax.set_ylim(-10, 110)
        self.ax.grid(True)

        def format_date(x, pos=None):
            ltime = time.localtime(x)
            return time.strftime('%H:%M', ltime)

        self.ax.xaxis.set_major_formatter(
            ticker.FuncFormatter(format_date))
        self.fig.autofmt_xdate()
        self.ax.plot(x, y)
        self.fig.canvas.draw()
        return True

    def _aux_set_text(self, textbox, value, value1):
        if isinstance(value, int):
            textbox.set_text(value1)
        else:
            textbox.set_text(value)

    def get_battery_duration(self):
        bd = BatteryDriver()
        if bd.get_state() == 'Charging':
            value = bd.get_time_to_full()
            self.battery_estimated_duration.set_text(
                str(datetime.timedelta(seconds=(value))))
            self.battery_data2.set_text(time.strftime('%H:%M:%S',
                                        time.localtime(value + time.time())))
        elif bd.get_state() == 'Discharging':
            value = bd.get_time_to_empty()
            self.battery_estimated_duration.set_text(
                str(datetime.timedelta(seconds=(value))))
            self.battery_data2.set_text(time.strftime('%H:%M:%S',
                                        time.localtime(value + time.time())))
        else:
            self.battery_estimated_duration.set_text('--')
            self.battery_data2.set_text('--')
        current_level = bd.get_percentage()
        self.battery_level_value.set_text(
            locale.format('%.2f', current_level) + _(' %'))
        self.battery_level.set_value(current_level)
        inv = Investigator()
        self.battery_capacity_level.set_text(
            '%s' % inv.battery_info('capacity-level'))
        self._aux_set_text(
            self.battery_voltage_now,
            inv.battery_info('voltage-now'),
            locale.format(
                '%.2f',
                inv.battery_info('voltage-now')/1000000) + _(' V'))
        self._aux_set_text(
            self.battery_min_voltage_design,
            inv.battery_info('voltage-min-design'),
            locale.format(
                '%.2f',
                inv.battery_info('voltage-min-design')/1000000) + _(' V'))
        self._aux_set_text(
            self.battery_charge_now,
            inv.battery_info('charge-now'),
            locale.format(
                '%.2f',
                inv.battery_info('charge-now')/1000000) + _(' Ah'))
        self._aux_set_text(
            self.battery_charge_full,
            inv.battery_info('charge-full'),
            locale.format(
                '%.2f',
                inv.battery_info('charge-full')/1000000) + _(' Ah'))
        self._aux_set_text(
            self.battery_charge_full_design,
            inv.battery_info('charge-full-design'),
            locale.format(
                '%.2f',
                inv.battery_info('charge-full-design')/1000000) + _(' Ah'))
        self._aux_set_text(
            self.battery_current_now,
            inv.battery_info('current-now'),
            locale.format(
                '%.2f',
                inv.battery_info('current-now')/1000000) + _(' A'))
        return True

    def uptime_update(self):
        self.uptime.set_text(Investigator().uptime())
        return True

    def ram_update(self):
        values = Investigator().raminfo()
        self.ram_total.set_text(
            locale.format('%.1f', values['total'], True) + ' ' + _('MB'))
        self.ram_available.set_text(
            locale.format('%.1f', values['available'], True) + ' ' + _('MB'))
        self.ram_available_progress.set_value(
            values['available']/values['total'])
        self.ram_used.set_text(
            locale.format('%.1f', values['used'], True) + ' ' + _('MB'))
        self.ram_used_progress.set_value(values['used']/values['total'])
        self.ram_free.set_text(
            locale.format('%.1f', values['free'], True) + ' ' + _('MB'))
        self.ram_free_progress.set_value(values['free']/values['total'])
        self.ram_active.set_text(
            locale.format('%.1f', values['active'], True) + ' ' + _('MB'))
        self.ram_inactive.set_text(
            locale.format('%.1f', values['inactive'], True) + ' ' + _('MB'))
        self.ram_buffers.set_text(
            locale.format('%.1f', values['buffers'], True) + ' ' + _('MB'))
        self.ram_cached.set_text(
            locale.format('%.1f', values['cached'], True) + ' ' + _('MB'))
        values = Investigator().swapinfo()
        self.swap_total.set_text(
            locale.format('%.1f', values['total'], True) + ' ' + _('MB'))
        if values['total'] == 0:
            values['total'] = 1
        self.swap_used.set_text(
            locale.format('%.1f', values['used'], True) + ' ' + _('MB'))
        self.swap_used_progress.set_value(values['used']/values['total'])
        self.swap_free.set_text(
            locale.format('%.1f', values['free'], True) + ' ' + _('MB'))
        self.swap_free_progress.set_value(values['free']/values['total'])
        self.swap_sin.set_text(
            locale.format('%.1f', values['sin'], True) + ' ' + _('MB'))
        self.swap_sout.set_text(
            locale.format('%.1f', values['sout'], True) + ' ' + _('MB'))
        return True

    def close_application(self, widget):
        print("Quit")
        self.stop_ram_updater()
        self.stop_uptime_updater()
        self.stop_battery_updater()
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
        self.hostname.set_text(os.uname()[1])
        self.architecture.set_text(os.uname()[4])
        self.kernel.set_text(os.uname()[2])
        self.xorg_server_version.set_text(inv.x_server_version())
        self.screen_resolution.set_text(inv.resolution())
        self.desktop_environment.set_text(inv.desktop_environment())
        self.window_manager.set_text(inv.get_window_manager())
        self.gcc_version.set_text(inv.gccver())
        self.distribution.set_text(inv.distro())
        distro_logo = inv.get_distro_logo()
        if distro_logo is not None:
            print(distro_logo)
            self.distro_logo.set_from_file(distro_logo)
        #
        self.graphic_controller.set_text(inv.open_gl('VGA'))
        self.opengl_vendor.set_text(inv.open_gl('vendor'))
        self.opengl_renderer.set_text(inv.open_gl('renderer'))
        self.opengl_version.set_text(inv.open_gl('version'))
        self.graphic_card_logo.set_from_file(inv.get_graphic_card_logo())
        #
        self.exists_battery = inv.battery_info('exists')
        if self.exists_battery is True:
            self.battery_manufacturer.set_text(
                inv.battery_info('manufacturer'))
            self.battery_model_name.set_text(inv.battery_info('model_name'))
            self.battery_serial_number.set_text(
                inv.battery_info('serial_number'))
            self.battery_technology.set_text(inv.battery_info('technology'))
        #
        for child in self.vbox71.get_children():
            self.vbox71.remove(child)
        devices = inv.disksinfo()
        for device in devices:
            frame7x = Gtk.Frame.new()
            self.vbox71.pack_start(frame7x, True, True, 0)
            table7x = Gtk.Table(10, 2, False)
            frame7x.add(table7x)
            label = Gtk.Label(_('Device'))
            label.set_alignment(0, 0.5)
            table7x.attach(label, 0, 1, 0, 1,
                           xoptions=Gtk.AttachOptions.FILL,
                           yoptions=Gtk.AttachOptions.FILL,
                           xpadding=5, ypadding=5)
            entry = Gtk.Entry()
            table7x.attach(entry, 1, 2, 0, 1,
                           xoptions=Gtk.AttachOptions.FILL,
                           yoptions=Gtk.AttachOptions.FILL,
                           xpadding=5, ypadding=5)
            entry.set_text(device['device'])
            label = Gtk.Label(_('Mount Point'))
            label.set_alignment(0, 0.5)
            table7x.attach(label, 0, 1, 1, 2,
                           xoptions=Gtk.AttachOptions.FILL,
                           yoptions=Gtk.AttachOptions.FILL,
                           xpadding=5, ypadding=5)
            entry = Gtk.Entry()
            table7x.attach(entry, 1, 2, 1, 2,
                           xoptions=Gtk.AttachOptions.FILL,
                           yoptions=Gtk.AttachOptions.FILL,
                           xpadding=5, ypadding=5)
            entry.set_text(device['mountpoint'])
            label = Gtk.Label(_('File System Type'))
            label.set_alignment(0, 0.5)
            table7x.attach(label, 0, 1, 2, 3,
                           xoptions=Gtk.AttachOptions.FILL,
                           yoptions=Gtk.AttachOptions.FILL,
                           xpadding=5, ypadding=5)
            entry = Gtk.Entry()
            table7x.attach(entry, 1, 2, 2, 3,
                           xoptions=Gtk.AttachOptions.FILL,
                           yoptions=Gtk.AttachOptions.FILL,
                           xpadding=5, ypadding=5)
            entry.set_text(device['fstype'])
            label = Gtk.Label(_('Options'))
            label.set_alignment(0, 0.5)
            table7x.attach(label, 0, 1, 3, 4,
                           xoptions=Gtk.AttachOptions.FILL,
                           yoptions=Gtk.AttachOptions.FILL,
                           xpadding=5, ypadding=5)
            entry = Gtk.Entry()
            table7x.attach(entry, 1, 2, 3, 4,
                           xoptions=Gtk.AttachOptions.FILL,
                           yoptions=Gtk.AttachOptions.FILL,
                           xpadding=5, ypadding=5)
            if len(device['opts']) > 70:
                entry.set_width_chars(70)
            else:
                entry.set_width_chars(len(device['opts']))
            entry.set_text(device['opts'])
            label = Gtk.Label(_('Total space'))
            label.set_alignment(0, 0.5)
            table7x.attach(label, 0, 1, 4, 5,
                           xoptions=Gtk.AttachOptions.FILL,
                           yoptions=Gtk.AttachOptions.FILL,
                           xpadding=5, ypadding=5)
            entry = Gtk.Entry()
            table7x.attach(entry, 1, 2, 4, 5,
                           xoptions=Gtk.AttachOptions.FILL,
                           yoptions=Gtk.AttachOptions.FILL,
                           xpadding=5, ypadding=5)
            entry.set_text(locale.format(
                '%.2f', device['total']/1024/1024, True) + ' ' + _('MB'))
            label = Gtk.Label(_('Used space'))
            label.set_alignment(0, 0.5)
            table7x.attach(label, 0, 1, 5, 7,
                           xoptions=Gtk.AttachOptions.FILL,
                           yoptions=Gtk.AttachOptions.FILL,
                           xpadding=5, ypadding=5)
            entry = Gtk.Entry()
            table7x.attach(entry, 1, 2, 5, 6,
                           xoptions=Gtk.AttachOptions.FILL,
                           yoptions=Gtk.AttachOptions.FILL,
                           xpadding=5, ypadding=5)
            entry.set_text(locale.format(
                '%.2f', device['used']/1024/1024, True) + ' ' + _('MB'))
            disk_used_progress = Gtk.LevelBar()
            disk_used_progress.set_min_value(0)
            disk_used_progress.set_max_value(1)
            disk_used_progress.set_value(device['used']/device['total'])
            table7x.attach(disk_used_progress, 1, 2, 6, 7,
                           xoptions=Gtk.AttachOptions.FILL,
                           yoptions=Gtk.AttachOptions.FILL,
                           xpadding=5, ypadding=5)
            label = Gtk.Label(_('Free space'))
            label.set_alignment(0, 0.5)
            table7x.attach(label, 0, 1, 7, 9,
                           xoptions=Gtk.AttachOptions.FILL,
                           yoptions=Gtk.AttachOptions.FILL,
                           xpadding=5, ypadding=5)
            entry = Gtk.Entry()
            table7x.attach(entry, 1, 2, 7, 8,
                           xoptions=Gtk.AttachOptions.FILL,
                           yoptions=Gtk.AttachOptions.FILL,
                           xpadding=5, ypadding=5)
            entry.set_text(locale.format(
                '%.2f', device['free']/1024/1024, True) + ' ' + _('MB'))
            disk_free_progress = Gtk.LevelBar()
            disk_free_progress.set_min_value(0)
            disk_free_progress.set_max_value(1)
            disk_free_progress.set_value(device['free']/device['total'])
            table7x.attach(disk_free_progress, 1, 2, 8, 9,
                           xoptions=Gtk.AttachOptions.FILL,
                           yoptions=Gtk.AttachOptions.FILL,
                           xpadding=5, ypadding=5)

        #
        self.start_ram_updater()
        self.start_uptime_update()
        if self.exists_battery is True:
            self.start_battery_updater()

    def start_ram_updater(self):
        if self.ram_updater > 0:
            GLib.source_remove(self.ram_updater)
        self.ram_update()
        self.ram_updater = GLib.timeout_add_seconds(1, self.ram_update)

    def stop_ram_updater(self):
        if self.ram_updater > 0:
            GLib.source_remove(self.ram_updater)
            self.ram_updater = 0

    def start_uptime_update(self):
        if self.uptime_updater > 0:
            GLib.source_remove(self.uptime_updater)
        self.uptime_update()
        self.uptime_updater = GLib.timeout_add_seconds(60, self.uptime_update)

    def stop_uptime_updater(self):
        if self.uptime_updater > 0:
            GLib.source_remove(self.uptime_updater)
            self.uptime_updater = 0

    def start_battery_updater(self):
        if self.battery_updater > 0:
            GLib.source_remove(self.battery_updater)
        if self.exists_battery is True:
            self.get_battery_duration()
            self.battery_updater = GLib.timeout_add_seconds(
                300, self.get_battery_duration)

    def stop_battery_updater(self):
        if self.battery_updater > 0:
            GLib.source_remove(self.battery_updater)
            self.battery_updater = 0

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
    cpug = CPUG()
    Gtk.main()
    exit(0)
