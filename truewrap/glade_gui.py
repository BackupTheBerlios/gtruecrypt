#!/usr/bin/env python

import gtk
from gtk import glade
import truecrypt
import tcresponse
import tcerr
import sys

class TruecryptGui(object):
    def __init__(self, glade_conf):
        self.xml = glade.XML(glade_conf)
        self.__connect()
        self.widget = self.xml.get_widget('window1')
        self.vbox = self.widget.get_child()
        (self.hbox1, self.hbox2) = self.vbox.get_children()
        (self.mount_button, self.filechooser, self.status, self.path) = self.hbox2.get_children()
        (self.combo, self.password) = self.hbox1.get_children()

        self.truecrypt = truecrypt.TrueCrypt()
        self.containers = []

        self.main()
    def __connect(self):
        self.xml.signal_autoconnect({
                "on_mountbutton_clicked": self.mount,
                "delete_event"               : self.destroy,
                })
    def mount(self, widget, data=None):
        filename = self.filechooser.get_filename()
        if not filename:
            self.status.set_text("Choose a file!")
            return False
        cont = truecrypt.TrueCont(filename)
        cont.open(target = '/home/dax/tmp/crypt', password = 'blub') #FIXME


    def destroy(self, widget, data=None):
        gtk.main_quit()
        print "exiting..."
        sys.exit(0)
        return False

    def main(self):
        self.widget.show()
        gtk.main()

if __name__ == '__main__':
    gui = TruecryptGui('glade_gui.glade')
