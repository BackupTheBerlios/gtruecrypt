#!/usr/bin/env python

#
#		gTrueCrypt.py - gTrueCrypt 0.0.1
#
#	author:		Sebastian Billaudelle
#	copyright:	2007 by Sebastian Billaudelle
#	license:		GNU General Public License, version 2 only
#	date:			
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

import pygtk
pygtk.require('2.0')
import gtk
"""importing classes from the TrueCrypt-Wrapper from Jens Kaldenbach"""
from tcw import *
"""This class includes all stuff to create and manage the main window"""
class main_window:
	"""creates a new window and sets its properties"""
	def create(self):
		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.window.set_title("gTrueCrypt")
		self.window.set_border_width(20)
		self.window.set_size_request(450, 200)
		self.window.connect("delete_event", self.delete_event)
		
		self.table()
	def table(self):
		self.liststore = gtk.ListStore(str, str, str, 'gboolean')
		self.treeview = gtk.TreeView(self.liststore)
		self.container = gtk.TreeViewColumn('Container')
		self.target = gtk.TreeViewColumn('Mountpoint')
		self.state = gtk.TreeViewColumn('State')
		self.TC = TrueCrypt("ME182BT")
		container = self.TC.getList()
		for c in container:
			container_list = [c[1][0], c[1][1], c[1][2], "True"]
			self.liststore.append(container_list)
		self.treeview.append_column(self.container)
		self.treeview.append_column(self.target)
		self.treeview.append_column(self.state)
		self.cellpb = gtk.CellRendererText()
		self.cell = gtk.CellRendererText()
		self.cell1 = gtk.CellRendererText()
		self.cellpb.set_property('cell-background', 'white')
		self.cell.set_property('cell-background', 'white')
		self.cell1.set_property('cell-background', 'white')
		self.container.pack_start(self.cellpb, False)
		self.state.pack_start(self.cell, True)
		self.target.pack_start(self.cell1, True)
		self.treeview.connect('cursor-changed', self.button_change)
		self.button = gtk.Button("action")#Has to be renamed automaticly on changing cont.-state (,ount/eject/details)
		self.button.show()
		self.container.set_attributes(self.cellpb, text=0)
		self.target.set_attributes(self.cell1, text=1)
		self.state.set_attributes(self.cell, text=2)
		self.scrolledwindow = gtk.ScrolledWindow()
		self.scrolledwindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		self.scrolledwindow.add(self.treeview)
		self.vbox = gtk.VBox()
		self.button.connect('clicked', self.action)
		self.vbox.show()
		self.vbox.pack_start(self.scrolledwindow, True)
		self.vbox.pack_start(self.button, False)
		self.window.add(self.vbox)
		self.window.show_all()
	def button_change(self, treeview):
		selection = self.treeview.get_selection()
		model, iter = selection.get_selected()
		if iter:
			state = self.liststore.get(iter, 2)
			if state[0] == "volume not mounted":
				self.button.set_label("mount")
			elif state[0] == "volume not found":
				self.button.set_label("deatails")
			elif state[0] == "volume mounted":
				self.button.set_label("unmount")
			elif state[0] == "error":
				self.button.set_label("details")
				#need some more info about state "mounted"
	def action(self, button):
		selection = self.treeview.get_selection()
		model, iter = selection.get_selected()
		if iter:
			state = self.liststore.get(iter, 2)
			path = self.liststore.get(iter, 0)
			target = self.liststore.get(iter, 1)
			if state[0] == "volume not mounted":
				self.liststore.set(iter, 2, "mounted")
				print self.TC.mount(0, target[0], "ME182BT")
			elif state[0] == "mounted":
				self.liststore.set(iter, 2, "unmounted")
				
		return
	"""funktion for closing gTC"""
	def delete_event(self, widget, event, data=None):
		gtk.main_quit()
		return False
"""main class"""
class gTrueCrypt:
    def __init__(self):
    	mw = main_window()
    	mw.create()
    	mw.window.show()


def main():
    gtk.main()
    return 0       

if __name__ == "__main__":
    gTrueCrypt()
    main()
