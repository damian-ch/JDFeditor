#!/usr/bin/env python
# coding=utf-8
# -----------------------------------------------------------------------------
# Name:        jdf_editor.py
# Purpose:     JDF database editor
# Author:      Damian Chrzanowski
# Created:     22/03/16
# Modified:    14/04/16
# Copyright:   pjdamian.chrzanowski@gmail.com
# License:     GNU Public License v3
# Version:     1.0
# Revision:    N/A
# -----------------------------------------------------------------------------
# jdf_editor, GUI application for editing database files,
#             specifically designed for the new JDF file format.
#             (J)son(D)atabase(F)ormat
# Copyright (C) 2016 Damian Chrzanowski
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
# --------------------------------------------
from gi.repository import Gdk, GdkPixbuf, Gtk

import export_html
import jdf_lib
import os
import webbrowser

if os.name == 'nt':
    PATH_BREAK = '\\'  # set the windows style path breaker = '\'
else:
    PATH_BREAK = '/'   # set the Linux / Mac OS X style path breaker = '/'

VERSION = 'v 1.1'   # current version


class MainWindow(object):
    """Main window.

    (None) -> None

    Contains the main window object and various subclasses.
    """

    def __init__(self):
        """Class constructor.

        (self) -> None
        """
        self.window = Gtk.Window()
        self.window.set_title('JDF Editor ' + VERSION)
        self.window.set_default_size(700, 400)
        self.window.set_icon_from_file('icon_small.png')
        self.window.connect("delete-event", self.quit)
        self.grid = Gtk.Grid()
        self.grid.set_row_spacing(5)
        self.grid.set_column_spacing(5)
        self.window.add(self.grid)  # add the grid to the window

        # accel group (keyboard shortcuts group)
        self.accelgroup = Gtk.AccelGroup()
        self.window.add_accel_group(self.accelgroup)

        # tabs (aka notebook)
        self.notebook_tabs = Gtk.Notebook()
        self.grid.attach(self.notebook_tabs, 0, 2, 1, 1)  # add the tabs frame to the grid
        self.notebook_tabs.set_hexpand(True)    # expand horizontaly
        self.notebook_tabs.set_vexpand(True)    # expand vertically
        self.notebook_tabs.set_scrollable(True)
        self.notebook_tabs.connect('switch-page', self.notebook_page_switched)  # post current tab name to the title bar
        self.notebook_tabs.set_show_tabs(True)  # always show tabs

        # status bar
        self.statusbar = Gtk.Statusbar()
        self.context = self.statusbar.get_context_id("example")
        self.grid.attach(self.statusbar, 0, 3, 1, 1)    # attach the status bar to the bottom of the grid

        # clipboard
        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)  # set the clipboard selection mode
        # self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_PRIMARY)

        # right click menu
        # uses make_menu_item() function to create boxes with an image and a label
        # that box is then placed inside of the Gtk.MenuItem()
        self.menu = Gtk.Menu()

        self.menuitem = Gtk.MenuItem()
        self.menuitem.add(make_menu_item('edit-cut', 'Cut', from_file=False))
        self.menuitem.connect('activate', lambda q: clipboard_manager('cut'))
        self.menu.append(self.menuitem)

        self.menuitem = Gtk.MenuItem()
        self.menuitem.add(make_menu_item('edit-copy', 'Copy', from_file=False))
        self.menuitem.connect('activate', lambda q: clipboard_manager('copy'))
        self.menu.append(self.menuitem)

        self.menuitem = Gtk.MenuItem()
        self.menuitem.add(make_menu_item('edit-paste', 'Paste', from_file=False))
        self.menuitem.connect('activate', lambda q: clipboard_manager('paste'))
        self.menu.append(self.menuitem)

        self.separator = Gtk.SeparatorMenuItem()
        self.menu.append(self.separator)

        self.menuitem = Gtk.MenuItem()
        self.menuitem.add(make_menu_item('icons/16/insert_row.png', 'Insert a row here', from_file=True))
        self.menuitem.connect('activate', lambda q: add_row('insert-here'))
        self.menu.append(self.menuitem)

        self.menuitem = Gtk.MenuItem()
        self.menuitem.add(make_menu_item('icons/16/delete_row.png', 'Delete a row here', from_file=True))
        self.menuitem.connect('activate', lambda q: delete_row('delete-here'))
        self.menu.append(self.menuitem)

        self.separator = Gtk.SeparatorMenuItem()
        self.menu.append(self.separator)

        self.menuitem = Gtk.MenuItem()
        self.menuitem.add(make_menu_item('icons/16/insert_column.png', 'Insert a column', from_file=True))
        self.menuitem.connect('activate', lambda q: add_column('insert-at'))
        self.menu.append(self.menuitem)

        self.menuitem = Gtk.MenuItem()
        self.menuitem.add(make_menu_item('icons/16/delete_column.png', 'Delete a column', from_file=True))
        self.menuitem.connect('activate', lambda q: delete_column('delete-at'))
        self.menu.append(self.menuitem)

        self.separator = Gtk.SeparatorMenuItem()
        self.menu.append(self.separator)

        self.menuitem = Gtk.MenuItem()
        self.menuitem.add(make_menu_item('icons/16/convert.png', 'Convert a column', from_file=True))
        self.menuitem.connect('activate', lambda q: convert_column())
        self.menu.append(self.menuitem)

    def quit(self, widget, something):
        """Exit the program.

        (self, object, object) -> bool

        Checks whether there are unsaved changes through calling check_before_quit() function.
        """
        return check_before_quit()

    def push_message(self, text_pushed):
        """Display message in the statusbar.

        (self, str) -> None
        """
        self.statusbar.push(self.context, text_pushed)

    def post_filename_to_title(self, filename):
        """Display filename in the titlebar.

        (self, str) -> None

        :param filename: is the filename that will be posted in the title
        """
        self.window.set_title('JDF Editor ' + VERSION + ' - ' + filename)

    def notebook_page_switched(self, widget, page, page_num):
        """Switch the page if changed.

        (self, object, object, int) -> None

        :param page_num: is the page number that is being switched to.

        This is used to post the current tab's name into the title bar, after switching pages.
        """
        tab_control('switched', data=page_num)


