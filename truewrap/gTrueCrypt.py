#!/usr/bin/env python
#
#		gTrueCrypt.py - gTrueCrypt 0.2-alpha
#
#	author:		Sebastian Billaudelle
#	copyright:	2007 by Sebastian Billaudelle
#	license:		GNU General Public License, version 2 only
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
		"""Get list from backend"""
		self.TW = TrueCrypt()
		self.__container = self.TW.getList()
		self.createMainWindow()
		self.setMainWindowLayout()
		self.loadList()

	def createMainWindow(self):
		"""Create a new window and show it"""
		self.main_window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.main_window.set_title("gTrueCrypt")
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
		#self.add_button.connect('clicked', self.add)
		self.pref_button = gtk.Button("preferences")
		self.pref_button.show()
		#self.pref_button.connect('clicked', self.pref)
		self.hbox = gtk.HBox()
		self.hbox.show()
		self.hbox.pack_start(self.action_button, True)
		self.hbox.pack_start(self.edit_button, True)
		self.hbox.pack_start(self.add_button, True)
		self.hbox.pack_start(self.pref_button, True)
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
			self.number = self.list.get(self.iter, 0)
			self.path = self.list.get(self.iter, 1)
			self.target = self.list.get(self.iter, 2)
			self.state = self.list.get(self.iter, 3)
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
			self._number = self.list.get(self.iter, 0)
			self._path = self.list.get(self.iter, 1)
			self._target = self.list.get(self.iter, 2)
			self._state = self.list.get(self.iter, 3)
			self.editDialog()

	def editDialog(self, wrong_edit=False):
		"""Stuff for the password-dialog"""
		self.edit_dialog_window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.edit_dialog_window.set_title("Edit")
		self.edit_dialog_window.set_border_width(5)
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
		self.edit_dialog_target_entry = gtk.Entry(max=0)
		self.edit_dialog_target_entry.set_text(self._target[0])
		self.edit_dialog_label.show()
		self.edit_dialog_path_entry.show()
		self.edit_dialog_button_ok = gtk.Button("OK")
		self.edit_dialog_button_cancel = gtk.Button("Cancel")
		self.edit_dialog_button_ok.connect('clicked', self.editDialogOk)
		self.edit_dialog_button_cancel.connect('clicked', self.editDialogCancel)
		self.edit_dialog_layout.attach(self.edit_dialog_label, 0, 2, 0, 1)
  		self.edit_dialog_layout.attach(self.edit_dialog_path_label, 0, 1, 1, 2)
  		self.edit_dialog_layout.attach(self.edit_dialog_path_entry, 1, 2, 1, 2)
  		self.edit_dialog_layout.attach(self.edit_dialog_path_select, 2, 3, 1, 2)
  		self.edit_dialog_layout.attach(self.edit_dialog_target_label, 0, 1, 2, 3)
  		self.edit_dialog_layout.attach(self.edit_dialog_target_entry, 1, 2, 2, 3)
  		self.edit_dialog_layout.attach(self.edit_dialog_button_ok, 0, 1, 3, 4)
  		self.edit_dialog_layout.attach(self.edit_dialog_button_cancel, 1, 2, 3, 4)
		self.edit_dialog_window.add(self.edit_dialog_layout)
		self.edit_dialog_window.show_all()

	def pathFileselector(self, button):
		self.path_fileselector = gtk.FileSelection("select container")
		self.path_fileselector.ok_button.connect("clicked", self.fileselectorOk)
		self.path_fileselector.cancel_button.connect("clicked", self.fileselectorCancel)
		self.path_fileselector.set_filename(self._path[0])
		self.path_fileselector.show()

	def pwdDialog(self, wrong_pwd=False):
		"""Stuff for the password-dialog"""
		self.pwd_dialog_window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.pwd_dialog_window.set_title("Password")
		self.pwd_dialog_window.set_border_width(5)
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
		self.pwd_dialog_button_ok = gtk.Button("OK")
		self.pwd_dialog_button_cancel = gtk.Button("Cancel")
		self.pwd_dialog_button_ok.connect('clicked', self.pwdDialogOk)
		self.pwd_dialog_button_cancel.connect('clicked', self.pwdDialogCancel)
		self.pwd_dialog_layout.attach(self.pwd_dialog_label, 0, 2, 0, 1)
  		self.pwd_dialog_layout.attach(self.pwd_dialog_entry, 0, 2, 1, 2)
  		self.pwd_dialog_layout.attach(self.pwd_dialog_button_ok, 0, 1, 2, 3)
  		self.pwd_dialog_layout.attach(self.pwd_dialog_button_cancel, 1, 2, 2, 3)
		self.pwd_dialog_window.add(self.pwd_dialog_layout)
		self.pwd_dialog_window.show_all()

	def mountContainer(self, number, target):
		"""Function for mounting a container"""
		self.pwdDialog()

	def umountContainer(self, number):
		"""Function for umounting a container"""
		self.list.set(self.iter, 3, "volume not mounted")
		self.action_button.set_label("mount")
		self.TW.close(self.number[0])

	def fileselectorOk(self, button):
		"""Eventhandler of the OK-button in the"""
		self._new_path = self.path_fileselector.get_filename()
		self.edit_dialog_path_entry.set_text(self._new_path)
		self.path_fileselector.destroy()

	def fileselectorCancel(self, button):
		"""Eventhandler of the Cancel-button in the"""
		self.path_fileselector.destroy()

	def editDialogOk(self, button):
		"""Eventhandler of the OK-button in the editDialog"""
		self.TW.setList(self._number[0], self.edit_dialog_path_entry.get_text(), self.edit_dialog_target_entry.get_text())
		self.list.set(self.iter, 1, self.edit_dialog_path_entry.get_text(), 2, self.edit_dialog_target_entry.get_text())
		self.edit_dialog_window.destroy()

	def editDialogCancel(self, button):
		"""Eventhandler of the Cancel-button in the editDialog"""
		self.edit_dialog_window.destroy()

	def pwdDialogOk(self, button):
		"""Eventhandler of the OK-button in the pwdDialog"""
		self.pwd = self.pwd_dialog_entry.get_text()
		self.result = self.TW.mount(self.number[0], self.target[0], self.pwd)
		self.pwd = ""
		self.pwd_dialog_window.destroy()
		if self.result == "wrong password": self.pwdDialog(True)
		elif self.result == "no password given": self.pwdDialog(True)
		elif self.result == "mounted":
			self.list.set(self.iter, 3, "mounted")
			self.action_button.set_label("unmount")

	def pwdDialogCancel(self, button):
		"""Eventhandler of the Cancel-button in the pwdDialog"""
		self.pwd_dialog_window.destroy()

	def delete_event(self, widget, event, data=None):
		"""Stuff for closing gTC"""
		gtk.main_quit()
		return False

def main():
        parser = OptionParser(version="%prog blub" )
        (options, args) = parser.parse_args()
        gui = gTrueCrypt()
        gtk.main()
        return 0

if __name__ == "__main__":
	print
	print "###########################################################"
	print "#                 gTrueCrypt 0.2-alpha                    #"
	print "#                                                         #"
	print "#   backend by:      Jens Kadenbach                       #"
	print "#   gui by:       Sebastian Billaudelle                   #"
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
