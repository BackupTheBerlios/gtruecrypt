import pygtk
pygtk.require('2.0')
import gtk

class optionFactory(gtk.VBox):
	def __init__(self, group_name, options):
		gtk.VBox.__init__(self)
		self._options = options
		count = 0
		for c in options:
			count = count + 1
		lines = count/3
		if count%3 != 0:
			lines = lines + 1
		self.table = gtk.Table(lines, 3, False)
		self.frame = gtk.Frame(group_name)
		self.frame.add(self.table)
		self.option_buttons = []
		count = 0
		count_x = 0
		count_y = 0
		for c in options:
			if count != 0:
				self.rad = gtk.RadioButton(self.option_buttons[0], c[1])
			else:
				self.rad = gtk.RadioButton(None, c[1])
			self.option_buttons.append(self.rad)
			self.table.attach(self.option_buttons[count], count_x, count_x+1, count_y, count_y+1)
			self.option_buttons[count].show()
			count = count + 1
			count_x = count_x + 1
			if count_x == 3:
				count_x = 0
				count_y = count_y + 1
		self.pack_start(self.frame, True, True, 0)
		self.frame.show()
		self.table.show()

	def get_active(self):
		count = 0
		for c in self.option_buttons:
			if self.option_buttons[count].get_active() == True:
				return self._options[count][0]
			count = count + 1