class MainMenu(object):
    """Main Menu of the Window"""

    def __init__(self, MAINWINDOW):
        """Main menu constructor.

        (self, object) -> None

        :param MAINWINDOW: is the class instance of the main window.
        """
        self.MAINWINDOW = MAINWINDOW
        self.menubar = Gtk.MenuBar()
        self.menubar.set_hexpand(True)
        self.MAINWINDOW.grid.attach(self.menubar, 0, 0, 1, 1)  # attach the menu into the main window's grid

        self.menuitem = Gtk.MenuItem("_File", use_underline=True)
        self.menubar.append(self.menuitem)  # add the menu to the menubar
        self.menu1 = Gtk.Menu()  # make a sub menu
        self.menuitem.set_submenu(self.menu1)   # attach submenu

        # most menu items call make_menu_item() function that creates a box with a label, image and accel label
        # this box is the placed within a Gtk.MenuItem()
        self.menuitem = Gtk.MenuItem()
        self.menuitem.add(make_menu_item('document-new', 'New', accel='Ctrl+N'))
        self.menuitem.add_accelerator('activate', self.MAINWINDOW.accelgroup, Gdk.keyval_from_name(
            "n"), Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE)  # set a Ctrl+N shortcut
        self.menuitem.connect('activate', lambda q: tab_control('new'))  # launch tab control when clicked
        self.menuitem.connect('select', lambda q: status_msg('Create a new file'))  # post to statusbar on hover
        self.menu1.append(self.menuitem)  # add to the menu

        self.menuitem = Gtk.MenuItem()
        self.menuitem.add(make_menu_item('document-open', 'Open', accel='Ctrl+O'))
        self.menuitem.add_accelerator('activate', self.MAINWINDOW.accelgroup, Gdk.keyval_from_name(
            "o"), Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE)
        self.menuitem.connect('activate', lambda q: open_file())
        self.menuitem.connect('select', lambda q: status_msg('Open a new file'))
        self.menu1.append(self.menuitem)

        self.menuitem = Gtk.MenuItem()
        self.menuitem.add(make_menu_item('document-save', 'Save', accel='Ctrl+S'))
        self.menuitem.add_accelerator('activate', self.MAINWINDOW.accelgroup, Gdk.keyval_from_name(
            "s"), Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE)
        self.menuitem.connect('activate', lambda q: save_file())
        self.menuitem.connect('select', lambda q: status_msg('Save a file to disk'))
        self.menu1.append(self.menuitem)

        self.menuitem = Gtk.MenuItem()
        self.menuitem.add(make_menu_item('document-save-as', 'Save as...', accel='Ctrl+Shift+S'))
        self.menuitem.add_accelerator('activate', self.MAINWINDOW.accelgroup, Gdk.keyval_from_name(
            "s"), Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.SHIFT_MASK, Gtk.AccelFlags.VISIBLE)
        self.menuitem.set_label('Save As...')
        self.menuitem.connect('activate', lambda q: save_file(force_dialog=True))
        self.menuitem.connect('select', lambda q: status_msg('Save a file as a different file name'))
        self.menu1.append(self.menuitem)

        self.separator = Gtk.SeparatorMenuItem()
        self.menu1.append(self.separator)

        self.menuitem = Gtk.MenuItem('Recent Items')
        self.menu1.append(self.menuitem)

        self.recentchoosermenu = Gtk.RecentChooserMenu()

        self.recentfilter = Gtk.RecentFilter()
        self.recentfilter.set_name("JDF Database Files")
        self.recentfilter.add_pattern("*.jdf")   # display only jdf files in the recent files submenu
        self.recentchoosermenu.add_filter(self.recentfilter)

        self.recentchoosermenu.connect("item-activated", self.item_activated)
        self.menuitem.set_submenu(self.recentchoosermenu)

        self.separator = Gtk.SeparatorMenuItem()
        self.menu1.append(self.separator)

        self.menuitem = Gtk.MenuItem()
        self.menuitem.add(make_menu_item('text-html', 'Export as HTML'))
        self.menuitem.connect("activate", lambda q: export_to_html())
        self.menuitem.connect('select', lambda q: status_msg('Export current database as a html file'))
        self.menu1.append(self.menuitem)

        self.separator = Gtk.SeparatorMenuItem()
        self.menu1.append(self.separator)

        self.menuitem = Gtk.MenuItem()
        self.menuitem.add(make_menu_item('application-exit', 'Quit', accel='Ctrl+Q'))
        self.menuitem.add_accelerator('activate', self.MAINWINDOW.accelgroup, Gdk.keyval_from_name(
            "q"), Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE)
        self.menuitem.connect("activate", lambda q: check_before_quit())
        self.menuitem.connect('select', lambda q: status_msg('Exit the program'))
        self.menu1.append(self.menuitem)

        self.menuitem = Gtk.MenuItem(label="_Edit", use_underline=True)
        self.menubar.append(self.menuitem)
        self.menu1 = Gtk.Menu()
        self.menuitem.set_submenu(self.menu1)

        # self.menuitem = Gtk.MenuItem()
        # self.menuitem.add(make_menu_item('edit-undo', 'Undo', accel='Ctrl+Z'))
        # self.menuitem.add_accelerator('activate', self.MAINWINDOW.accelgroup, Gdk.keyval_from_name(
        #     "z"), Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE)
        # self.menuitem.connect('select', lambda q: status_msg('Undo recent changes'))
        # self.menu1.append(self.menuitem)
        #
        # self.menuitem = Gtk.MenuItem()
        # self.menuitem.add(make_menu_item('edit-redo', 'Redo', accel='Ctrl+Y'))
        # self.menuitem.add_accelerator('activate', self.MAINWINDOW.accelgroup, Gdk.keyval_from_name(
        #     "y"), Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE)
        # self.menuitem.connect('select', lambda q: status_msg('Redo recent changes'))
        # self.menu1.append(self.menuitem)
        #
        # self.separator = Gtk.SeparatorMenuItem()
        # self.menu1.append(self.separator)

        self.menuitem = Gtk.MenuItem()
        self.menuitem.add(make_menu_item('edit-cut', 'Cut', accel='Ctrl+X'))
        self.menuitem.add_accelerator('activate', self.MAINWINDOW.accelgroup, Gdk.keyval_from_name(
            "x"), Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE)
        self.menuitem.connect('activate', lambda q: clipboard_manager('cut'))
        self.menuitem.connect('select', lambda q: status_msg('Cut out currently highlighted data to the clipboard'))
        self.menu1.append(self.menuitem)

        self.menuitem = Gtk.MenuItem()
        self.menuitem.add(make_menu_item('edit-copy', 'Copy', accel='Ctrl+C'))
        self.menuitem.add_accelerator('activate', self.MAINWINDOW.accelgroup, Gdk.keyval_from_name(
            "c"), Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE)
        self.menuitem.connect('activate', lambda q: clipboard_manager('copy'))
        self.menuitem.connect('select', lambda q: status_msg('Copy currently highlighted data to the clipboard'))
        self.menu1.append(self.menuitem)

        self.menuitem = Gtk.MenuItem()
        self.menuitem.add(make_menu_item('edit-paste', 'Paste', accel='Ctrl+V'))
        self.menuitem.add_accelerator('activate', self.MAINWINDOW.accelgroup, Gdk.keyval_from_name(
            "v"), Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE)
        self.menuitem.connect('activate', lambda q: clipboard_manager('paste'))
        self.menuitem.connect('select', lambda q: status_msg('Paste in data from the clipboard into the database'))
        self.menu1.append(self.menuitem)

        self.menuitem = Gtk.MenuItem(label="_Tabs", use_underline=True)
        self.menubar.append(self.menuitem)
        self.menu = Gtk.Menu()
        self.menuitem.set_submenu(self.menu)

        self.menuitem = Gtk.MenuItem()
        self.menuitem.add(make_menu_item('document-new', 'New Tab', accel='Ctrl+T'))
        self.menuitem.add_accelerator('activate', self.MAINWINDOW.accelgroup, Gdk.keyval_from_name(
            "t"), Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE)
        self.menuitem.connect('activate', lambda q: tab_control('new'))
        self.menuitem.connect('select', lambda q: status_msg('Create a new empty tab'))
        self.menu.append(self.menuitem)

        self.menuitem = Gtk.MenuItem()
        self.menuitem.add(make_menu_item('window-close', 'Close Tab', accel='Ctrl+W'))
        self.menuitem.set_label('Close Tab')
        self.menuitem.add_accelerator('activate', self.MAINWINDOW.accelgroup, Gdk.keyval_from_name(
            "w"), Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE)
        self.menuitem.connect('activate', lambda q: tab_control('close'))
        self.menuitem.connect('select', lambda q: status_msg('Close the current tab'))
        self.menu.append(self.menuitem)

        self.menuitem = Gtk.MenuItem()
        self.menuitem.add(make_menu_item('go-next', 'Next Tab', accel='Ctrl+Right'))
        self.menuitem.add_accelerator('activate', self.MAINWINDOW.accelgroup, Gdk.keyval_from_name(
            "Right"), Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE)
        self.menuitem.connect('activate', lambda q: tab_control('next'))
        self.menuitem.connect('select', lambda q: status_msg('Switch to the next tab'))
        self.menu.append(self.menuitem)

        self.menuitem = Gtk.MenuItem()
        self.menuitem.add(make_menu_item('go-previous', 'Previous Tab', accel='Ctrl+Left'))
        self.menuitem.add_accelerator('activate', self.MAINWINDOW.accelgroup, Gdk.keyval_from_name(
            "Left"), Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE)
        self.menuitem.connect('activate', lambda q: tab_control('previous'))
        self.menuitem.connect('select', lambda q: status_msg('Switch to the previous tab'))
        self.menu.append(self.menuitem)

        self.menuitem = Gtk.MenuItem(label="_Cells", use_underline=True)
        self.menubar.append(self.menuitem)
        self.menu = Gtk.Menu()
        self.menuitem.set_submenu(self.menu)

        self.menuitem = Gtk.MenuItem()
        self.menuitem.add(make_menu_item('icons/16/insert_row.png', 'Append row', accel='Ctrl+Insert', from_file=True))
        self.menuitem.connect('activate', lambda q: add_row('append'))
        self.menuitem.connect('select', lambda q: status_msg('Insert a row at the end of the database'))
        self.menuitem.add_accelerator('activate', self.MAINWINDOW.accelgroup, Gdk.keyval_from_name(
            "Insert"), Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE)
        self.menu.append(self.menuitem)

        self.menuitem = Gtk.MenuItem()
        self.menuitem.add(make_menu_item('icons/16/insert_row.png', 'Prepend row', from_file=True))
        self.menuitem.connect('activate', lambda q: add_row('prepend'))
        self.menuitem.connect('select', lambda q: status_msg('Insert a row at the beginning of the database'))
        self.menu.append(self.menuitem)

        self.menuitem = Gtk.MenuItem()
        self.menuitem.add(make_menu_item('icons/16/insert_row.png', 'Insert row at...', from_file=True))
        self.menuitem.connect('activate', lambda q: add_row('insert-at'))
        self.menuitem.connect('select', lambda q: status_msg('Insert a row at a specific location within the database'))
        self.menu.append(self.menuitem)

        self.menuitem = Gtk.MenuItem()
        self.menuitem.add(make_menu_item('icons/16/insert_row.png', 'Insert row here', from_file=True))
        self.menuitem.connect('activate', lambda q: add_row('insert-here'))
        self.menuitem.connect('select', lambda q: status_msg('Insert a row at the currently highlighted area'))
        self.menu.append(self.menuitem)

        self.separator = Gtk.SeparatorMenuItem()
        self.menu.append(self.separator)

        self.menuitem = Gtk.MenuItem()
        self.menuitem.add(make_menu_item('icons/16/delete_row.png',
                                         'Delete last row', accel='Ctrl+Delete', from_file=True))
        self.menuitem.connect('activate', lambda q: delete_row('delete-last'))
        self.menuitem.connect('select', lambda q: status_msg('Delete the last row from the database'))
        self.menuitem.add_accelerator('activate', self.MAINWINDOW.accelgroup, Gdk.keyval_from_name(
            "Delete"), Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE)
        self.menu.append(self.menuitem)

        self.menuitem = Gtk.MenuItem()
        self.menuitem.add(make_menu_item('icons/16/delete_row.png', 'Delete first row', from_file=True))
        self.menuitem.connect('activate', lambda q: delete_row('delete-first'))
        self.menuitem.connect('select', lambda q: status_msg('Delete the last row from the database'))
        self.menu.append(self.menuitem)

        self.menuitem = Gtk.MenuItem()
        self.menuitem.add(make_menu_item('icons/16/delete_row.png', 'Delete row at...', from_file=True))
        self.menuitem.connect('activate', lambda q: delete_row('delete-at'))
        self.menuitem.connect('select', lambda q: status_msg('Delete a row from a specific loaction of the database'))
        self.menu.append(self.menuitem)

        self.menuitem = Gtk.MenuItem()
        self.menuitem.add(make_menu_item('icons/16/delete_row.png', 'Delete row here', from_file=True))
        self.menuitem.connect('activate', lambda q: delete_row('delete-here'))
        self.menuitem.connect('select', lambda q: status_msg('Delete a row from the currently highlighted area'))
        self.menu.append(self.menuitem)

        self.separator = Gtk.SeparatorMenuItem()
        self.menu.append(self.separator)

        self.menuitem = Gtk.MenuItem()
        self.menuitem.add(make_menu_item('icons/16/insert_column.png',
                                         'Insert column at...', accel='Shift+Insert', from_file=True))
        self.menuitem.connect('activate', lambda q: add_column('insert-at'))
        self.menuitem.connect('select', lambda q: status_msg('Insert a column at a specific location of the database'))
        self.menuitem.add_accelerator('activate', self.MAINWINDOW.accelgroup, Gdk.keyval_from_name(
            "Insert"), Gdk.ModifierType.SHIFT_MASK, Gtk.AccelFlags.VISIBLE)
        self.menu.append(self.menuitem)

        self.menuitem = Gtk.MenuItem()
        self.menuitem.add(make_menu_item('icons/16/insert_column.png', 'Append column', from_file=True))
        self.menuitem.connect('activate', lambda q: add_column('append'))
        self.menuitem.connect('select', lambda q: status_msg('Insert a column at the end of the database'))
        self.menu.append(self.menuitem)

        self.menuitem = Gtk.MenuItem()
        self.menuitem.add(make_menu_item('icons/16/insert_column.png', 'Prepend column', from_file=True))
        self.menuitem.connect('activate', lambda q: add_column('prepend'))
        self.menuitem.connect('select', lambda q: status_msg('Insert a column at the beginning of the database'))
        self.menu.append(self.menuitem)

        self.separator = Gtk.SeparatorMenuItem()
        self.menu.append(self.separator)

        self.menuitem = Gtk.MenuItem()
        self.menuitem.add(make_menu_item('icons/16/delete_column.png',
                                         'Delete column at...', accel='Shift+Delete', from_file=True))
        self.menuitem.connect('activate', lambda q: delete_column('delete-at'))
        self.menuitem.connect('select', lambda q: status_msg('Delete a column from a specific location'))
        self.menuitem.add_accelerator('activate', self.MAINWINDOW.accelgroup, Gdk.keyval_from_name(
            "Delete"), Gdk.ModifierType.SHIFT_MASK, Gtk.AccelFlags.VISIBLE)
        self.menu.append(self.menuitem)

        self.menuitem = Gtk.MenuItem()
        self.menuitem.add(make_menu_item('icons/16/delete_column.png', 'Delete last column', from_file=True))
        self.menuitem.connect('activate', lambda q: delete_column('delete-last'))
        self.menuitem.connect('select', lambda q: status_msg('Delete the last column of the database'))
        self.menu.append(self.menuitem)

        self.menuitem = Gtk.MenuItem()
        self.menuitem.add(make_menu_item('icons/16/delete_column.png', 'Delete first column', from_file=True))
        self.menuitem.connect('activate', lambda q: delete_column('delete-first'))
        self.menuitem.connect('select', lambda q: status_msg('Delete the first column of the database'))
        self.menu.append(self.menuitem)

        self.menuitem = Gtk.MenuItem(label="_Help", use_underline=True)
        self.menubar.append(self.menuitem)
        self.menu = Gtk.Menu()
        self.menuitem.set_submenu(self.menu)

        self.menuitem = Gtk.MenuItem()
        self.menuitem.add(make_menu_item('help-contents', 'Help'))
        msg = "\tFull manual is in the process of creation.\nPlease refer to MANUAL.txt and README.txt files for help"
        self.menuitem.connect('activate', lambda q: display_dialog('info', msg))
        self.menuitem.connect('select', lambda q: status_msg('Check MANUAL.txt and README.txt for help'))
        self.menu.append(self.menuitem)

        self.menuitem = Gtk.MenuItem()
        self.menuitem.add(make_menu_item('help-about', 'About'))
        self.menuitem.connect('activate', lambda q: about_dialog())
        self.menuitem.connect('select', lambda q: status_msg('Information about the creator and licensing'))
        self.menu.append(self.menuitem)

        self.separator = Gtk.SeparatorMenuItem()
        self.menu.append(self.separator)

        self.menuitem = Gtk.MenuItem()
        self.menuitem.add(make_menu_item('accessories-dictionary', 'Donate'))
        self.menuitem.connect('activate', lambda q: webbrowser.open('http://damianch.eu.pn/index.html#donate'))
        self.menuitem.connect('select', lambda q: status_msg('Support Damian is his journey through college'))
        self.menu.append(self.menuitem)

    def item_activated(self, widget):
        """Recent menu launcher.

        (self, object) -> None

        Handler for the submenu. It launches the open_file() function.
        Recent menu gives the file path in the uri format.
        Split is used to remove the uri formating.
        """
        item_chosen = widget.get_current_item()
        if item_chosen:
            file_name = item_chosen.get_uri()
            file_name = file_name.split('file://')[-1]  # cut out the uri
            open_file(file_uri=file_name)  # open the file without a dialog


