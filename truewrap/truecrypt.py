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
import yaml

#TODO
# Add more filesystems for creation

class TrueCrypt (object):
    """Wrapper class to access TrueCrypt functions and to store and load options"""
    def __init__(self, sudo_passwd=None, preferences=None):
        """_containers is a list of TrueCont Objects"""
        self.__sudo_passwd = sudo_passwd
        self.__version__ = "0.2-alpha"
        self.__pref_path = self.loadPrefPath(preferences)
        self.__pref = self.loadPreferences()
        self._containers = []
        self.loadContainers()

    def loadPreferences(self):
        """Load the preferences or create a new default file"""
        try:
            f = file(self.__pref_path)
            data = yaml.safe_load(f)
        except IOError:
            return self.exceptFunc()
        return data

    def loadContainers(self):
        """Load the containers described in the yaml document self.__pref"""
        list = []
        containers = self.__pref['containers']
        if not containers:
            return list
        for c in containers:
            path = c['path']
            targ = c['target']
            self.open(path, target=targ)
        return list

    def addtoyaml(self, num):
        """Add to the options"""
        c = iter(self._containers[num])
        path = c.next()
        target = c.next()
        containers = self.__pref['containers']
        containers.append({'path': path, 'target': target})

    def save(self):
        """Refresh and save the prefences"""
        
        f = file(self.__pref_path, 'w')
        f.write(yaml.dump(self.__pref))
        f.close()

    def umountall(self):
        for c in self.getList():
            self.close(c[0])

    def exit(self):
        self.save()
        self.umountall()

    def exceptFunc(self):
        """Create a default config"""
        default="""\
containers: []\
""" 
        yamlfile = file(self.__pref_path, 'w')
        yamlfile.write(default)
        yamlfile.close()
        yamlfile = file(self.__pref_path, 'r')
        return yaml.safe_load(yamlfile)

    def loadPrefPath(self, preferences=None):
        if not preferences:
            path = os.environ['HOME'] + "/.gtruecrypt"
            if not os.path.isdir(path):
                os.makedirs(path)
            path += "/saved_containers"
            return path
        else:
            return preferences

    def getMapped(self):
        """Will Return a nice Tuple of mapped TrueCrypt objects"""
        mapped = os.popen("truecrypt --list").readlines()
        return mapped

    def create(self, path, password, voltype, size, fs, ha, ea):
        """
        Create a TrueCont Object and let it create a real TrueCrypt-container
        voltype normal or hidden
        size    in bytes or like "10M", look in TrueCrypts manpage!
        fs  fat or none # I will implement ext3 as soon as possible
        ha  Hash algorithm 
        ea  Encryption algorithm

        returns __str__ of TrueCont Object
        """
        if not self.isDouble(path):
            cont = TrueCont(path, password)
            cont.create(voltype, size, fs, ha, ea, self.__sudo_passwd)
            self._containers += [cont]
            self.addtoyaml(self._containers.index(cont))
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
            list += [(cnt, (cont.next(), cont.next(), cont.next()))]
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

    def isDouble(self, path):
        paths = set()
        for c in self._containers:
            paths.add(c.path)
        if path not in paths:
            return 0
        else:
            return 1
        

    def open(self, path, password=None, target=None):
        if not self.isDouble(path):
           cont = TrueCont(path, password, target)
           self._containers += [cont]
           self.addtoyaml(self._containers.index(cont))


class TrueCont (object):
    def __init__(self, path, password = None, target=None):
        self.path = path
        self.password = password
        self.target = target
        self._status = self.frstStatus()
        self._error = ""

    def create(self,voltype, size, fs, ha, ea, sudo_passwd=None):
        """
        voltype normal or hidden
        size    in bytes or like "10M", look in TrueCrypts Manpage!
        fs  fat or none # I will implement ext3 as soon as possible
        ha  Hash algorithm 
        ea  Encryption algorithm
        """
        assert voltype in ["normal", "hidden"], "Voltype must be of 'normal' or 'hidden'"
        assert fs in ["fat", "none"], "Filesystem must be of 'fat' or 'none'"
        import string
        from random import choice

        # Create a file in /tmp with 320 random ASCI chars to give truecrypt random input
        chars = string.letters + string.digits
        random = "".join([choice(chars) for c in xrange(320)])
        randfilename = "/tmp/randfile"
        if os.path.isfile(randfilename): os.remove(randfilename) # Delte any previous randfiles
        randfile = file(randfilename, "w")
        randfile.write(random)
        randfile.close()
        # File created
        
        self.size = size
        command = "truecrypt -u -p %s  --size %s --type %s --encryption %s --hash %s --filesystem %s --keyfile '' --overwrite --random-source %s -c %s" % (self.password, self.size, voltype, ea, ha, fs, randfilename, self.path)
        if sudo_passwd:
            command = str("echo %s | sudo -S " % sudo_passwd) + command
        else:
            command = "sudo " + command
        input, result, errors = os.popen3(command)
        error = errors.readlines()
        if len(error) < 1:
            self._status = "unmounted"
        elif error[0] == 'Password:':
            self._status == "wrongpass"
        else:
            self._status = error
        os.remove(randfilename) # Remove the random-file
        return result.readlines()

    def frstStatus(self):
        if os.path.isfile(self.path) and self.password:
            return "unmounted"
        elif not self.password:
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
    path = "/home/dax/test2.tc"
    target = "/tmp/tc2"
    password = "test"
    size = "10M"
    voltype = "normal"
    ha = "SHA-1"
    ea = "AES"
    fs = "fat"
    sudo = "jul3chen"

    t = TrueCrypt(sudo)
#    t.create(path, password, voltype, size, fs, ha, ea)
    print t.getList()
    t.save()
