#!/usr/bin/env python
#
#		gTrueCrypt.py - gTrueCrypt 0.2-alpha
#
#	author:		Sebastian Billaudelle
#	copyright:	2007 by Sebastian Billaudelle
#	license:	GNU General Public License, version 2 only
#
#
#	This program is free software. It's allowed to modify and/or redistribute
#	it under the terms of the GNU General Public License, published by the
#	Free Software Foundation, version 2 only.
#	You should have received a copy of this license along with this software.
#	If not, see http://www.gnu.org/licenses/!
#
#	This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#

version = '0.2-alpha'

import pygtk
pygtk.require('2.0')
import gtk
import sys
from optparse import OptionParser
"""Try to load the backend"""
try:
	from truecrypt import *
except:
	print "ERROR: Couldn't find backend!"
	sys.exit()

"""This is the main class of gTrueCrypt"""
class gTrueCrypt:
	def __init__(self):
		self._icon_path = os.path.join(os.path.dirname(__file__), "gTrueCrypt.png")
		self._icon = gtk.gdk.pixbuf_new_from_file(self._icon_path)
		"""Get list from backend"""
		self.TW = TrueCrypt()
		self.__container = self.TW.getList()
		self.createMainWindow()
		self.setMainWindowLayout()
		self.loadList()
		self._show_hide_counter = 1

	def createMainWindow(self):
		"""Create a new window and show it"""
		self.main_window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.main_window.set_title("gTrueCrypt")
		self.main_window.set_icon(self._icon)
		self.main_window.set_border_width(20)
		self.main_window.set_size_request(650, 200)
		self.main_window.connect("delete_event", self.delete_event)
		self.main_window.show()

	def setMainWindowLayout(self):
		"""Set the layout of the main window"""
		self.list = gtk.ListStore(int, str, str, str, 'gboolean')
		self.table = gtk.TreeView(self.list)
		self.container = gtk.TreeViewColumn('Container')
		self.target = gtk.TreeViewColumn('Mountpoint')
		self.state = gtk.TreeViewColumn('State')
		self.table.append_column(self.container)
		self.table.append_column(self.target)
		self.table.append_column(self.state)
		self.container_cell = gtk.CellRendererText()
		self.target_cell = gtk.CellRendererText()
		self.state_cell = gtk.CellRendererText()
		self.container_cell.set_property('cell-background', 'white')
		self.target_cell.set_property('cell-background', 'white')
		self.state_cell.set_property('cell-background', 'white')
		self.container.pack_start(self.container_cell, False)
		self.state.pack_start(self.state_cell, True)
		self.target.pack_start(self.target_cell, True)
		self.container.set_attributes(self.container_cell, text=1)
		self.target.set_attributes(self.target_cell, text=2)
		self.state.set_attributes(self.state_cell, text=3)
		self.scrolledwindow = gtk.ScrolledWindow()
		self.scrolledwindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		self.scrolledwindow.add(self.table)
		self.table.connect('cursor-changed', self.actionButtonChange)
		self.action_button = gtk.Button("action")
		self.action_button.show()
		self.action_button.connect('clicked', self.action)
		self.edit_button = gtk.Button("edit")
		self.edit_button.show()
		self.edit_button.connect('clicked', self.edit)
		self.add_button = gtk.Button("add")
		self.add_button.show()
		self.add_button.connect('clicked', self.add)
		#self.pref_button = gtk.Button("preferences")
		#self.pref_button.show()
		#self.pref_button.connect('clicked', self.pref)
		self.hbox = gtk.HBox()
		self.hbox.show()
		self.hbox.pack_start(self.action_button, True)
		self.hbox.pack_start(self.edit_button, True)
		self.hbox.pack_start(self.add_button, True)
		#self.hbox.pack_start(self.pref_button, True)
		self.vbox = gtk.VBox()
		self.vbox.show()
		self.vbox.pack_start(self.scrolledwindow, True)
		self.vbox.pack_start(self.hbox, False)
		self.main_window.add(self.vbox)
		self.main_window.show_all()

	def loadList(self):
		"""Load the list of containers in the TreeView"""
		for c in self.__container:
			container_list = [c[0], c[1][0], c[1][1], c[1][2], "True"]
			self.list.append(container_list)

	def reloadList(self):
		"""Stuff to reload the list"""
		self.list.clear()
		self.loadList()

	def actionButtonChange(self, table):
		"""Switches the value of the action-button"""
		selection = self.table.get_selection()
		model, iter = selection.get_selected()
		if iter:
			state = self.list.get(iter, 3)
			if state[0] == "volume not mounted":
				self.action_button.set_label("mount")
			elif state[0] == "volume not found":
				self.action_button.set_label("details")
			elif state[0] == "volume mounted":
				self.action_button.set_label("unmount")
			elif state[0] == "error":
				self.action_button.set_label("details")
			elif state[0] == "mounted":
				self.action_button.set_label("unmount")

	def action(self, button):
		"""Eventhandler of the action-button"""
		self.selection = self.table.get_selection()
		self.model, self.iter = self.selection.get_selected()
		if iter:
			try:
				self.number = self.list.get(self.iter, 0)
				self.path = self.list.get(self.iter, 1)
				self.target = self.list.get(self.iter, 2)
				self.state = self.list.get(self.iter, 3)
			except TypeError:
				return False #FIXME Error dialog needed!
			if self.state[0] == "volume not mounted":
				self.mountContainer(self.number[0], self.target[0])
			elif self.state[0] == "mounted":
				self.umountContainer(self.number[0])
		return

	def edit(self, button):
		"""Eventhandler of the edit-button"""
		self.selection = self.table.get_selection()
		self.model, self.iter = self.selection.get_selected()
		if iter:
            		try:
				self._number = self.list.get(self.iter, 0)
				self._path = self.list.get(self.iter, 1)
				self._target = self.list.get(self.iter, 2)
				self._state = self.list.get(self.iter, 3)
			except TypeError: # If there are no entries....
				return False #FIXME Error dialog needed
			self.editDialog()

	def add(self, button):
		self.add_dialog_counter = 1
		self.addDialog()

	def editDialog(self, wrong_edit=False):
		self._show_hide_counter = 2
		"""Stuff for the password-dialog"""
		self.edit_dialog_window = gtk.Dialog("Edit", self.main_window,
            gtk.DIALOG_NO_SEPARATOR,
            ("Cancel",  gtk.RESPONSE_CLOSE,
             "OK",         gtk.RESPONSE_OK))
		self.edit_dialog_window.set_border_width(5)
		self.edit_dialog_window.set_modal(True)
		self.edit_dialog_layout = gtk.Table(4, 3, False)
		self.edit_dialog_layout.set_row_spacings(2)
		self.edit_dialog_layout.set_col_spacings(2)
		self.edit_dialog_layout.show()
		self.edit_dialog_label = gtk.Label("Here you can change all the stuff containing\nto the selected container.")
		self.edit_dialog_path_label = gtk.Label("Container")
		self.edit_dialog_path_label.show()
		self.edit_dialog_path_select = gtk.Button("...")
		self.edit_dialog_path_select.connect('clicked', self.pathFileselector)
		self.edit_dialog_path_select.show()
		self.edit_dialog_path_entry = gtk.Entry(max=0)
		self.edit_dialog_path_entry.set_text(self._path[0])
		self.edit_dialog_target_label = gtk.Label("Target")
		self.edit_dialog_target_label.show()
		self.edit_dialog_target_select = gtk.Button("...")
		self.edit_dialog_target_select.connect('clicked', self.targetFileselector)
		self.edit_dialog_target_select.show()
		self.edit_dialog_target_entry = gtk.Entry(max=0)
		self.edit_dialog_target_entry.set_text(self._target[0])
		self.edit_dialog_label.show()
		self.edit_dialog_path_entry.show()
		self.edit_dialog_layout.attach(self.edit_dialog_label, 0, 2, 0, 1)
  		self.edit_dialog_layout.attach(self.edit_dialog_path_label, 0, 1, 1, 2)
  		self.edit_dialog_layout.attach(self.edit_dialog_path_entry, 1, 2, 1, 2)
  		self.edit_dialog_layout.attach(self.edit_dialog_path_select, 2, 3, 1, 2)
  		self.edit_dialog_layout.attach(self.edit_dialog_target_label, 0, 1, 2, 3)
  		self.edit_dialog_layout.attach(self.edit_dialog_target_entry, 1, 2, 2, 3)
  		self.edit_dialog_layout.attach(self.edit_dialog_target_select, 2, 3, 2, 3)
		self.edit_dialog_window.vbox.pack_start(self.edit_dialog_layout, True, True, 0)
		self.edit_dialog_window.show_all()
		self.edit_dialog_window.connect("response", self.responseEditDialog)

	def addDialog(self):
		if self.add_dialog_counter == 1:
			self._show_hide_counter = 2
			"""Stuff for the add-dialog"""
			self.add_dialog_window = gtk.Dialog("Edit", self.main_window,
				gtk.DIALOG_NO_SEPARATOR,
            	("Cancel",  gtk.RESPONSE_CLOSE,
             	"Forward",         gtk.RESPONSE_OK))
			self.add_dialog_window.set_border_width(5)
			self.add_dialog_window.set_modal(True)
			self.add_dialog_label = gtk.Label("Here you can add new containers to the list and create new ones.")
			self.add_dialog_label.show()
			self.add_dialog_add_radio = gtk.RadioButton(None, "Add existing container to he list")
			self.add_dialog_add_radio.show()
			self.add_dialog_create_radio = gtk.RadioButton(self.add_dialog_add_radio, "Create new container")
			self.add_dialog_create_radio.show()
			self.add_dialog_create_radio.set_active(True)
			self.add_dialog_window.vbox.pack_start(self.add_dialog_label, True, True, 0)
			self.add_dialog_window.vbox.pack_start(self.add_dialog_create_radio, True, True, 0)
			self.add_dialog_window.vbox.pack_start(self.add_dialog_add_radio, True, True, 0)
			self.add_dialog_window.show_all()
			self.add_dialog_window.connect("response", self.responseAddDialog)
		elif self.add_dialog_counter == 2:
			if self.add_dialog_add_radio.get_active() == True:
				self.add_dialog_label.set_text("Select a container! It will be added to the list...")
				self.add_dialog_add_radio.destroy()
				self.add_dialog_create_radio.destroy()
				self.add_dialog_layout = gtk.Table(3, 2, False)
				self.add_dialog_layout.set_row_spacings(2)
				self.add_dialog_layout.set_col_spacings(2)
				self.add_dialog_layout.show()
				self.add_dialog_path_label = gtk.Label("Path to of the container you want to add")
				self.add_dialog_path_label.show()
				self.add_dialog_path_select = gtk.Button("...")
				self.add_dialog_path_select.connect('clicked', self.pathFileselector)
				self.add_dialog_path_select.show()
				self.add_dialog_path_entry = gtk.Entry(max=0)
				self.add_dialog_path_entry.show()
				self.add_dialog_target_label = gtk.Label("Path you want to mount the container")
				self.add_dialog_target_label.show()
				self.add_dialog_target_select = gtk.Button("...")
				self.add_dialog_target_select.connect('clicked', self.targetFileselector)
				self.add_dialog_target_select.show()
				self.add_dialog_target_entry = gtk.Entry(max=0)
				self.add_dialog_label.show()
				self.add_dialog_path_entry.show()
				self.add_dialog_target_entry.show()
  				self.add_dialog_layout.attach(self.add_dialog_path_label, 0, 1, 1, 2)
  		  		self.add_dialog_layout.attach(self.add_dialog_path_entry, 1, 2, 1, 2)
  		  		self.add_dialog_layout.attach(self.add_dialog_path_select, 2, 3, 1, 2)
  		  		self.add_dialog_layout.attach(self.add_dialog_target_label, 0, 1, 2, 3)
  		  		self.add_dialog_layout.attach(self.add_dialog_target_entry, 1, 2, 2, 3)
  		  		self.add_dialog_layout.attach(self.add_dialog_target_select, 2, 3, 2, 3)
		  		self.add_dialog_window.vbox.pack_start(self.add_dialog_layout, True, True, 0)
			elif self.add_dialog_create_radio.get_active() == True:
				self.add_dialog_label.set_text("Not implemented yet...")
				self.add_dialog_add_radio.destroy()
				self.add_dialog_create_radio.destroy()


	def responseEditDialog(self, dialog, response_id):
		if response_id == gtk.RESPONSE_OK:
			self.TW.setList(self._number[0], self.edit_dialog_path_entry.get_text(), self.edit_dialog_target_entry.get_text())
			self.list.set(self.iter, 1, self.edit_dialog_path_entry.get_text(), 2, self.edit_dialog_target_entry.get_text())
			self.edit_dialog_window.destroy()
			self._show_hide_counter = 1
		else:
			dialog.destroy()
			self._show_hide_counter = 1

	def responseAddDialog(self, dialog, response_id):
		if response_id == gtk.RESPONSE_OK:
			if self.add_dialog_add_radio.get_active() == True and self.add_dialog_counter == 2:
				self.TW.setList(None, self.add_dialog_path_entry.get_text(), self.add_dialog_target_entry.get_text())
				self.add_dialog_window.destroy()
				return
			self.add_dialog_counter = self.add_dialog_counter + 1
			self.addDialog()
		else:
			dialog.destroy()
			self._show_hide_counter = 1

	def pathFileselector(self, button):
		if button == self.add_dialog_path_select:
			self.path_fileselector = gtk.FileChooserDialog("Choose container", self.add_dialog_window, gtk.FILE_CHOOSER_ACTION_OPEN, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
			self.path_fileselector_response = self.path_fileselector.run()
			if self.path_fileselector_response == gtk.RESPONSE_OK:
				self.add_dialog_path_entry.set_text(self.path_fileselector.get_filename())
			self.path_fileselector.destroy()
		elif button == self.edit_dialog_path_select:
			self.path_fileselector = gtk.FileChooserDialog("Choose container", self.edit_dialog_window, gtk.FILE_CHOOSER_ACTION_OPEN, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
			self.path_fileselector.set_filename(self._path[0])
			self.path_fileselector_response = self.path_fileselector.run()
			if self.path_fileselector_response == gtk.RESPONSE_OK:
				self.edit_dialog_path_entry.set_text(self.path_fileselector.get_filename())
			self.path_fileselector.destroy()

	def targetFileselector(self, button):
		if button == self.add_dialog_target_select:
			self.target_fileselector = gtk.FileChooserDialog("Choose target", self.add_dialog_window, gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
			self.target_fileselector_response = self.target_fileselector.run()
			if self.target_fileselector_response == gtk.RESPONSE_OK:
				self.add_dialog_target_entry.set_text(self.target_fileselector.get_filename())
			self.target_fileselector.destroy()
		elif button == self.edit_dialog_target_select:
			self.target_fileselector = gtk.FileChooserDialog("Choose target", self.edit_dialog_window, gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
			self.target_fileselector.set_filename(self._target[0])
			self.target_fileselector_response = self.target_fileselector.run()
			if self.target_fileselector_response == gtk.RESPONSE_OK:
				self.edit_dialog_target_entry.set_text(self.target_fileselector.get_filename())
			self.target_fileselector.destroy()

	def pwdDialog(self, wrong_pwd=False):
		self._show_hide_counter = 2
		"""Stuff for the password-dialog"""
		self.pwd_dialog_window = gtk.Dialog("Enter password", self.main_window,
            gtk.DIALOG_NO_SEPARATOR,
            ("Cancel",  gtk.RESPONSE_CLOSE,
             "OK",         gtk.RESPONSE_OK))
		self.pwd_dialog_window.set_border_width(5)
		self.pwd_dialog_window.set_modal(True)
		self.pwd_dialog_layout = gtk.Table(3, 2, True)
		self.pwd_dialog_layout.set_row_spacings(2)
		self.pwd_dialog_layout.set_col_spacings(2)
		self.pwd_dialog_layout.show()
		if wrong_pwd == True: self.pwd_dialog_label = gtk.Label("Wrong password!\nPlease re-enter it!")
		else: self.pwd_dialog_label = gtk.Label("Please enter the password\nfor the container you want to mount!")
		self.pwd_dialog_entry = gtk.Entry(max=0)
		self.pwd_dialog_entry.set_visibility(False)
		self.pwd_dialog_label.show()
		self.pwd_dialog_entry.show()
		self.pwd_dialog_layout.attach(self.pwd_dialog_label, 0, 2, 0, 1)
  		self.pwd_dialog_layout.attach(self.pwd_dialog_entry, 0, 2, 1, 2)
		self.pwd_dialog_window.vbox.pack_start(self.pwd_dialog_layout, True, True, 0)
		self.pwd_dialog_window.show_all()
		self.pwd_dialog_window.connect("response", self.responsePwdDialog)

	def responsePwdDialog(self, dialog, response_id):
		if response_id == gtk.RESPONSE_OK:
			self.pwd = self.pwd_dialog_entry.get_text()
			self.result = self.TW.mount(self.number[0], self.target[0], self.pwd)
			self.pwd = ""
			self.pwd_dialog_window.destroy()
			self._show_hide_counter = 1
			if self.result == "wrong password": self.pwdDialog(True)
			elif self.result == "no password given": self.pwdDialog(True)
			elif self.result == "mounted":
				self.list.set(self.iter, 3, "mounted")
				self.action_button.set_label("unmount")
		else:
			dialog.destroy()
			self._show_hide_counter = 1

	def mountContainer(self, number, target):
		"""Function for mounting a container"""
		self.pwdDialog()

	def umountContainer(self, number):
		"""Function for umounting a container"""
		self.list.set(self.iter, 3, "volume not mounted")
		self.action_button.set_label("mount")
		self.TW.close(self.number[0])

	def delete_event(self, widget, event, data=None):
		"""Stuff for closing gTC"""
		self.main_window.hide_all()
		self._show_hide_counter = 0
		return True

	def statusIcon(self):
		self.icon = gtk.status_icon_new_from_file(self._icon_path) #TODO: Change icon
		self.icon.connect('popup-menu', self.on_right_click)
		self.icon.connect('activate', self.show_hide)

	def on_right_click(self, icon, event_button, event_time):
		self.statusIconMenu(event_button, event_time, icon)

	def statusIconMenu(self, event_button, event_time, icon):
		menu = gtk.Menu()
		item = gtk.MenuItem("Close")
		item.connect_object("activate", self.exit, menu)
		item.show()
		menu.append(item)
		menu.popup(None, None, gtk.status_icon_position_menu, event_button, event_time, icon)

	def exit(self, button):
		gtk.main_quit()

	def show_hide(self, button):
		if self._show_hide_counter == 1:
			self.main_window.hide_all()
			self._show_hide_counter = 0
		elif self._show_hide_counter == 0:
			self.main_window.show_all()
			self._show_hide_counter = 1

def main():
		parser = OptionParser(version="%prog blub" )
		(options, args) = parser.parse_args()
		gui = gTrueCrypt()
		gui.statusIcon()
		gtk.main()
		return 0

if __name__ == "__main__":
	print
	print "###########################################################"
	print "#                 gTrueCrypt 0.2-alpha                    #"
	print "#                                                         #"
	print "#   backend by:    Jens Kadenbach                         #"
	print "#   gui by:     Sebastian Billaudelle                     #"
	print "#                                                         #"
	print "# This program is free software. It is published under    #"
	print "# the terms of the of the GNU General Public License,     #"
	print "# published by the Free Software Foundation,              #"
	print "# version 2 only. See http://www.gnu.org/licenses/!       #"
	print "#                                                         #"
	print "# This program is distributed in the hope that it will    #"
	print "# be useful, but WITHOUT ANY WARRANTY; without even the   #"
	print "# implied warranty of MERCHANTABILITY or FITNESS FOR A    #"
	print "# PARTICULAR PURPOSE.                                     #"
	print "# See the GNU General Public License for more details.    #"
	print "###########################################################"
	print
	main()