class MainToolbar(object):
    """Main Toolbar of the Window"""

    def __init__(self, MAINWINDOW):
        """Constructor of the Toolbar.

        (self, object) -> None

        :param MAINWINDOW: is the class instance of the main window.
        """
        self.MAINWINDOW = MAINWINDOW
        self.grid = Gtk.Grid()  # make a subgrid. it will hold the toolbar and the infobar
        self.toolbar = Gtk.Toolbar()
        self.toolbar.set_show_arrow(True)  # displat scrolling arrow if the window is too narrow
        self.toolbar.set_hexpand(True)
        self.MAINWINDOW.grid.attach(self.grid, 0, 1, 1, 1)  # attach to the main windows
        self.grid.attach(self.toolbar, 0, 0, 1, 1)  # attach the toolbar to the inner grid

        self.toolbutton = Gtk.ToolButton()
        self.toolbutton.set_icon_name('document-new')
        # self.toolbutton.set_is_important(True)  # prints also the label text
        self.toolbutton.set_tooltip_text('Create a new file')
        self.toolbutton.connect('clicked', lambda q: tab_control('new'))
        self.toolbar.add(self.toolbutton)

        self.toolbutton = Gtk.ToolButton()
        self.toolbutton.set_icon_name('document-open')
        self.toolbutton.set_tooltip_text('Open a file')
        self.toolbutton.connect('clicked', lambda q: open_file())
        self.toolbar.add(self.toolbutton)

        self.toolbutton = Gtk.ToolButton()
        self.toolbutton.set_icon_name('document-save')
        self.toolbutton.set_tooltip_text('Save a file')
        self.toolbutton.connect('clicked', lambda q: save_file())
        self.toolbar.add(self.toolbutton)

        self.separatortoolitem = Gtk.SeparatorToolItem()
        self.toolbar.add(self.separatortoolitem)

        self.menu = Gtk.Menu()
        self.menuitem = Gtk.MenuItem(label="Prepend row")
        self.menuitem.connect('activate', lambda q: add_row('prepend'))
        self.menu.append(self.menuitem)
        self.menuitem = Gtk.MenuItem(label="Insert row at...")
        self.menuitem.connect('activate', lambda q: add_row('insert-at'))
        self.menu.append(self.menuitem)
        self.menuitem = Gtk.MenuItem(label="Insert row here")
        self.menuitem.connect('activate', lambda q: add_row('insert-here'))
        self.menu.append(self.menuitem)
        self.menuitem = Gtk.MenuItem(label="Append row (Default)")
        self.menuitem.connect('activate', lambda q: add_row('append'))
        self.menu.append(self.menuitem)
        self.menu.show_all()

        self.icon_img = Gtk.Image()
        self.icon_img.set_from_file('icons/insert_row.png')
        self.toolbutton = Gtk.MenuToolButton(label='Insert Row')
        self.toolbutton.set_icon_widget(self.icon_img)
        self.toolbutton.set_tooltip_text('Insert Row')
        self.toolbutton.connect('clicked', lambda q: add_row('append'))
        self.toolbutton.set_menu(self.menu)
        self.toolbar.add(self.toolbutton)

        self.menu = Gtk.Menu()
        self.menuitem = Gtk.MenuItem(label="Delete first row")
        self.menuitem.connect('activate', lambda q: delete_row('delete-first'))
        self.menu.append(self.menuitem)
        self.menuitem = Gtk.MenuItem(label="Delete last row")
        self.menuitem.connect('activate', lambda q: delete_row('delete-last'))
        self.menu.append(self.menuitem)
        self.menuitem = Gtk.MenuItem(label="Delete row at...")
        self.menuitem.connect('activate', lambda q: delete_row('delete-at'))
        self.menu.append(self.menuitem)
        self.menuitem = Gtk.MenuItem(label="Delete row here (Default)")
        self.menuitem.connect('activate', lambda q: delete_row('delete-here'))
        self.menu.append(self.menuitem)
        self.menu.show_all()

        self.icon_img = Gtk.Image()
        self.icon_img.set_from_file('icons/delete_row.png')
        self.toolbutton = Gtk.MenuToolButton(label='Delete Row')
        self.toolbutton.set_icon_widget(self.icon_img)
        self.toolbutton.set_tooltip_text('Delete Row')
        self.toolbutton.connect('clicked', lambda q: delete_row('delete-here'))
        self.toolbutton.set_menu(self.menu)
        self.toolbar.add(self.toolbutton)

        self.separatortoolitem = Gtk.SeparatorToolItem()
        self.toolbar.add(self.separatortoolitem)

        self.menu = Gtk.Menu()
        self.menuitem = Gtk.MenuItem(label="Prepend column")
        self.menuitem.connect('activate', lambda q: add_column('prepend'))
        self.menu.append(self.menuitem)
        self.menuitem = Gtk.MenuItem(label="Insert column at...")
        self.menuitem.connect('activate', lambda q: add_column('insert-at'))
        self.menu.append(self.menuitem)
        self.menuitem = Gtk.MenuItem(label="Append (Default)")
        self.menuitem.connect('activate', lambda q: add_column('append'))
        self.menu.append(self.menuitem)
        self.menu.show_all()

        self.icon_img = Gtk.Image()
        self.icon_img.set_from_file('icons/insert_column.png')
        self.toolbutton = Gtk.MenuToolButton(label='Insert Column')
        self.toolbutton.set_icon_widget(self.icon_img)
        self.toolbutton.set_tooltip_text('Insert Column')
        self.toolbutton.connect('clicked', lambda q: add_column('append'))
        self.toolbutton.set_menu(self.menu)
        self.toolbar.add(self.toolbutton)

        self.menu = Gtk.Menu()
        self.menuitem = Gtk.MenuItem(label="Delete first column")
        self.menuitem.connect('activate', lambda q: delete_column('delete-first'))
        self.menu.append(self.menuitem)
        self.menuitem = Gtk.MenuItem(label="Delete column at...")
        self.menuitem.connect('activate', lambda q: delete_column('delete-at'))
        self.menu.append(self.menuitem)
        self.menuitem = Gtk.MenuItem(label="Delete last column (Default)")
        self.menuitem.connect('activate', lambda q: delete_column('delete-last'))
        self.menu.append(self.menuitem)
        self.menu.show_all()

        self.icon_img = Gtk.Image()
        self.icon_img.set_from_file('icons/delete_column.png')
        self.toolbutton = Gtk.MenuToolButton(label='Delete Column')
        self.toolbutton.set_icon_widget(self.icon_img)
        self.toolbutton.set_tooltip_text('Delete Column')
        self.toolbutton.connect('clicked', lambda q: delete_column('delete-last'))
        self.toolbutton.set_menu(self.menu)
        self.toolbar.add(self.toolbutton)

        self.separatortoolitem = Gtk.SeparatorToolItem()
        self.toolbar.add(self.separatortoolitem)

        self.icon_img = Gtk.Image()
        self.icon_img.set_from_file('icons/convert.png')
        self.toolbutton = Gtk.ToolButton(label='Convert a column')
        self.toolbutton.set_icon_widget(self.icon_img)
        self.toolbutton.set_tooltip_text('Convert Column')
        self.toolbutton.connect('clicked', lambda q: convert_column())
        self.toolbar.add(self.toolbutton)

        self.separatortoolitem = Gtk.SeparatorToolItem()
        self.toolbar.add(self.separatortoolitem)

        self.toolbutton = Gtk.ToolButton()
        self.toolbutton.set_icon_name('help-contents')
        self.toolbutton.set_tooltip_text('Help')
        msg = "\tFull manual is in the process of creation.\nPlease refer to MANUAL.txt and README.txt files for help"
        self.toolbutton.connect('clicked', lambda q: display_dialog('info', msg))
        self.toolbar.add(self.toolbutton)

        self.toolbutton = Gtk.ToolButton()
        self.toolbutton.set_icon_name('help-about')
        self.toolbutton.set_tooltip_text('About JDF Editor')
        self.toolbutton.connect('clicked', lambda q: about_dialog())
        self.toolbar.add(self.toolbutton)

    def push_message_infobar(self, signal, message_text):
        """Info bar.

        (self, str, str) -> None

        :param signal: is the type of coloured background that will be displayed on the infobar.
                       refer to the manual for a list of all the signal types.
        :param message_text: is the string containing the message to be displayed.

        Posts a message to the InfoBar. InfoBar is in the top right corner of the window.
        """
        if signal == 'info':  # info style background
            signal = Gtk.MessageType.INFO
        elif signal == 'warn':  # warning style background
            signal = Gtk.MessageType.WARNING
        elif signal == 'error':  # error style background
            signal = Gtk.MessageType.ERROR
        elif signal == 'quest':  # question style background
            signal = Gtk.MessageType.QUESTION
        infobar = Gtk.InfoBar()
        self.grid.attach(infobar, 1, 0, 1, 1)  # attach the infobar beside the toolbar
        infobar.add_button(Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE)
        infobar.set_default_response(Gtk.ResponseType.CLOSE)
        infobar.set_message_type(signal)
        infobar.connect("response", self.infobar_response)  # hide the bar if 'close' is clicked

        infobar_label = Gtk.Label(message_text)
        infobar_content = infobar.get_content_area()
        infobar_label.show()
        infobar_content.add(infobar_label)

        infobar.show()

    def infobar_response(self, infobar, respose_id):
        """Handler for the Info Bar.

        (self, object, object) -> None

        Hides the infobar if close is clicked inside the Info Bar.
        """
        infobar.hide()
        self.grid.remove_column(1)


