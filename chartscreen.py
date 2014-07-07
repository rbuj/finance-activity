# Copyright 2008 by Wade Brainerd.
# This file is part of Finance.
#
# Finance is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Finance is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Finance.  If not, see <http://www.gnu.org/licenses/>.

# Import standard Python modules.
import math
import locale

# Import activity module
import colors

from gettext import gettext as _

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject

from sugar3.graphics import style

# Set up localization.
locale.setlocale(locale.LC_ALL, '')

CHART_HELP = _(
    'The Chart view shows the proportion of your expenses that is in each '
    'category.\nYou can categorize transactions in the Register view.')


class ChartScreen(Gtk.HBox):
    def __init__(self, activity):
        GObject.GObject.__init__(self)

        self.activity = activity

        self.category_total = {}
        self.sorted_categories = []

        self.area = Gtk.DrawingArea()
        self.area.connect('draw', self.chart_draw_cb)

        label = Gtk.Label()
        label.set_markup('<b>' + _('Debit Categories') + '</b>')
        label.props.margin_top = style.GRID_CELL_SIZE
        label.props.margin_right = style.GRID_CELL_SIZE / 2

        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        separator.props.margin_right = style.GRID_CELL_SIZE / 2

        self.catbox = Gtk.VBox()
        self.catbox.props.margin_right = style.GRID_CELL_SIZE / 2

        white_box = Gtk.EventBox()
        white_box.modify_bg(Gtk.StateType.NORMAL,
                            style.COLOR_WHITE.get_gdk_color())
        box = Gtk.VBox()
        box.pack_start(label, False, False, 0)
        box.pack_start(separator, False, False, 0)
        box.pack_start(self.catbox, False, False, 10)

        white_box.add(box)

        self.pack_start(self.area, True, True, 0)
        self.pack_start(white_box, False, False, 0)

        self.show_all()

    def build(self):
        # Build the category totals.
        self.category_total = {}
        for t in self.activity.visible_transactions:
            cat = t['category']
            amount = t['amount']

            if t['type'] == 'debit':
                if cat not in self.category_total:
                    self.category_total[cat] = amount
                else:
                    self.category_total[cat] += amount

        # Generate a list of names sorted by total.
        self.sorted_categories = self.category_total.keys()
        # self.sorted_categories.sort(lamba a, b: cmp(self.category_total[a],
        #                                             self.category_total[b]))

        # Clear and rebuild the labels box.
        for w in self.catbox.get_children():
            self.catbox.remove(w)

        catgroup = Gtk.SizeGroup(Gtk.SizeGroupMode.HORIZONTAL)
        amountgroup = Gtk.SizeGroup(Gtk.SizeGroupMode.HORIZONTAL)

        for c in self.sorted_categories:
            hbox = Gtk.HBox()

            description = c
            # If there is no category, display as Unknown
            if c is '':
                description = _('Unknown')
            catlabel = Gtk.Label(label=description)
            catgroup.add_widget(catlabel)

            color = colors.get_category_color_str(c)

            amountlabel = Gtk.Label()
            amountlabel.set_text(locale.currency(self.category_total[c]))
            amountgroup.add_widget(amountlabel)

            hbox.pack_start(amountlabel, True, True, 20)
            hbox.pack_start(catlabel, True, True, 20)

            ebox = Gtk.EventBox()

            parse, color = Gdk.Color.parse(color)
            ebox.modify_bg(Gtk.StateType.NORMAL, color)
            ebox.add(hbox)

            self.catbox.pack_end(ebox, False, False, 5)

        self.show_all()

    def chart_draw_cb(self, widget, context):
        # Draw pie chart.
        bounds = widget.get_allocation()
        context.rectangle(0, 0, bounds.width, bounds.height)
        context.set_source_rgb(1, 1, 1)
        context.fill()

        x = bounds.width / 2
        y = bounds.height / 2
        r = min(bounds.width, bounds.height) / 2 - 10

        total = 0
        for c in self.sorted_categories:
            total += self.category_total[c]

        if total != 0:
            angle = 0.0

            for c in self.sorted_categories:
                slice = 2 * math.pi * self.category_total[c] / total
                color = colors.get_category_color(c)

                context.move_to(x, y)
                context.arc(x, y, r, angle, angle + slice)
                context.close_path()

                context.set_source_rgb(color[0], color[1], color[2])
                context.fill()

                angle += slice
