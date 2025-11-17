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
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

import matplotlib
matplotlib.use('GTK3Agg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas

class MatplotlibGTKWindow:
    def __init__(self):
        self.window = Gtk.Window()
        self.window.connect("delete-event", Gtk.main_quit)
        self.window.set_default_size(800, 600)
        self.window.set_title("Embedding in GTK - Updated")
        self.setup_ui()

    def setup_ui(self):
        # Create scrolled window
        sw = Gtk.ScrolledWindow()
        sw.set_border_width(10)
        sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        # Create matplotlib figure and plot
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.axes = self.figure.add_subplot(111)

        # Sample data
        t = [1, 2, 3, 4]
        s = [1, 4, 9, 16]
        self.axes.plot(t, s, 'b-', linewidth=2)
        self.axes.set_xlabel('Time')
        self.axes.set_ylabel('Value')
        self.axes.set_title('Sample Plot')
        self.axes.grid(True)

        # Create canvas
        self.canvas = FigureCanvas(self.figure)
        self.canvas.set_size_request(600, 400)

        # Add canvas to scrolled window
        sw.add(self.canvas)

        # Add scrolled window to main window
        self.window.add(sw)

    def show(self):
        self.window.show_all()
        Gtk.main()

if __name__ == "__main__":
    app = MatplotlibGTKWindow()
    app.show()