class DataCells(object):
    """Data Cells hold all the information about the database"""

    def __init__(self, MAINWINDOW, file_name, list_of_records, header_types, header_names, position):
        """Constructor of the class

        (self, object, str, list, list, list, int) -> None

        :param MAINWINDOW: is the class instance of the main window.
        :param file_name: is the entire path of the filename
        :param list_of_records: is the entire database record (refer to documentation for the schema)
        :param header_types: is a list of strings containing the types of each of the columns
        :param header_names: is a list of strings containing the names of each of the columns
        :param position: is the current spot (index) occupied by the class within the windows

        This class is the main body of the cells displayed.
        Holds all the mechanisms of the cell edits and any associated manipulations.
        """
        self.MAINWINDOW = MAINWINDOW
        self.list_of_records = list_of_records
        self.header_types = header_types
        self.header_names = header_names
        self.file_edited = False  # becomes True is a modification occures within the database
        self.file_name = file_name
        self.position = position
        self.set_input_data()  # prepare the list for the table (give it field types str,float etc.)
        self.add_table()  # add the table to the window from the records (liststore)
        self.currently_selected_row = 0  # currently selected row (for copy,cut,paste purpose)
        self.selector = self.treeview.get_selection()   # allows for selections control (cut,copy,paste)
        # self.selector.set_mode(Gtk.SelectionMode.MULTIPLE)  # allow to select multiple rows
        self.selector.connect('changed', self.selector_changed)  # handler for the selector

    def set_input_data(self):
        """Prepare the Gtk.Liststore() for the Gtk.Treeview() class

        (self) -> None
        """
        # make the ListStore
        exec_string = 'int'
        for each in self.header_types:  # add the header names to the string
            exec_string += ', ' + each
        exec('self.liststore = Gtk.ListStore(' + exec_string + ')')  # execute the string
        # enumerate the records inputed to the class (add incremental numbers at index 0)
        for idx, val in enumerate(self.list_of_records):
            val.insert(0, idx)
        self.header_types.insert(0, 'int')   # add the first row as int
        self.header_names.insert(0, '#')   # add the first row's label as '#'
        for each in self.list_of_records:  # add the database to the table
            self.liststore.append(each)

        self.treeview = Gtk.TreeView(model=self.liststore)
        self.treeview.set_property('enable-grid-lines', Gtk.TreeViewGridLines(3))
        self.treeview.set_property('activate-on-single-click', True)
        self.set_tooltip_if_column_is_name()  # launche the method, set the tooltip (if possible)
        self.treeview.set_headers_clickable(True)

    def set_tooltip_if_column_is_name(self):
        """Find a column with 'name' inside of it

        (self) -> None

        Helps finding the right row. The row name gets displayed (not only the row's number).
        Helps especially with bigger databases.
        If the database has a column which containes the string 'name' then that column's data will be used to
        diplay tooltips when a mouse hovers over a row.
        Therefore, a good idea is to hava a column that has the string 'name' in it.
        """
        for idx, val in enumerate(self.header_names):   # set the tooltip column if one of the columns is called 'name'
            if 'name' in val.lower():
                self.treeview.set_property('tooltip-column', idx)
                break   # leave on the first found column tha has 'name' in its name

    def add_table(self):
        """Add the table to the window

        (self) -> None

        Sets the cells based on the type of input (str, float, int, bool).
        Wraps it all up and adds it to the window's tabs.
        """
        for each in range(len(self.list_of_records[0])):   # iterate through the list's columns
            if each == 0:       # the first column is special (doesn't expand)
                self.treeviewcolumn = Gtk.TreeViewColumn(self.header_names[each])
                self.treeviewcolumn.set_expand(False)
            else:
                self.treeviewcolumn = Gtk.TreeViewColumn(self.header_names[each] + ' - ' + self.header_types[each])
                self.treeviewcolumn.set_expand(True)
                self.treeviewcolumn.set_alignment(0.5)
            self.treeview.append_column(self.treeviewcolumn)  # add the column to the treeview
            self.treeviewcolumn.set_clickable(True)
            self.treeviewcolumn.set_resizable(True)
            # self.treeviewcolumn.set_sizing(Gtk.TreeViewColumnSizing(2)) # autosize
            self.treeviewcolumn.connect('clicked', self.column_clicked, each)  # handler for the header click
            if each == 0:   # first column has special settings (non-editable, set width, etc.)
                self.treeviewcolumn.set_min_width(40)
                self.treeviewcolumn.set_alignment(0.5)
                self.adjustment = Gtk.Adjustment(0, 0, 100000, 1, 1, 2)
                self.cellrendererspin = Gtk.CellRendererSpin()
                self.cellrendererspin.set_property("editable", False)
                self.cellrendererspin.set_property("adjustment", self.adjustment)
                self.cellrendererspin.set_property("digits", False)
                self.treeviewcolumn.pack_start(self.cellrendererspin, True)
                self.treeviewcolumn.add_attribute(self.cellrendererspin, "text", each)
            elif self.header_types[each] == 'str':  # if the column is of str type
                self.treeviewcolumn.set_min_width(90)
                self.cellrenderertext = Gtk.CellRendererText()   # text entry cell
                self.cellrenderertext.set_property("editable", True)  # is editable
                self.cellrenderertext.connect("edited", self.cell_edited_str, each)  # bind the handler to the cell
                self.treeviewcolumn.pack_start(self.cellrenderertext, True)   # add to the treeviewcolumn
                self.treeviewcolumn.add_attribute(self.cellrenderertext, "text", each)  # capture data from liststore
            elif self.header_types[each] == 'bool':  # if the column is of bool type
                self.treeviewcolumn.set_min_width(70)
                self.cellrenderertoggle = Gtk.CellRendererToggle()  # toggle type cell
                self.cellrenderertoggle.connect("toggled", self.cell_edited_bool, each)
                self.treeviewcolumn.pack_start(self.cellrenderertoggle, True)
                self.treeviewcolumn.add_attribute(self.cellrenderertoggle, "active", each)
            elif self.header_types[each] == 'float':  # if the column is of float type
                self.treeviewcolumn.set_min_width(110)
                self.adjustment = Gtk.Adjustment(0, -100000, 100000, 1, 1, 2)
                self.cellrendererspin = Gtk.CellRendererSpin()   # spin type cell (numbers)
                self.cellrendererspin.set_property("editable", True)
                self.cellrendererspin.set_property("adjustment", self.adjustment)
                self.cellrendererspin.set_property("digits", 6)   # display/edit with a 6 decimal place accuracy
                self.cellrendererspin.connect("edited", self.cell_edited_float, each)
                self.treeviewcolumn.pack_start(self.cellrendererspin, True)
                self.treeviewcolumn.add_attribute(self.cellrendererspin, "text", each)
            else:   # otherwise the column is an int type
                self.treeviewcolumn.set_min_width(80)
                self.adjustment = Gtk.Adjustment(0, -100000, 100000, 1, 1, 2)
                self.cellrendererspin = Gtk.CellRendererSpin()   # spin type cell (numbers)
                self.cellrendererspin.set_property("editable", True)
                self.cellrendererspin.set_property("adjustment", self.adjustment)
                self.cellrendererspin.set_property("digits", False)   # no decimal places
                self.cellrendererspin.connect("edited", self.cell_edited_int, each)
                self.treeviewcolumn.pack_start(self.cellrendererspin, True)
                self.treeviewcolumn.add_attribute(self.cellrendererspin, "text", each)

        self.scrolled_window = Gtk.ScrolledWindow()   # the database is inside a scrolled window
        self.scrolled_window.add(self.treeview)   # add the cells(treeview) to the scrolled window
        # self.scrolled_window.set_policy(Gtk.PolicyType.ALWAYS, Gtk.PolicyType.ALWAYS)
        self.scrolled_window.set_min_content_height(200)
        # self.scrolled_window.set_overlay_scrolling()
        self.scrolled_window.unset_placement()

        # make a box for the tabs' header
        self.notebook_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)

        filename_no_path = self.file_name.split(PATH_BREAK)[-1]  # extract just the filename (no path)
        self.notebook_label = Gtk.Label(label=filename_no_path)
        self.MAINWINDOW.post_filename_to_title(filename_no_path)  # post the filename to the title
        self.notebook_box.pack_start(self.notebook_label, False, False, 0)  # add the label to the box

        self.notebook_button = Gtk.Image()  # make a close button inside of the tab's header
        self.notebook_button.set_from_file('icons/close.png')

        self.eventbox = Gtk.EventBox()   # create a handler for the button(image)
        self.eventbox.connect("button-release-event", self.close_tab)
        self.eventbox.add(self.notebook_button)  # add the button to the handler

        self.notebook_box.pack_start(self.eventbox, False, False, 0)  # add the handler+image to the box

        self.notebook_box.show_all()

        # create an event box to handle right clicks inside of the database area
        # add the scrolled window(with the treeview inside) to the event box
        # then add that event box to the tab with the box(image+label) as the header of the tab
        self.eventbox = Gtk.EventBox()
        self.eventbox.connect("button-release-event", self.right_click_menu)
        self.eventbox.add(self.scrolled_window)
        self.MAINWINDOW.notebook_tabs.insert_page(self.eventbox, self.notebook_box, self.position)
        # if self.MAINWINDOW.notebook_tabs.get_n_pages() > 1:     # show tabs if there is more than one pane
        #     self.MAINWINDOW.notebook_tabs.set_show_tabs(True)
        # else:
        #     self.MAINWINDOW.notebook_tabs.set_show_tabs(False)

    def close_tab(self, widget, event):
        """Close tab handler.

        (self, object, object) -> None

        This method gets launched when the user clicks the close button on the tab.
        Which in a consequence launches the tab_control() function to close that tab.
        """
        if event.button == 1:  # left mouse button
            tab_control('close-from-class', self.file_name)

    def right_click_menu(self, widget, event):
        """Right click menu.

        (self, object, object) -> None

        Displays a right click contex menu if the user right clicks within the database area.
        """
        # current_focus = self.MAINWINDOW.window.get_focus()
        # if isinstance(current_focus, Gtk.TreeView):
        if event.button == 3:  # right mouse button
            self.MAINWINDOW.menu.popup(None, None, None, None, event.button, event.time)
            self.MAINWINDOW.menu.show_all()

    def column_clicked(self, widget, column_num):
        """Column header clicked.

        (self, object, int) -> None

        This method creates a Gtk.Entry() widget inside of the column's header.
        The user can then enter a new name for the column.
        """
        if column_num > 0:  # make sure that the first column is not affected
            text_inside = self.header_names[column_num]  # grab the current text of the column
            entry_widget = Gtk.Entry()   # make a widget
            entry_widget.set_text(text_inside)   # set the current text inside of the widget
            entry_widget.connect('activate', self.set_new_header_name, widget, column_num)  # when enter pressed
            entry_widget.connect('focus-out-event', self.set_new_header_name_f_out,
                                 widget, column_num)  # if focus changes
            widget.set_widget(entry_widget)  # replace the default header column widget
            entry_widget.show()
            entry_widget.grab_focus()  # set the focus to the entry widget

    def set_new_header_name_f_out(self, widget, something, column_widget, column_num):
        """Set a new name for the column's header.

        (self, object, object, object, int) -> None

        Sets a new name for the columns header.
        Displays a warning if the name already exists.
        """
        modified_header_text = widget.get_text()  # grab the text entered
        if modified_header_text in self.header_names:  # check if the name already exists
            infobar_msg('warn', 'This name already exists')
        else:
            self.header_names[column_num] = modified_header_text  # change the name within the class
            column_widget.set_title(modified_header_text)  # set the title in the column widget
            modified_header_text += ' - ' + self.header_types[column_num]  # add the column type to the text
            label = Gtk.Label(modified_header_text)  # make a label with the text
            column_widget.set_widget(label)  # set the label inside of the column's header
            label.show()
            self.notify_file_edited()   # notify that the file was edited
            status_msg('Column ' + str(column_num) + " name edited")   # post status
            self.set_tooltip_if_column_is_name()   # recheck the tooltip displays

    def set_new_header_name(self, widget, column_widget, column_num):
        """Enter pressed inside the entry widget, inside the column header.

        (self, object, object, int) -> None

        If an Enter key has been pressed this function simply creates a focus
        on the main cell display to automatically trigger set_new_header_name_f_out() method
        """
        self.treeview.grab_focus()  # automatically triggers focus out event trigger

    def cell_edited_str(self, cellrenderertext, path, text, column):
        """String cell edited handler.

        (self, object, str, str, int) -> None
        """
        status_msg('Edited Row: ' + str(path) + '  Col:' + str(column) + ' To ' + text)   # post edit to statusbar
        self.liststore[path][column] = text   # modify the data in the Gtk.Liststore()
        self.notify_file_edited()   # notify that the file has been edited

    def cell_edited_float(self, cellrendererspin, path, value, column):
        """Float cell edited handler.

        (self, object, str, str, int) -> None
        """
        status_msg('Edited Row: ' + str(path) + '  Col:' + str(column) + ' To ' + str(value))
        self.liststore[path][column] = float(value)   # convert the value to a float
        self.notify_file_edited()

    def cell_edited_int(self, cellrendererspin, path, value, column):
        """Integer cell edited handler.

        (self, object, str, str, int) -> None
        """
        status_msg('Edited Row: ' + str(path) + '  Col:' + str(column) + ' To ' + str(value))
        self.liststore[path][column] = int(value)  # convert the value to an integer
        self.notify_file_edited()

    def cell_edited_bool(self, cellrenderertoggle, path, column):
        """Bool cell edited handler.

        (self, object, str, int) -> None
        """
        self.liststore[path][column] = not self.liststore[path][column]  # reverse the cell (toggle)

    def selector_changed(self, widget):
        """Row highlighter.

        (self, object) -> None

        This method is used to post into the status bar the currently highlighted row.
        This technique is also used by the clipboard to retrieve the whole row's data.
        """
        current_row = str(widget.get_selected_rows()[1][0])  # get current row
        status_msg('Row: ' + current_row)    # post it to the statusbar
        self.currently_selected_row = int(current_row)   # change the class's argument

    def notify_file_edited(self):
        """Post the fact that a file has been edited.

        (self) -> None

        This method adds an asterisk in front of the file name one the tab and on the window title.
        """
        if not self.file_edited:   # if file has not been edited
            self.file_edited = True   # change the state to edited
            text = self.notebook_label.get_text()   # retrieve the filename from the notebook label
            self.notebook_label.set_text('* ' + text)   # add an asterisk in front of the name
            self.MAINWINDOW.post_filename_to_title('* ' + text)   # do the same with the window title


