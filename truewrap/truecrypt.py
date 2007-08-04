#!/usr/bin/python 
#
#      gTrueCrypt.py - gTrueCrypt 0.0.1
#
#   author:      Jens Kadenbach
#   copyright:   2007 by Jens Kadenbach
#   license:      GNU General Public License, version 2 only
#
#
#  This program is free software. It's allowed to modify and/or redistribute
#  it under the terms of the GNU General Public License, published by the
#  Free Software Foundation, version 2 only.
#  You should have received a copy of this license along with this software.
#  If not, see http://www.gnu.org/licenses/!
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
# 


import os
import sys

__version__ = "0.2-alpha"

class TrueCrypt (object):
    """Wrapper class to access TrueCrypt functions"""
    def __init__(self, sudo_passwd=None):
        """_containers is a list of TrueCont Objects"""
        self._containers = []
        self.__sudo_passwd = sudo_passwd

    def getMapped(self):
        """Will Return a nice Tuple of mapped TrueCrypt objects"""
        mapped = os.popen("truecrypt --list").readlines()
        return mapped

    def create(self, path, password, voltype, size, fs, ha, ea):
        """
        Create a TrueCont Object and let it create a real TrueCrypt-Container
        voltype Normal or Hidden
        size    in bytes or like "10M", look in TrueCrypts Manpage!
        fs  Fat32 or None :: I will implement ext3 as soon as possible
        ha  Hash algorithm 
        ea  Encryption algorithm

        returns __str__ of TrueCont Object
        """
        cont = TrueCont(path, password)
        cont.create(voltype, size, fs, ha, ea, self.__sudo_passwd)
        self._containers += [cont]
        return str(cont)

    def getList(self):
        """
        Returns a list of tuples with (Number of container, (path, target, status))
        """
        list = []
        cnt = 0
        for c in self._containers:
            cnt += 1
            cont = iter(c) # Iterate through containers atributes
            list += [(cnt, cont.next(), cont.next(), cont.next())]
        return list

    def mount(self, num, target, mount_options=None):
        """
        mount the TrueCont to given target

        num (int) - Number of a TrueCont Object in the self._containers list
        target (str) - Target directory
        """
        return self._containers[num].open(target, mount_options, self.__sudo_passwd)    

    def close(self, num):
        return self._containers[num].close(self.__sudo_passwd)

    def open(self, path, password=None, target=None):
        self._containers += [TrueCont(path, password, target)]
        return 


class TrueCont (object):
    def __init__(self, path, password = None, target=None):
        self.path = path
        self.password = password
        self.target = target
        self._status = self.frstStatus()
        self._error = ""

    def create(self,voltype, size, fs, ha, ea):
        """
        voltype Normal or Hidden
        size    in bytes or like "10M", look in TrueCrypts Manpage!
        fs  fat or None :: I will implement ext3 as soon as possible
        ha  Hash algorithm 
        ea  Encryption algorithm
        """
        assert voltype in ["Normal", "Hidden"], "Voltype must be of 'Normal' or 'Hidden'"
        assert fs in ["fat", "None"], "Filesystem must be of 'fat' or 'None'"
        import string
        from random import choice
        self.size = size
        # Create a file in /tmp with 320 random ASCI Chars to give truecrypt random input
        chars = string.letters + string.digits
        random = "".join([choice(chars) for c in xrange(320)])
        randfilename = "/tmp/randfile"
        if os.path.isfile(randfilename): os.remove(randfilename) # Delte any previous Randfiles
        randfile = file(randfilename, "w")
        randfile.write(random)
        randfile.close()
        # File created
        command = "truecrypt -u -p %s  --size %s --type %s --encryption %s --hash %s --filesystem %s --keyfile '' --overwrite --random-source %s -c %s" % (self.password, self.size, voltype, ea, ha, fs, randfilename, self.path)
        input, result, errors = os.popen3(command)
        error = errors.readlines()
        if len(error) < 1:
            self._status = "unmounted"
        else:
            self._status = error
        os.remove(randfilename) # Remove the random-file
        return result.readlines()

    def frstStatus(self):
        if os.path.isfile(self.path) and password:
            return "unmounted"
        elif not password:
            return "nopass"
        elif not os.path.isfile(self.path):
            return "notfound"
        else:
            return "error"

    def open(self, target=None, mount_options=None, sudo_passwd=None):
        """
        Mounts the Container to <target> and will create the target directory if able
        """
        if target: self.target = target
        if not os.path.isdir(self.target):
            try:
                os.makedirs(self.target)
            except:
                self._error = "cannot create dir"
                return 1
        command = "truecrypt -u %s %s -p %s" % (self.path, target, self.password)
        if sudo_passwd:
            command = str("echo %s | sudo -S " % sudo_passwd) + command
        else:
            command = "sudo " + command
        if mount_options: command.join("-M %s" % mount_options)
        input, result, errors = os.popen3(command)
        error = errors.readlines()
        if len(error) < 1 or error[0] == 'Password:':
            self._status = "mounted"
        elif 'truecrypt: Volume already mapped\n' in error:
            self._status = "mounted"
        else:
            print error
            self._error = error
        return error

    def close(self, sudo_passwd=None):
        """
        Unmounts the Container
        """
        if self._status == "mounted":
            command = "truecrypt -d %s" % self.path
            if sudo_passwd:
                command = command + "echo %s | sudo -s " % sudo_passwd
            else:
                command = "sudo " + command
            input, result, errors = os.popen3(command)
            error = errors.readlines()
            print error
            if len(error) < 1:
                self._status == "unmounted"
            else:
                self._error = error
            return result
        else:
            return 0

    def __iter__(self):
        yield self.path
        yield self.target
        yield self._status

    def __str__(self):
        """
        Returns a string with "path size target"
        When there is no target or size, it will not be in the string.
        """
        string = ""
        string += self.path
        if hasattr(self, "size"): string += " " + self.size + " "
        if self.target: string += self.target
        return str(path)

if __name__ == "__main__":
    path = "test.tc"
    target = "/tmp/tc"
    password = "test"
    size = "10M"
    voltype = "normal"
    ha = "SHA-1"
    ea = "AES"
    fs = "fat"
    sudo = "foobar"

    t = TrueCrypt()
    t.open(path, password)
    print t.getList()
