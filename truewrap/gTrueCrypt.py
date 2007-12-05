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

version = '0.3.1-beta'

import pygtk
pygtk.require('2.0')
import gtk, gobject
import sys, os
from gtctable import *
from optionFactory import *
from language_de import *
lang = language_de
from optparse import OptionParser
import dbus

class gTrueCrypt:
	def __init__(self, tray=None):
		"""
		dbus-stuff
		"""
		self._bus = dbus.SessionBus()
		try:
			self._daemon = self._bus.get_object("org.gtruecrypt.daemon",
										"/gTCd")
		except dbus.DBusException:
			print "FATAL: Couldn't find backend on dbus."
			print "Check if dbus is running and start the daemon!"
			print
			print_exc()
			sys.exit(1)
		self._containers = self._daemon.getList()
		try:
			self._icon_path = os.path.join(os.path.dirname(__file__), "gTrueCrypt.png")
			self._icon = gtk.gdk.pixbuf_new_from_file(self._icon_path)
		except Exception, e:
			print e
			sys.exit()
		self.trayIcon()
		self.mainWindow = mainWindow(self._icon, self._containers)

	def trayIcon(self):
		def trayMenu(icon, event_button, event_time):
			menu = gtk.Menu()
			item = gtk.MenuItem(lang['trayMenuClose'])
			item.connect_object("activate", self.exit, menu)
			item.show()
			menu.append(item)
			menu.popup(None, None, gtk.status_icon_position_menu, event_button, event_time, icon)
		def trayShowHide(statusIcon):
			print "showhide"
		self.icon = gtk.status_icon_new_from_file(self._icon_path)
		self.icon.connect('popup-menu', trayMenu)
		self.icon.connect('activate', trayShowHide)

	def exit(self, button):
		gtk.main_quit()