def make_menu_item(name, label_name, from_file=False, accel=None, size=1):
    """Creates a box with an image and a label.

    (str, str, bool, str, int) -> object

    :param name: icon-name or image path
    :param label_name: text to be placed inside of the label
    :param from_file: indicates that the 'name' variable is a path if set to True. Otherwise 'name' is the icon name.
    :param accel: text to be placed inside of the label of the accelerator used
    :param size: size of the image (only used if from_file is set to False)

    This function creates a Gtk.Image and a Gtk.Label.
    Packs them into a box a sends them back to be used in a Gtk.MenuItem(), usually.
    This function is used due to the fact that Gtk.ImageMenuItem() will be soon removed.
    """
    image = Gtk.Image()
    if from_file:
        image.set_from_file(name)
    else:
        image.set_from_icon_name(name, Gtk.IconSize.MENU)
    label = Gtk.Label(label_name)
    box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
    box.pack_start(image, False, False, 0)
    box.pack_start(label, False, False, 10)
    if accel is not None:   # don't add an accelerator if it hasn't been named
        accel_label = Gtk.Label(accel)
        box.pack_end(accel_label, False, False, 0)
    return box


def tab_control(signal, data=None):
    """Tab control function.

    (str, int) -> None

    :param signal: is a string type value that controls the behaviour of this function.
                   refer to the manual for a full list of signals.
    :param data: if necessary it holds the information (index numer) of a tab.

    This function controls all behaviours of the tabs.
    """
    global WINDOW, DATA  # capture the global cell data and the main window's info
    current_page = WINDOW.notebook_tabs.get_current_page()
    num_of_pages = WINDOW.notebook_tabs.get_n_pages()
    if signal == 'close':   # close tab signal
        short_filename = DATA[current_page].file_name.split(PATH_BREAK)[-1]   # short version of the current file path
        if data is None:  # if a specific tab has not been requested -->
            if num_of_pages == 1:   # if there is only one tab left -> check_before_quit()
                check_before_quit()
            else:
                if DATA[current_page].file_edited:   # check if the tab has edits
                    answer = display_dialog('warn',
                                            'You have unsaved changes\nAre you sure you want to close this tab?',
                                            choice=True)
                    if answer:    # close the tab if user is sure
                        WINDOW.notebook_tabs.remove_page(current_page)   # remove the tab
                        del DATA[current_page]   # delete the DataCells() instance from the global data
                        status_msg('Closed a tab with a file: ' + short_filename)   # post message
                else:
                    WINDOW.notebook_tabs.remove_page(current_page)
                    del DATA[current_page]
                    status_msg('Closed a tab with a file: ' + short_filename)
        else:   # specifi tab has been requested
            current_page = data
            if num_of_pages == 1:
                check_before_quit()
            else:
                if DATA[current_page].file_edited:
                    answer = display_dialog('warn',
                                            'You have unsaved changes\nAre you sure you want to close this tab?',
                                            choice=True)
                    if answer:
                        WINDOW.notebook_tabs.remove_page(current_page)
                        del DATA[current_page]
                        status_msg('Closed a tab with a file: ' + short_filename)
                else:
                    WINDOW.notebook_tabs.remove_page(current_page)
                    del DATA[current_page]
                    status_msg('Closed a tab with a file: ' + short_filename)

    elif signal == 'new':   # create a new blank table/tab
        build_blank_table()
        tab_control('switch-to-last')
    elif signal == 'next':  # switch to the next tab
        if current_page == num_of_pages - 1:
            WINDOW.notebook_tabs.set_current_page(0)  # go back to first (loop around)
        else:
            WINDOW.notebook_tabs.next_page()
    elif signal == 'previous':   # switch to the previous tab
        if current_page == 0:
            WINDOW.notebook_tabs.set_current_page(num_of_pages - 1)  # go to last (loop around)
        else:
            WINDOW.notebook_tabs.prev_page()
    elif signal == 'close-from-class':   # a DataCells() class has requested to be closed (user clicked x on the tab)
        if num_of_pages == 1:
            check_before_quit()
        else:
            # ---------------------------------------------------------------------------------------------------------
            # ---SECTION TO BE REMOVED AFTER DATACELLS NOTEBOOK DATA WILL BE MIGRATED TO THE WINDOW CLASS -------------
            # ---------------------------------------------------------------------------------------------------------
            # ---------------------------------------------------------------------------------------------------------
            for idx, each in enumerate(DATA):
                if each.file_name == data:    # find the page number that needs to be closed (by filename matching)
                    current_page = idx   # this method will be removed soon, once DataCells will be modified
                    break
            short_filename = DATA[current_page].file_name.split(PATH_BREAK)[-1]
            if DATA[current_page].file_edited:
                answer = display_dialog('warn',
                                        'You have unsaved changes\nAre you sure you want to close this tab?',
                                        choice=True)
                if answer:
                    WINDOW.notebook_tabs.remove_page(current_page)
                    del DATA[current_page]
            else:
                WINDOW.notebook_tabs.remove_page(current_page)
                del DATA[current_page]
            status_msg('Closed a tab with a file: ' + short_filename)
    elif signal == 'switched':   # tab switched (used to post the current tab name to the windows title)
        if len(DATA) != 0:
            current_filename = DATA[data].file_name.split(PATH_BREAK)[-1]
            if DATA[data].file_edited:
                current_filename = '* ' + current_filename
            WINDOW.post_filename_to_title(current_filename)
    elif signal == 'switch-to-last':  # switch to the last tab
        WINDOW.notebook_tabs.set_current_page(num_of_pages - 1)
    elif signal == 'switch-to-first':  # switch to the first tab
        WINDOW.notebook_tabs.set_current_page(0)
    elif signal == 'force-close':   # don't ask the user for permission, close a tab regardless of any unsaved changes
        short_filename = DATA[current_page].file_name.split(PATH_BREAK)[-1]
        if data is None:
            if num_of_pages == 1:
                check_before_quit()
            else:
                WINDOW.notebook_tabs.remove_page(current_page)
                del DATA[current_page]
                status_msg('Force closed a tab with a file: ' + short_filename)
        else:
            current_page = data
            if num_of_pages == 1:
                check_before_quit()
            else:
                WINDOW.notebook_tabs.remove_page(current_page)
                del DATA[current_page]
                status_msg('Force closed a tab with a file: ' + short_filename)


def add_column(signal):
    """Add a column.

    (str) -> None

    :param signal: is a string type value that controls the behaviour of this function.
                   refer to the manual for a full list of signals.

    This function adds a column with a specific name and type to the current database.
    """
    global WINDOW, DATA  # capture the window's and the databases' current data
    current_page = WINDOW.notebook_tabs.get_current_page()   # current tab (also position within global DATA)
    current_header_names = DATA[current_page].header_names[1:]  # chop off the first index (unused in the database)
    current_header_types = DATA[current_page].header_types[1:]  # chop off the first index (unused in the database)
    current_filename = DATA[current_page].file_name  # make a copy of the filename
    current_data = list()  # make a copy of the database
    for each in DATA[current_page].liststore:   # create a copy without the first index
        current_data.append(each[1:])
    if signal != 'insert-at':  # if the query is not for a particular column position
        column_name, column_type = dialog_ask('entry combo', 'Insert a column', 'Enter a name for the column:',
                                              combo_list=['str', 'int', 'float', 'bool'],
                                              combo_prompt='Choose a column type:')
    else:   # a column postion needs to be selected
        column_name, column_type, column_number = dialog_ask('entry combo sec num', 'Insert a column',
                                                             'Enter a name for the column:',
                                                             combo_list=['str', 'int', 'float', 'bool'],
                                                             combo_prompt='Choose a column type:',
                                                             sec_combo_list=current_header_names + ['Insert as last'],
                                                             sec_combo_prompt='Insert before...')
    if column_name is not None:   # if the user selected valid data  -->
        # add new data
        if signal == 'append':   # adds a column at the end of the database
            current_header_names.append(column_name)   # add the column name
            current_header_types.append(column_type)   # add the column type
            for each in current_data:   # insert default values based on the type of the column
                if column_type == 'str':
                    each.append('Empty Data')
                elif column_type == 'bool':
                    each.append(True)
                elif column_type == 'int' or column_type == 'float':
                    each.append(0)
            status_msg('Appended a column')
        elif signal == 'prepend':  # insert a column at the beginning of the database
            current_header_names.insert(0, column_name)
            current_header_types.insert(0, column_type)
            for each in current_data:
                if column_type == 'str':
                    each.insert(0, 'Empty Data')
                elif column_type == 'bool':
                    each.insert(0, True)
                elif column_type == 'int' or column_type == 'float':
                    each.insert(0, 0)
            status_msg('Prepended a column')
        elif signal == 'insert-at':   # insert a column at a user specified position
            current_header_names.insert(column_number, column_name)
            current_header_types.insert(column_number, column_type)
            for each in current_data:
                if column_type == 'str':
                    each.insert(column_number, 'Empty Data')
                elif column_type == 'bool':
                    each.insert(column_number, True)
                elif column_type == 'int' or column_type == 'float':
                    each.insert(column_number, 0)
            status_msg('Inserted a column at index ' + str(column_number))

        # build a new table
        build_table((current_header_names, current_header_types, current_data), current_filename, position=current_page)
        # move the tab to the currently build table
        WINDOW.notebook_tabs.set_current_page(current_page)
        # close the 'old' tab
        tab_control('force-close', data=current_page + 1)
        post_file_edited()   # file has been edited (post it)


