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
import comun
import time
import datetime
import sys
import numpy
import decimal
from comun import _
from crontab import CronTab
import getpass
from matplotlib.figure import Figure
from matplotlib.backends.backend_gtk3cairo import FigureCanvasGTK3Cairo as FigureCanvas
import matplotlib.ticker as ticker
from investigator import Investigator

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
        label = Gtk.Label(_('Xorg version'))
        label.set_alignment(0, 0.5)
        table41.attach(label, 0, 1, 5, 6,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.xorg_version = Gtk.Entry()
        table41.attach(self.xorg_version, 1, 2, 5, 6,
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
        notebook.append_page(vbox6, Gtk.Label.new(_('Battery')))

        frame60 = Gtk.Frame.new()
        vbox6.pack_start(frame60, True, True, 0)
        table601 = Gtk.Table(3, 3, False)
        frame60.add(table601)
        label = Gtk.Label(_('Monitoring battery?'))
        label.set_alignment(0, 0.5)
        table601.attach(label, 0, 1, 0, 1,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.monitor_battery = Gtk.Switch()
        self.monitor_battery.set_active(self.is_monitor_battery_activated())
        table601.attach(self.monitor_battery, 0, 1, 1, 2,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.monitor_battery.connect('state-set',
                                     self.on_monitor_battery_activate)
        frame611 = Gtk.Frame.new()
        vbox6.pack_start(frame611, True, True, 0)
        table611 = Gtk.Table(3, 3, False)
        frame611.add(table611)
        label = Gtk.Label(_('Manufacturer'))
        label.set_alignment(0, 0.5)
        table611.attach(label, 0, 1, 0, 1,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.battery_manufacturer = Gtk.Entry()
        self.battery_manufacturer.set_width_chars(50)
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
        self.battery_model_name.set_width_chars(50)
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
        self.battery_serial_number.set_width_chars(50)
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
        self.battery_technology.set_width_chars(50)
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
        self.battery_estimated_duration.set_width_chars(50)
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
        self.battery_data2.set_width_chars(50)
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
        self.battery_level_value.set_width_chars(50)
        table611.attach(self.battery_level_value, 1, 2, 6, 7,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.battery_level = Gtk.LevelBar()
        self.battery_level.set_min_value(0)
        self.battery_level.set_max_value(100)
        self.battery_level.set_value(50)
        table611.attach(self.battery_level, 1, 2, 7, 8,
                       xoptions=Gtk.AttachOptions.FILL,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)

        # add graph
        self.fig = Figure(figsize=(20,20), dpi=80)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.set_size_request(500,300)
        vbox6.pack_start(self.canvas, True, True, 0)
        self.liststore = Gtk.ListStore(float, float)
        self.liststore.append([2.35, 2.40])
        self.liststore.append([3.45, 4.70])

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
Michael Schmöller
Copyright © 2012 Michał Głowienka
Copyright © 2012 Michał Olber
Copyright © 2016 Lorenzo Carbonell
"""
        label = Gtk.Label()
        label.set_markup('<span font_desc="Ubuntu 12">%s</span>'
                         % (mcopyright))
        table991.attach(label, 0, 1, 4, 8,
                       xoptions=Gtk.AttachOptions.EXPAND,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        label = Gtk.LinkButton(uri='http://www.atareao.es')
        label.set_label('http://www.atareao.es')
        table991.attach(label, 0, 1, 8, 9,
                       xoptions=Gtk.AttachOptions.EXPAND,
                       yoptions=Gtk.AttachOptions.FILL,
                       xpadding=5, ypadding=5)
        self.ram_updater = 0
        self.uptime_updater = 0
        self.battery_updater = 0
        self.update_info()
        if self.is_monitor_battery_activated():
            self.read_data_for_battery_plot()
        self.show_all()

    def read_data_for_battery_plot(self):
        if os.path.exists('/var/tmp/monitor_battery.log'):
            reader = open('/var/tmp/monitor_battery.log', 'r')
            data = list(reversed(list(reader)))
            reader.close()
            if len(data) > 3:
                data = data[:288]
                ctime = int(time.time())
                result = []
                for adata in data:
                    current = int(adata[-4:-2])
                    result.append([ctime, current])
                    ctime = ctime - 300
                result = list(reversed(result))
                minx = -1
                maxx = -1
                self.liststore.clear()
                for element in result:
                    self.liststore.append(element)
                    if element[0] < minx or minx == -1:
                        minx = element[0]
                    if element[0] > maxx or maxx == -1:
                        maxx = element[0]
                self.ax.cla()
                self.ax.set_xlim(minx, maxx)
                self.ax.set_ylim(-10, 110)
                self.ax.grid(True)

                def format_date(x, pos=None):
                    ltime = time.localtime(x)
                    return time.strftime('%H:%M', ltime)

                self.ax.xaxis.set_major_formatter(
                    ticker.FuncFormatter(format_date))
                self.fig.autofmt_xdate()
                for row in self.liststore:
                    self.ax.scatter(row[:1], row[1:],
                                    marker='.', s=50, linewidths=1)
                self.fig.canvas.draw()
                return True
            return False

    def get_battery_duration(self):
        if self.read_data_for_battery_plot():
            inv = Investigator()
            if inv.battery_info('status').lower() == 'discharging' and\
                    self.is_monitor_battery_activated():
                reader = open('/var/tmp/monitor_battery.log', 'r')
                data = reversed(list(reader))
                gdata = []
                previous = 0
                for line in data:
                    current = int(line[-4:-2])
                    if current >= previous:
                        print(current)
                        gdata.append(current)
                    else:
                        break
                    previous = current
                result = []
                ctime = int(time.time())
                current_level = gdata[0]
                for adata in gdata:
                    result.append([ctime, adata])
                    ctime = ctime - 300
                result = list(reversed(result))
                previous = -1
                count = 0
                first = result[0][1]
                for element in result[1:]:
                    current = element[1]
                    if first == current:
                        count += 1
                    else:
                        break
                result = result[count:]
                #
                M = numpy.empty([len(result), 2])
                YA = numpy.empty([len(result), 1])
                for index, row in enumerate(result):
                    x = decimal.Decimal(row[0])
                    y = decimal.Decimal(row[1])
                    YA[index, 0] = decimal.Decimal(y)
                    M[index, 0] = 1
                    M[index, 1] = decimal.Decimal(x)
                # pseudoinversa
                # MS = (AT x A)^-1 x AT
                A = numpy.mat(M.copy())
                AT = A.T
                #ATA = numpy.dot(AT,A)
                ATA = AT * A
                ATAI = ATA.I
                MS = numpy.dot(ATAI,AT)
                Y = numpy.mat(YA.copy())
                ANS = MS * Y
                a = ANS[0]
                b = ANS[1]
                value = int(-a/b)
                self.battery_estimated_duration.set_text(
                    str(datetime.timedelta(seconds=(int(value - time.time())))))
                self.battery_data2.set_text(time.strftime('%H:%M:%S',
                                            time.localtime(value)))
                self.battery_level_value.set_text('%s %%' % current_level)
                self.battery_level.set_value(current_level)
        return True

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
        self.xorg_version.set_text(inv.xver())
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
        self.battery_manufacturer.set_text(inv.battery_info('manufacturer'))
        self.battery_model_name.set_text(inv.battery_info('model_name'))
        self.battery_serial_number.set_text(inv.battery_info('serial_number'))
        self.battery_technology.set_text(inv.battery_info('technology'))
        #
        self.start_ram_updater()
        self.start_uptime_update()
        if self.is_monitor_battery_activated():
            self.start_battery_updater()
        else:
            self.stop_battery_updater()

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

    def on_monitor_battery_activate(self, widget, status):
        print(widget, status)
        cron = CronTab(user=True)
        cron.remove_all(command=comun.BATTERY_MONITOR)
        cron.write()
        if status:
            job = cron.new(command=comun.BATTERY_MONITOR,
                           comment='--monitor-battery-cpu-g--')
            job.minute.every(5)
            job.enable()
            cron.write()
            self.battery_level.set_visible(True)
            self.canvas.set_visible(True)
            self.get_battery_duration()
            self.start_battery_updater()
        else:
            self.stop_battery_updater()
            self.battery_estimated_duration.set_text('--')
            self.battery_data2.set_text('--')
            self.battery_level_value.set_text('--')
            self.battery_level.set_visible(False)
            self.canvas.set_visible(False)


    def is_monitor_battery_activated(self):
        cron = CronTab(user=True)
        print(0)
        for job in cron:
            print(1, job)
            if job.is_enabled():
                return True
        return False


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
