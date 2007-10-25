import pygtk
pygtk.require('2.0')
import gtk

class Table(gtk.Table):
	def attach(self, widget, x, x2, y, y2):
		self.alignment = gtk.Alignment(xalign=0.0, yalign=0.0, xscale=0.0, yscale=0.0)
		self.alignment.add(widget)
		self.alignment.show()
		gtk.Table.attach(self, self.alignment, x, x2, y, y2)