def delete_column(signal):
    """Delete a column.

    (str) -> None

    :param signal: is a string type value that controls the behaviour of this function.
                   refer to the manual for a full list of signals.

    This function deletes a column from the database.
    """
    global WINDOW, DATA  # capture the window's and the databases' current data
    rows_columns = count_rows_columns()   # count the column and rows
    if rows_columns[1] == 1:   # if there is only one column left
        infobar_msg('error', "Last column cannot be deleted")   # post an error and skip the deletion process
    else:
        column_to_delete = -1
        current_page = WINDOW.notebook_tabs.get_current_page()  # current tab (also position within global DATA)
        current_header_names = DATA[current_page].header_names[1:]  # chop off the first index (unused in the database)
        current_header_types = DATA[current_page].header_types[1:]  # chop off the first index (unused in the database)
        current_filename = DATA[current_page].file_name  # make a copy of the filename
        current_data = list()  # make a copy of the database
        for each in DATA[current_page].liststore:   # create a copy without the first index
            current_data.append(each[1:])
        # add new data
        if signal == 'delete-first':  # delete first column
            column_to_delete = 0   # index number 0
        elif signal == 'delete-last':  # delete last column
            column_to_delete = -1  # index -1
        elif signal == 'delete-at':  # delete a user chosen column , ask which one
            column_to_delete = dialog_ask('sec num', 'Delete column at...', '',
                                          sec_combo_list=current_header_names, sec_combo_prompt='Select a column')
            column_to_delete = column_to_delete[0]   # retrieve the column from the dialog
        # delete data
        if column_to_delete is not None:   # if the user has chosen a valid data -->
            del current_header_names[column_to_delete]  # delete a header
            del current_header_types[column_to_delete]  # delete a type
            for each in current_data:  # delete column from the database
                del each[column_to_delete]
            # build a new table
            build_table((current_header_names, current_header_types, current_data),
                        current_filename, position=current_page)
            # move the tab to the currently build table
            WINDOW.notebook_tabs.set_current_page(current_page)
            status_msg('Deleted a column at index ' + str(column_to_delete))
            # close the 'old' tab
            tab_control('force-close', data=current_page + 1)
            post_file_edited()   # file has been edited (post it)


def convert_column():
    """Convert a column

    (None) -> None

    This function converts the data type of a column.
    It converts the values to their neatest possible outcomes.
    Converting a float 1.1 to an integer, will have an output of 1.
    """
    global WINDOW, DATA  # capture the window's and the databases' current data
    infobar_msg('warn', "\tWARNING!\nConverting a column may cause\nthat column's data loss")
    current_page = WINDOW.notebook_tabs.get_current_page()  # current tab (also position within global DATA)
    current_header_names = DATA[current_page].header_names[1:]  # chop off the first index (unused in the database)
    current_header_types = DATA[current_page].header_types[1:]  # chop off the first index (unused in the database)
    current_filename = DATA[current_page].file_name  # make a copy of the filename
    current_data = list()  # make a copy of the database
    for each in DATA[current_page].liststore:   # create a copy without the first index
        current_data.append(each[1:])
    list_of_types = ['str', 'int', 'float', 'bool']   # create a list of valid types
    text_prompt = 'Values will be converted\nto their nearest possible outcomes\n\nSelect a column'
    # ask which column to convert and to which type
    column_to_convert, convert_to = dialog_ask('combo sec', 'Convert a column', '',
                                               combo_list=current_header_names,
                                               combo_prompt=text_prompt,
                                               sec_combo_list=list_of_types,
                                               sec_combo_prompt='Convert to...')
    if column_to_convert is not None:  # if the user chose a valid input
        index_of_choice = current_header_names.index(column_to_convert)   # pick the index of the user's choice
        for each in current_data:
            if convert_to == 'bool':  # anything can be converted to a bool -->
                each[index_of_choice] = bool(each[index_of_choice])
            elif convert_to == 'int':  # anything can be converted to an integer, apart from a string (mostly :) )
                if current_header_types[index_of_choice] == 'str':
                    each[index_of_choice] = 0
                else:
                    each[index_of_choice] = int(each[index_of_choice])
            elif convert_to == 'str':   # anything can be converted to a string
                each[index_of_choice] = str(each[index_of_choice])
            elif convert_to == 'float':   # anything can be converted to a float, apart from a string (mostly :) )
                if current_header_types[index_of_choice] == 'str':
                    each[index_of_choice] = 0
                else:
                    each[index_of_choice] = float(each[index_of_choice])

        current_header_types[index_of_choice] = convert_to  # set a new type in the header
        # rebuild the table
        build_table((current_header_names, current_header_types, current_data), current_filename)
        # set the current tab
        WINDOW.notebook_tabs.set_current_page(len(DATA) - 1)
        status_msg('Converted a column at index ' + str(index_of_choice) + ' to type ' + convert_to)
        # delete the 'old' tab
        tab_control('force-close', data=current_page)
        post_file_edited()  # post that the file has been edited


def add_row(signal):
    """Add a row.

    (str) -> None

    :param signal: is a string type value that controls the behaviour of this function.
                   refer to the manual for a full list of signals.

    This function adds a row to the current database.
    """
    global WINDOW, DATA  # capture the window's and the databases' current data
    current_page = WINDOW.notebook_tabs.get_current_page()   # set the current page
    empty_list = list()   # make an empty list for the row
    # iterate through the column types and add their default values to the blank list
    for each in DATA[current_page].header_types:
        if each == 'str':
            empty_list.append('')
        elif each == 'int':
            empty_list.append(0)
        elif each == 'float':
            empty_list.append(0.0)
        elif each == 'bool':
            empty_list.append(False)
    # add the next highest number to the index (this is the '#' column, basically)
    empty_list[0] = DATA[current_page].liststore[-1][0] + 1
    if signal == 'prepend':   # add the row at the beginnig of the database
        DATA[current_page].liststore.prepend(empty_list)
        status_msg('Prepended a row')
    elif signal == 'append':   # add the row at the end of the database
        DATA[current_page].liststore.append(empty_list)
        status_msg('Appended a row')
    elif signal == 'insert-at':   # at the row at the location specified by the user
        list_of_rows = list()   # check how many rows are there
        list_of_rows = [str(each[0]) for each in DATA[current_page].liststore]  # convert row numbers to strings
        selected_row = dialog_ask('sec num', 'Add row at...', '',
                                  sec_combo_list=list_of_rows, sec_combo_prompt='Select a row')
        selected_row = selected_row[0]   # pick the user chosen row
        if selected_row is not None:   # if the user picked a valid choice
            DATA[current_page].liststore.insert(selected_row, empty_list)
            status_msg('Inserted a row at index ' + str(selected_row))
    elif signal == 'insert-here':   # insert the row at the currently highlighted row
        selected_row = DATA[current_page].currently_selected_row + 1
        DATA[current_page].liststore.insert(selected_row, empty_list)
        status_msg('Inserted a row at index ' + str(selected_row))
    fix_row_indices()   # repair row indices (if the numbering is not 0,1,2,3,4...)
    post_file_edited()  # post that the file has been edited


def delete_row(signal):
    """Delete a row.

    (str) -> None

    :param signal: is a string type value that controls the behaviour of this function.
                   refer to the manual for a full list of signals.

    Delete a row from the database.
    """
    global WINDOW, DATA  # capture the window's and the databases' current data
    rows_columns = count_rows_columns()   # count the rows and columns
    if rows_columns[0] == 1:   # don't allow to delete the last row
        infobar_msg('error', "Last row cannot be deleted")
    else:
        row_num = 0
        current_page = WINDOW.notebook_tabs.get_current_page()
        if signal == 'delete-first':   # delete the first row
            row_num = 0   # index 0
        elif signal == 'delete-last':   # delete the last row
            row_num = rows_columns[0] - 1   # delete the last row
        elif signal == 'delete-at':   # delete a row at the user's specified location
            list_of_rows = list()
            list_of_rows = [str(each[0]) for each in DATA[current_page].liststore]  # convert row numbers to strings
            row_num = dialog_ask('sec num', 'Delete row at...', '',
                                 sec_combo_list=list_of_rows, sec_combo_prompt='Select a row')
            row_num = row_num[0]   # pick the user chosen row
        elif signal == 'delete-here':  # delete the row currently highlighted
            row_num = DATA[current_page].currently_selected_row
        if row_num is not None:   # if the row number is valid
            # get the iterator (otherwise cannot remove a row from Gtk.ListStore()...wtf...)
            to_remove = DATA[current_page].liststore.get_iter(row_num)
            DATA[current_page].liststore.remove(to_remove)   # remove the row from the liststore
            status_msg('Deleted a row at index ' + str(row_num))  # post satus
            fix_row_indices()   # repair row indices (if the numbering is not 0,1,2,3,4...)
            post_file_edited()  # post that the file has been edited


def build_blank_table(position=-1):
    """Build a blank table

    (int) -> None

    Builds a blank table in a new tab. By default it builds a row with columns: Name and E-Mail.
    """
    global WINDOW, DATA, UNTITLED_FILE_COUNT  # capture the window's and the databases' current data, and file count
    if position == -1:  # set the position to zero if it is the first tab
        if len(DATA) == 0:
            position = 0
        else:   # otherwise make the position as the last index
            position = WINDOW.notebook_tabs.get_n_pages()
    file_name = 'Untitled' + str(UNTITLED_FILE_COUNT) + '.jdf'   # set the filename
    UNTITLED_FILE_COUNT += 1   # increase the number of the untitled counter
    header_name = ['Name', 'E-Mail']
    header_types = ['str', 'str']
    sample_data = [["John Smith", "j.smith@email.com"]]
    # instantiate the DataCells Class at a given position
    DATA.insert(position, DataCells(WINDOW, file_name, sample_data, header_types, header_name, position))
    # make sure that all is displayed
    WINDOW.window.show_all()


def build_table(database, file_name, position=-1):
    """short_description

    (list, str, int) -> None

    :param database: is the data of the entire database.
                     index 0: are headers
                     index 1: are header types
                     index 2: is the data of the whole database
    :param  file_name: database's file path
    :param position: index in which the database will be Inserted

    This function creates a database out of the provided information. Instantiates the class and inserts it to
    the global DATA list and also inserts that Class into a window tab.
    """
    global WINDOW, DATA  # capture the window's and the databases' current data
    if position == -1:   # if the position is unspecified, create the page as the last one
        position = WINDOW.notebook_tabs.get_n_pages()
    header_name = database[0]   # grab the header names
    header_types = database[1]   # grab the header types
    table_data = database[2]   # data of the whole database
    # instantiate the DataCells Class at a given position
    DATA.insert(position, DataCells(WINDOW, file_name, table_data, header_types, header_name, position))
    # make sure that all is displayed
    WINDOW.window.show_all()