class mainWindow(gtk.Window):
	def __init__(self, icon, containers):
		gtk.Window.__init__(self)
		self._containers = containers
		self.set_size_request(800, 270)
		self.set_border_width(8)
		self.set_icon(icon)
		self.content = gtk.HPaned()
		self.packLeft()
		self.packRight()
		self.loadList()
		self.add(self.content)
		self.show_all()
	def packLeft(self):
		self.listBox = gtk.VBox()
		self.list = gtk.ScrolledWindow()
		self.list.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		self.list.set_size_request(240, 214)
		self.addButton = gtk.Button(lang["add"])
		self.delButton = gtk.Button(lang["del"])
		self.addButton.connect("clicked", self.addContainer)
		self.buttonTable = gtk.Table(1, 2, True)
		self.buttonTable.set_size_request(270, 26)
		self.buttonTable.attach(self.addButton, 0, 1, 0, 1)
		self.buttonTable.attach(self.delButton, 1, 2, 0, 1)
		self.listBox.pack_start(self.list, True, False, 0)
		self.listBox.pack_start(self.buttonTable, True, True, 0)
		self.content.add1(self.listBox)
	def packRight(self):
		self.infoBox = gtk.VBox()
		self.content.add2(self.infoBox)
	def loadList(self):
		self.listStore = gtk.ListStore(int, str, str, str, 'gboolean')
		self.treeView = gtk.TreeView(self.listStore)
		self.list.add_with_viewport (self.treeView)
		status = {
				'volume not mounted' : None,
				'mounted' : gtk.STOCK_APPLY,
				'volume not found' : gtk.STOCK_DIALOG_ERROR
				}
		for c in self._containers:
			container_list = [c[0], c[1][0], c[1][1],status[c[1][2]], "True"]
			self.listStore.append(container_list)
		self.iconCell = gtk.CellRendererPixbuf()
		self.cell = gtk.CellRendererText()
		self.column = gtk.TreeViewColumn(lang["cont"])
		self.column.pack_start(self.iconCell, False)
		self.column.pack_start(self.cell, False)
		self.column.set_attributes(self.iconCell, stock_id=3)
		self.column.set_attributes(self.cell, text=1)
		self.treeView.append_column(self.column)
		self.treeView.connect('cursor-changed', self.containerChange)
	def containerChange(self, treeView):
		selection = self.treeView.get_selection()
		model, iter = selection.get_selected()
		try:
			self.containerId = self.listStore.get(iter, 0)
			self.containerPath = self.listStore.get(iter, 1)
			self.containerTarget = self.listStore.get(iter, 2)
			self.containerState = self.listStore.get(iter, 3)
			if self.__dict__.has_key("info"):
				self.info.destroy()
			self.info = gtk.Frame(self.containerPath[0])
			self.infoBox.pack_start(self.info, True, True, 0)
			self.info.show()
			self.vBox = gtk.VBox()

			if self.containerState[0] == "gtk-apply":
				self.table = Table(4, 3, False)
				targetLabel = gtk.Label(lang["target"]+":")
				targetLabel.show()
				targetData = gtk.Label(self.containerTarget[0])
				targetData.show()
				self.table.attach(targetLabel, 0, 1, 0, 1)
				self.table.attach(targetData, 1, 2, 0, 1)
				self.table.show()
				self.vBox.pack_start(self.table, False, False, 0)

			elif self.containerState[0] == None:
				def optionUseOwnClick(optionButton):
					if optionUseOwn.get_active() == True:
						entryUseOwn.set_sensitive(True)
						buttonUseOwn.set_sensitive(Trueelf.buttonTable.set_sensitive(False))
					else:
						entryUseOwn.set_sensitive(False)
						buttonUseOwn.set_sensitive(False)
				def mount(button):
					pass
				self.table = Table(4, 3, False)
				targetLabel = gtk.Label(lang["target"]+":")
				targetLabel.show()
				optionLetCreate = gtk.RadioButton(None, None)
				labelLetCreate = gtk.Label(lang["letCreate"])
				labelLetCreate.show()
				optionLetCreate.show()
				optionUseOwn = gtk.RadioButton(optionLetCreate, None)
				optionUseOwn.connect("clicked", optionUseOwnClick)
				optionUseOwn.show()
				entryUseOwn = gtk.Entry()
				entryUseOwn.set_size_request(270, 28)
				try: entryUseOwn.set_text(self.containerTarget[0])
				except: pass
				entryUseOwn.set_sensitive(False)
				entryUseOwn.show()
				buttonUseOwn = gtk.Button("...")
				buttonUseOwn.set_size_request(40, 28)
				buttonUseOwn.set_sensitive(False)
				buttonUseOwn.show()
				boxUseOwn = gtk.HBox()
				boxUseOwn.pack_start(entryUseOwn, False, False, 0)
				boxUseOwn.pack_start(buttonUseOwn, False, False, 0)
				boxUseOwn.show()
				pwdLabel = gtk.Label(lang["pwd"]+":")
				pwdLabel.show()
				entryPwd = gtk.Entry()
				entryPwd.set_size_request(220, 28)
				entryPwd.set_visibility(False)
				entryPwd.show()
				savePwd = gtk.CheckButton(lang["savePwd"])
				savePwd.show()
				boxPwd = gtk.HBox()
				boxPwd.pack_start(entryPwd, False, False, 0)
				boxPwd.pack_start(savePwd, False, False, 0)
				boxPwd.show()
				optLabel = gtk.Label(lang["mountOpt"]+":")
				optLabel.show()
				userMount = gtk.CheckButton(lang["userMount"])
				userMount.set_active(True)
				userMount.show()
				buttonBox = gtk.HBox()
				okButton = gtk.Button(lang["mount"])
				okButton.show()
				okButton.set_size_request(100, 35)
				okButton.connect("clicked", mount)
				buttonBox.set_size_request(500, 35)
				buttonBox.pack_start(okButton, True, False, 0)
				buttonBox.show()
				self.table.attach(targetLabel, 0, 1, 0, 1)
				self.table.attach(optionLetCreate, 1, 2, 0, 1)
				self.table.attach(labelLetCreate, 2, 3, 0, 1)
				self.table.attach(optionUseOwn, 1, 2, 1, 2)
				self.table.attach(boxUseOwn, 2, 3, 1, 2)
				self.table.attach(pwdLabel, 0, 1, 2, 3)
				self.table.attach(boxPwd, 1, 3, 2, 3)
				self.table.attach(optLabel, 0, 1, 3, 4)
				self.table.attach(userMount, 1, 3, 3, 4)
				self.table.attach(buttonBox, 0, 3, 4, 5)
				self.table.show()
				self.vBox.pack_start(self.table, False, False, 0)
			self.vBox.show()
			self.info.add(self.vBox)
		except:
			if self.__dict__.has_key("info"):
				self.info.destroy()
			self.info = gtk.Frame(lang['error'])
			self.infoBox.pack_start(self.info, True, True, 0)
			self.info.show()
			errorLabel = gtk.Label(lang['mainCouldNotGetContainerInfo'])
			errorLabel.show()
			self.info.add(errorLabel)
	def addContainer(self, button):
		def forward(button, mode):
			if mode == "addExistingPath":
				addExistingPath()
		def cancel(button):
			self.treeView.set_sensitive(True)
			self.buttonTable.set_sensitive(True)
			self.containerChange(None)
		def modeSwitch(button):
			mode = self.mode.get_active()
			if mode == "new":
				createNewPath(None)
			else:
				addExistingPath(None)
		def fileChanged(button):
			print self.pathSelector.get_filename()
		def modeSelect():
			self.treeView.set_sensitive(False)
			self.buttonTable.set_sensitive(False)
			if self.__dict__.has_key("info"):
				self.info.destroy()
			self.info = gtk.Frame(lang["addContainer"])
			self.infoBox.pack_start(self.info, True, True, 0)
			self.info.show()
			self.vBox = gtk.VBox()
			self.vBox.show()
			self.info.add(self.vBox)
			self.helpLabel = gtk.Label(lang["addMode"])
			self.helpLabel.set_line_wrap(True)
			self.helpLabel.set_size_request(500, 100)
			self.helpLabel.show()
			choices = [
					["new", lang["createNewContainer"]],
					["add", lang["addExistingContainer"]]
					]
			self.mode = optionFactory(None, choices, 1, False)
			self.mode.show()
			self.forwardButton = gtk.Button(stock=gtk.STOCK_GO_FORWARD)
			self.forwardButton.connect("clicked", modeSwitch)
			self.forwardButton.show()
			self.cancelButton = gtk.Button(stock=gtk.STOCK_CANCEL)
			self.cancelButton.connect("clicked", cancel)
			self.cancelButton.show()
			self.buttonBox = gtk.HButtonBox()
			self.buttonBox.set_border_width(8)
			self.buttonBox.set_spacing(8)
			self.buttonBox.set_layout(gtk.BUTTONBOX_END)
			self.buttonBox.add(self.forwardButton)
			self.buttonBox.add(self.cancelButton)
			self.buttonBox.show()
			self.vBox.pack_start(self.helpLabel, False, False, 5)
			self.vBox.pack_start(self.mode, False, False, 5)
			self.vBox.pack_end(self.buttonBox, False, False, 5)
		def addExistingPath(button=None):
			self.treeView.set_sensitive(False)
			self.buttonTable.set_sensitive(False)
			if self.__dict__.has_key("info"):
				self.info.destroy()
			self.info = gtk.Frame(lang["addContainer"])
			self.infoBox.pack_start(self.info, True, True, 0)
			self.info.show()
			self.vBox = gtk.VBox()
			self.vBox.show()
			self.info.add(self.vBox)
			self.helpLabel = gtk.Label(lang["addExistingPath"])
			self.helpLabel.set_line_wrap(True)
			self.helpLabel.set_size_request(500, 100)
			self.helpLabel.show()
			self.pathSelectorDialog = gtk.FileChooserDialog(
				title="Select a directory",
				parent=None,
				action=gtk.FILE_CHOOSER_ACTION_OPEN,
				buttons= (gtk.STOCK_OPEN, gtk.RESPONSE_ACCEPT,
                          gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL),
                          backend=None)
			self.pathSelector = gtk.FileChooserButton(self.pathSelectorDialog)
			self.pathSelector.show()
			self.forwardButton = gtk.Button(stock=gtk.STOCK_GO_FORWARD)
			self.forwardButton.connect("clicked", forward, "addExistingTarget")
			self.forwardButton.show()
			self.cancelButton = gtk.Button(stock=gtk.STOCK_CANCEL)
			self.cancelButton.connect("clicked", cancel)
			self.cancelButton.show()
			self.buttonBox = gtk.HButtonBox()
			self.buttonBox.set_border_width(8)
			self.buttonBox.set_spacing(8)
			self.buttonBox.set_layout(gtk.BUTTONBOX_END)
			self.buttonBox.add(self.forwardButton)
			self.buttonBox.add(self.cancelButton)
			self.buttonBox.show()
			self.vBox.pack_start(self.helpLabel, False, False, 5)
			self.vBox.pack_start(self.pathSelector, False, False, 5)
			self.vBox.pack_end(self.buttonBox, False, False, 5)
		def createNewPath(button=None):
			def showPathSelect(button):
				self.pathSelectorDialog = gtk.FileChooserDialog(
				title="Select a directory",
				parent=None,
				action=gtk.FILE_CHOOSER_ACTION_SAVE,
				buttons= (gtk.STOCK_OPEN, gtk.RESPONSE_OK,
                          gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL),
                          backend=None)
				response = self.pathSelectorDialog.run()
				if response == gtk.RESPONSE_OK:
					print self.pathSelectorDialog.get_filename()
					self.pathSelectorDialog.destroy()
			self.treeView.set_sensitive(False)
			self.buttonTable.set_sensitive(False)
			if self.__dict__.has_key("info"):
				self.info.destroy()
			self.info = gtk.Frame(lang["addContainer"])
			self.infoBox.pack_start(self.info, True, True, 0)
			self.info.show()
			self.vBox = gtk.VBox()
			self.vBox.show()
			self.info.add(self.vBox)
			self.helpLabel = gtk.Label(lang["createNewPath"])
			self.helpLabel.set_line_wrap(True)
			self.helpLabel.set_size_request(500, 100)
			self.helpLabel.show()
			self.pathSelector = gtk.Button(lang["none"])
			self.pathSelector.connect("clicked", showPathSelect)
			self.pathSelector.show()
			self.forwardButton = gtk.Button(stock=gtk.STOCK_GO_FORWARD)
			self.forwardButton.connect("clicked", forward, "createNewTarget")
			self.forwardButton.show()
			self.cancelButton = gtk.Button(stock=gtk.STOCK_CANCEL)
			self.cancelButton.connect("clicked", cancel)
			self.cancelButton.show()
			self.buttonBox = gtk.HButtonBox()
			self.buttonBox.set_border_width(8)
			self.buttonBox.set_spacing(8)
			self.buttonBox.set_layout(gtk.BUTTONBOX_END)
			self.buttonBox.add(self.forwardButton)
			self.buttonBox.add(self.cancelButton)
			self.buttonBox.show()
			self.vBox.pack_start(self.helpLabel, False, False, 5)
			self.vBox.pack_start(self.pathSelector, False, False, 5)
			self.vBox.pack_end(self.buttonBox, False, False, 5)
		modeSelect()
	def nameEntryChanged(self, entry):
		selection = self.treeView.get_selection()
		self.model, iter = selection.get_selected()
		self.model.set(iter, 1, self.pathEntry.get_text())
class gTCError:
	def __init__(self, error):
		errorDialog = gtk.MessageDialog( None, 0, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, str(lang["errorMessage"])+"\n"+str(error))
		errorDialog.show()

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
	gTC = gTrueCrypt()
	gtk.main()