def open_file(file_uri=None):
    """Open file dialog.

    (str) -> None

    :param file_uri: path to the file. display a dialog if this variable is unspecified.
    otherwise open the file without a prompt.

    This function displays a dialog to open a database file. If a valid path is inserted the dialog will not appear.
    The file will be opened instantly.
    """
    global WINDOW, DATA  # capture the window's and the databases' current data
    if file_uri is None:   # File path not specified
        filechooserdialog = Gtk.FileChooserDialog(title="Open File", buttons=(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        filechooserdialog.set_transient_for(WINDOW.window)   # set the parent window (displays the dialog centered)
        filefilter = Gtk.FileFilter()   # set the valid files filter
        filefilter.set_name("Database")
        filefilter.add_pattern("*.jdf")
        filefilter.add_pattern("*.sql")
        filechooserdialog.add_filter(filefilter)
        filefilter = Gtk.FileFilter()
        filefilter.set_name("All File types")
        filefilter.add_pattern("*")
        filechooserdialog.add_filter(filefilter)

        response = filechooserdialog.run()

        if response == Gtk.ResponseType.OK:   # if ok is clicked
            opened_file = filechooserdialog.get_filename()   # capture the file from the dialog
            file_no_path = opened_file.split(PATH_BREAK)[-1]  # make a short file version as well
            for each in DATA:   # check if file is already opened, if it is -->
                if opened_file == each.file_name:
                    filechooserdialog.destroy()
                    infobar_msg('warn', file_no_path + '\nIs already open')
                    status_msg(file_no_path + ' is already open')
                    return
            # otherwise open the file using the jdf_lib library
            loaded_data = jdf_lib.load_database(opened_file)
            if loaded_data == -1:   # if an error occured while opening the file -->
                filechooserdialog.destroy()
                msg = 'Error while loading file:\n' + file_no_path + '\n\nCorrupted or invalid'
                display_dialog('warn', msg)
                status_msg('Error while loading: ' + opened_file)
            else:  # otherwise build a new table (instance of the database)
                build_table(loaded_data, opened_file)
                status_msg('Opened: ' + file_no_path)
                filechooserdialog.destroy()
                tab_control('switch-to-last')
        else:
            filechooserdialog.destroy()  # close the window
    else:
        opened_file = file_uri
        file_no_path = opened_file.split(PATH_BREAK)[-1]
        for each in DATA:  # check if file already exists
            if opened_file == each.file_name:
                infobar_msg('warn', file_no_path + '\nIs already open')
                status_msg(file_no_path + ' is already open')
                return
        loaded_data = jdf_lib.load_database(opened_file)
        if loaded_data == -1:
            msg = 'Error while loading file:\n' + file_no_path + '\n\nCorrupted or invalid'
            display_dialog('warn', msg)
            status_msg('Error while loading: ' + opened_file)
        else:
            build_table(loaded_data, opened_file)
            status_msg('Opened: ' + file_no_path)
            tab_control('switch-to-last')


def save_file(force_dialog=False):
    """Save file dialog.

    (bool) -> None

    :param force_dialog: True or False. When set to True a dialog will appear (Used for Save As...)

    This function displays a save file dialog. If the file is already opened it will autosave it, unless the
    force_dialog variable is set to True.
    """
    global WINDOW, DATA  # capture the window's and the databases' current data
    current_page = WINDOW.notebook_tabs.get_current_page()  # grab the current tab
    copy_of_data = list()  # make a data copy
    for each in DATA[current_page].liststore:   # create a copy without the first index
        copy_of_data.append(each[1:])

    # if the file has a path and is not force_dialog'ed then autosave it. A database created within the editor
    # one with the Untitled* name will not have a path and therefore will not have a '/'  or '\' (in Windows OS)
    if PATH_BREAK in DATA[current_page].file_name and not force_dialog:
        file_name_to_save = DATA[current_page].file_name   # grab the whole file path
        # use the jdf_lib to dump the database into a file (first indices are skipped, they are only informal)
        jdf_lib.save_database(file_name_to_save, DATA[current_page].header_names[1:],
                              DATA[current_page].header_types[1:], copy_of_data)
        file_name = file_name_to_save.split(PATH_BREAK)[-1]   # grab just the file name out of the path
        status_msg('File saved: ' + file_name)
        DATA[current_page].notebook_label.set_text(file_name)   # set label text in notebook (removes the asterisk)
        DATA[current_page].file_edited = False   # reset that the file has been edited
        WINDOW.post_filename_to_title(file_name)   # post the filename to the title (removes the asterisk)
    else:  # display the dialog
        filechooserdialog = Gtk.FileChooserDialog('Save File', buttons=(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
        filechooserdialog.set_action(Gtk.FileChooserAction.SAVE)  # save type dialog
        filechooserdialog.set_do_overwrite_confirmation(True)  # confirm overwrites
        filechooserdialog.set_current_name(DATA[current_page].file_name)   # preset the current name
        filechooserdialog.set_create_folders(True)
        filechooserdialog.set_transient_for(WINDOW.window)   # set parent windows (centers the dialog within)

        filefilter = Gtk.FileFilter()  # set filters for databases only
        filefilter.set_name("Database")
        filefilter.add_pattern("*.jdf")
        filefilter.add_pattern("*.sql")
        filechooserdialog.add_filter(filefilter)
        filefilter = Gtk.FileFilter()
        filefilter.set_name("All File types")
        filefilter.add_pattern("*")
        filechooserdialog.add_filter(filefilter)

        response = filechooserdialog.run()

        if response == Gtk.ResponseType.OK:
            file_name_to_save = filechooserdialog.get_filename()
            jdf_lib.save_database(file_name_to_save, DATA[current_page].header_names[1:],
                                  DATA[current_page].header_types[1:], copy_of_data)
            file_name = file_name_to_save.split(PATH_BREAK)[-1]
            status_msg('File saved: ' + file_name)
            DATA[current_page].notebook_label.set_text(file_name)
            DATA[current_page].file_edited = False
            WINDOW.post_filename_to_title(file_name)

        filechooserdialog.destroy()  # remove the dialog


def export_to_html():
    """Export to html.

    (bool) -> None

    This function displays a html save file dialog.
    """
    global WINDOW, DATA  # capture the window's and the databases' current data
    current_page = WINDOW.notebook_tabs.get_current_page()  # grab the current tab
    copy_of_data = list()  # make a data copy
    for each in DATA[current_page].liststore:   # create a copy without the first index
        copy_of_data.append(each[1:])

    # display the dialog
    html_name = DATA[current_page].file_name.split('.')[0]
    html_name += '.html'
    just_filename = DATA[current_page].file_name.split(PATH_BREAK)[-1]
    filechooserdialog = Gtk.FileChooserDialog('Export as HTML...', buttons=(
        Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
    filechooserdialog.set_action(Gtk.FileChooserAction.SAVE)  # save type dialog
    filechooserdialog.set_do_overwrite_confirmation(True)  # confirm overwrites
    filechooserdialog.set_current_name(html_name)   # preset the current name
    filechooserdialog.set_create_folders(True)
    filechooserdialog.set_transient_for(WINDOW.window)   # set parent windows (centers the dialog within)

    filefilter = Gtk.FileFilter()  # set filters for databases only
    filefilter.set_name("HTML file")
    filefilter.add_pattern("*.html")
    filechooserdialog.add_filter(filefilter)

    response = filechooserdialog.run()

    if response == Gtk.ResponseType.OK:
        file_name_to_save = filechooserdialog.get_filename()

        export_html.build_html(just_filename,
                               file_name_to_save,
                               DATA[current_page].header_names[1:],
                               DATA[current_page].header_types[1:],
                               copy_of_data,
                               'JDFeditor ' + VERSION)
        status_msg('File exported: ' + file_name_to_save)

    filechooserdialog.destroy()  # remove the dialog


def exit_n_save(widget, dialog):
    """Enter pressed in the Gtk.Entry()

    (object, object) -> None
    """
    dialog.response(Gtk.ResponseType.OK)   # return OK response if enter was pressed


def dialog_ask(signal, dialog_name, prompt, combo_list=None, combo_prompt='', sec_combo_list=None, sec_combo_prompt=''):
    """Display a dialog that requires user action.

    (str, str, str, list, str, list, str) -> None

    :param signal: is a string type value that controls the behaviour of this function.
            refer to the manual for a full list of signals.
    :param dialog_name: title of the dialog.
    :param prompt: text that will be displayed above the text entry box.
    :param combo_list: a list of entries for the combobox.
    :param combo_prompt:  text that will be displayed above the combobox.
    :param combo_list: a list of entries for the secondary combobox.
    :param combo_prompt:  text that will be displayed above the secondary combobox.

    This is a rather versatile dialog box. It can display a Gtk.Entry() and two Gtk.ComboBox()-es.
    How many will be displayed is controlled by the signal variable. The first combobox return the value selected
    as is (str value). The second combobox has the ability to return an int (add 'num' to the signal), which represents
    the index value of the choice from the combobox.
    """
    global WINDOW  # capture the window's current data
    dialog = Gtk.Dialog(title=dialog_name, buttons=(
        Gtk.STOCK_OK, Gtk.ResponseType.OK, Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
    content_area = dialog.get_content_area()  # grab the dialog's content area. more content will be added to it
    dialog.set_transient_for(WINDOW.window)  # set the parent window (centers the dialog)
    output = list()   # set the output list
    if 'entry' in signal:  # creates a Gtk.Entry() inside the dialog
        label = Gtk.Label(prompt)
        label.set_padding(10, 10)
        label.set_justify(Gtk.Justification.CENTER)
        content_area.add(label)  # add the label to the dialog
        label.show()
        entry = Gtk.Entry()
        entry.connect('activate', exit_n_save, dialog)
        content_area.add(entry)  # add the entry box to the dialog
        entry.show()
    if 'combo' in signal:  # creates a Gtk.ComboBox() inside the dialog
        liststore = Gtk.ListStore(str)  # create a list for the combobox
        for each in combo_list:
            liststore.append([each])
        label = Gtk.Label(combo_prompt)
        label.set_padding(10, 10)
        label.set_justify(Gtk.Justification.CENTER)
        content_area.add(label)
        label.show()
        combobox = Gtk.ComboBox(model=liststore)   # set the list for the combobox
        combobox.set_active(0)  # set the first entry by default
        content_area.add(combobox)
        combobox.show()
        cellrenderertext = Gtk.CellRendererText()
        combobox.pack_start(cellrenderertext, True)
        combobox.add_attribute(cellrenderertext, "text", 0)
    if 'sec' in signal:  # creates a secondary Gtk.ComboBox() inside the dialog
        sec_liststore = Gtk.ListStore(str)
        for each in sec_combo_list:
            sec_liststore.append([each])
        label = Gtk.Label(sec_combo_prompt)
        label.set_padding(10, 10)
        label.set_justify(Gtk.Justification.CENTER)
        content_area.add(label)
        label.show()
        sec_combobox = Gtk.ComboBox(model=sec_liststore)
        sec_combobox.set_active(0)
        content_area.add(sec_combobox)
        sec_combobox.show()
        sec_cellrenderertext = Gtk.CellRendererText()
        sec_combobox.pack_start(sec_cellrenderertext, True)
        sec_combobox.add_attribute(sec_cellrenderertext, "text", 0)

    response = dialog.run()

    if 'entry' in signal:   # add the entry box string to the output
        text_inserted = entry.get_text()
        output.append(text_inserted)
    if 'combo' in signal:   # add the combo box string to the output
        selected_combo_box = combobox.get_active()
        output.append(combo_list[selected_combo_box])
    if 'sec' in signal:   # add the combo box string to the output
        sec_selected_combo_box = sec_combobox.get_active()
        if 'num' in signal:   # add an int instead (index value of the choice)
            output.append(sec_selected_combo_box)
        else:
            output.append(sec_combo_list[sec_selected_combo_box])
    if response == Gtk.ResponseType.OK:
        dialog.destroy()   # destroy the dialog and return the output
        return output
    else:   # cancel and return  a list with None values
        dialog.destroy()
        return_empty_list = list()
        return_empty_list = [None for each in output]
        return return_empty_list


def pasted_text(widget, text):
    """Capture the data inside of the clipboard.

    (object, str) -> None
    """
    global TEMP_CLIPBOARD  # capture the data in the global temporary clipboard
    TEMP_CLIPBOARD = text   # set the TEMP_CLIPBOARD to the value of the clipboard


def clipboard_manager(signal):
    """Clipboard manager.

    (str) -> None

    :param signal: is a string type value that controls the behaviour of this function.
                   refer to the manual for a full list of signals.

    This function is a handler for any clipboard type opertions: Cut, Copy, Paste.
    It changes its behaviour based on the highlighted area (whole row, just a cell)
    """
    global WINDOW, DATA, TEMP_CLIPBOARD  # capture the window's and the databases' current data, and temporary clipboard
    current_page = WINDOW.notebook_tabs.get_current_page()  # grab the current page
    current_row = DATA[current_page].currently_selected_row  # grab the currently selected row
    current_focus = WINDOW.window.get_focus()   # check the currently focused item  (row or cell?)
    if signal == 'copy':   # copy to clipboard
        if isinstance(current_focus, Gtk.TreeView):   # check if the focus is on the cell or the row
            temp_data = list(DATA[current_page].liststore[current_row])   # grab the row's data
            temp_data = str(temp_data)   # convert the list to a string
            WINDOW.clipboard.set_text(temp_data, -1)   # copy data to the clipboard
            status_msg('Row data copied to clipboard from index ' + str(current_row))   # post status
        else:
            current_focus.copy_clipboard()   # copy a singular sell to clipboard
            status_msg('Data copied to clipboard')   # post status
    elif signal == 'paste':   # past data from the clipboard
        if isinstance(current_focus, Gtk.TreeView):   # if the current selection is a row
            WINDOW.clipboard.request_text(pasted_text)  # get the text from the clipboard
            try:
                rows_columns = count_rows_columns()   # grab the amount of rows and columns
                exec('temp_list = ' + TEMP_CLIPBOARD)   # asignt the clipboard content(str) into a list
                if rows_columns[1] == len(temp_list):   # if the amount of columns match the length in the database -->
                    DATA[current_page].liststore[current_row] = temp_list
                    status_msg('Row data pasted at ' + str(current_row))   # post
                    fix_row_indices()
                    post_file_edited()
                else:
                    raise(Exception)  # error (incorrect input data or incorrect length)
            except Exception:
                status_msg('Incorrect data in the clipboard to paste in as a row')
        else:
            current_focus.paste_clipboard()   # paste into a cell
            status_msg('Data pasted')
            post_file_edited()   # post that a file has been edited
    elif signal == 'cut':   # cut out of the cell/row an put data into the clipboard
        if isinstance(current_focus, Gtk.TreeView):   # if the current selection is a row
            temp_data = list(DATA[current_page].liststore[current_row])   # grab the row's data
            temp_data = str(temp_data)   # convert the list to a string
            status_msg('Row cut to clipboard from index: ' + str(current_row))
            WINDOW.clipboard.set_text(temp_data, -1)   # put the data into the clipboard
            delete_row('delete-here')   # delete the currently highlighted row (cut)
        else:   # current selection is a cell
            current_focus.cut_clipboard()   # cut out the information from the cell
            if isinstance(current_focus, Gtk.SpinButton):
                current_focus.set_text('0')   # leave behind a zero if it was a number type cell
            else:
                current_focus.set_text('')  # leave behind an empty string if the call was a text type cell
            status_msg('Data cut to clipboard')   # post to statusbar
            post_file_edited()   # post that a file has been edited


def post_file_edited():
    """Post that a file as been edited

    (None) -> None

    Function made for conveniance. Adds an asterisk to the tab and the window's title that. Indicates that a file
    has been modified.
    """
    global WINDOW, DATA  # capture the window's and the databases' current data
    current_page = WINDOW.notebook_tabs.get_current_page()   # grab the current page
    DATA[current_page].notify_file_edited()   # call the class' notify_file_edited() method


def fix_row_indices():
    """Fix row indices.

    (None) -> None

    Iterates through the whole database and makes sure that the rows have the following numbering (0,1,2,3,4.....)
    """
    global WINDOW, DATA  # capture the window's and the databases' current data
    current_page = WINDOW.notebook_tabs.get_current_page()
    for idx, val in enumerate(DATA[current_page].liststore):   # use enumerate to generate the numbers
        DATA[current_page].liststore[idx][0] = idx   # set the index values to the rows


def display_dialog(signal, prompt, choice=False):
    """Display a quick dialog

    (str, str, bool) -> bool

    :param signal: is a string type value that controls the behaviour of this function.
                   refer to the manual for a full list of signals.
    :param prompt: text to be displayed in the dialog box
    :param choice: force the user to select OK/CANCEL

    Displays a simple informational dialog. Offers no user choice unless choice variable is set to True.
    """
    global WINDOW  # capture the window's current data
    if choice:   # create ok/cancel button if needed
        options = (Gtk.STOCK_OK, Gtk.ResponseType.OK, Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
    else:   # otherwise just an OK button
        options = Gtk.ButtonsType.OK
    if signal == 'warn':   # put a warning icon in the dialog
        msg_format = Gtk.MessageType.WARNING
    elif signal == 'info':   # put a information icon in the dialog
        msg_format = Gtk.MessageType.INFO
    elif signal == 'error':   # put a error icon in the dialog
        msg_format = Gtk.MessageType.ERROR
    elif signal == 'quest':   # put a question icon in the dialog
        msg_format = Gtk.MessageType.QUESTION
    msg_dialog = Gtk.MessageDialog(message_format=prompt, buttons=options)
    msg_dialog.set_transient_for(WINDOW.window)   # set the parent window
    msg_dialog.set_property("message-type", msg_format)
    response = msg_dialog.run()
    if choice:   # return either True or False, depending on the user's action
        if response == Gtk.ResponseType.OK:
            msg_dialog.destroy()
            return True
        else:
            msg_dialog.destroy()
            return False
    msg_dialog.destroy()


def count_rows_columns():
    """Count rows and column.

    (None) -> tuple

    Counts the amount of rows and columns in the current tab. Returns it as a tuple of (rows, columns).
    """
    global WINDOW, DATA  # capture the window's and the databases' current data
    current_page = WINDOW.notebook_tabs.get_current_page()
    rows, columns = 0, 0
    for each in DATA[current_page].liststore:
        rows += 1
    for each in DATA[current_page].liststore[0]:
        columns += 1
    return rows, columns


def check_before_quit():
    """Check for unsaved changes

    (None) -> bool

    This function iterates through all the tabs and checks if there are any unsaved changes.
    Posts a dialog to check is the user is sure to leave unsaved changes behind.
    """
    global DATA, WINDOW  # capture the window's and the databases' current data
    modified_files = False   # set the variable
    for each in DATA:
        if each.file_edited:
            modified_files = True
            break   # found an unsaved change
    if modified_files:
        answer = display_dialog('warn', 'You have unsaved changes\nAre you sure you want to Quit?', choice=True)
        if answer:
            Gtk.main_quit()   # quit
        else:
            return True   # stay in the program
    else:
        Gtk.main_quit()


def test_func():
    """Tester function
    """
    pass
    # global WINDOW, DATA, TOOLBAR
    # current_page = WINDOW.notebook_tabs.get_current_page()
    # data = WINDOW.notebook_tabs.get_nth_page(current_page)
    # content_of_event = data.get_child()
    # print data, content_of_event
    # data.remove(content_of_event)
    # label = Gtk.Label('Dupsko')
    # data.add(label)
    # label.show()


def status_msg(message):
    """Post a status bar message.

    (str) -> None

    :param message: string input that will be pushed into the statusbar of the window

    This function is a conveniance function that post a given text into the window's statusbar.
    """
    global WINDOW  # capture the window's current data
    WINDOW.push_message(message)   # launch the window's push_message() method


def infobar_msg(signal, msg_txt):
    """Post a status bar message.

    (str) -> None

    :param signal: is a string type value that controls the behaviour of this function.
                   refer to the manual for a full list of signals.
    :param msg_txt: string input that will be pushed into the infobar of the window
    This function is a convenience function that post a given text into the window's statusbar.
    """
    global TOOLBAR  # capture the toolbar's current data
    TOOLBAR.push_message_infobar(signal, msg_txt)   # launch the toolbar's push_message_infobar() method


def about_dialog():
    """Display an about dialog

    (None) -> None
    """
    global WINDOW, VERSION   # capture the window's current data and the current version number
    msg = """Thanks for trying out JDFeditor !!!

JDFeditor is a cross-platform, quick and simple database manager,

JDF Editor is bundled with an easy-to-use library: jdf_lib.
jdf_lib will quickly load the content of your database into a variable.
All you need to know is the filename!
    """
    license = """================================================
JDF Editor License

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see:
http://www.gnu.org/licenses/
================================================
    """
    image = GdkPixbuf.Pixbuf.new_from_file("logo.png")
    aboutdialog = Gtk.AboutDialog()
    aboutdialog.set_transient_for(WINDOW.window)
    aboutdialog.set_program_name("JDF Editor")
    aboutdialog.set_copyright('Copyright (c) 2016 Damian Chrzanowski')
    aboutdialog.set_license(license)
    aboutdialog.set_wrap_license(True)
    aboutdialog.set_version(VERSION)
    aboutdialog.set_logo(image)
    aboutdialog.set_comments(msg)
    aboutdialog.set_website("http://www.damianch.eu.pn/")
    aboutdialog.set_website_label("Check out my WebSite")
    aboutdialog.set_authors(["Damian Chrzanowski"])

    aboutdialog.run()
    aboutdialog.destroy()


def main():
    """Main function.

    (None) -> None
    """
    global WINDOW, DATA, UNTITLED_FILE_COUNT, TEMP_CLIPBOARD, TOOLBAR   # set globals
    DATA = list()   # create an empty list that will hold instances of DataCells
    UNTITLED_FILE_COUNT = 1   # start at Untitled1 filename
    TEMP_CLIPBOARD = None   # no info in the clipboard currently
    WINDOW = MainWindow()   # instantiate the window to the global variable

    MainMenu(WINDOW)   # launch the MainMenu class
    TOOLBAR = MainToolbar(WINDOW)   # instantiate the Toolbar to the global variable

    build_blank_table()  # make a blank table
    Gtk.main()  # launch the Gtk's main loop


if __name__ == '__main__':
    main()
