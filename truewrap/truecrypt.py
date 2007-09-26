#!/usr/bin/python 
#
#      truecrypt.py - truecrypt wrapper libary
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
import yaml
import tcerr
import tcresponse as response
import pexpect
import tempfile
import sys

#TODO Add more filesystems for creation

class TrueCrypt (object):
    """Wrapper class to access TrueCrypt functions and to store and load options"""
    def __init__(self, sudo_passwd=None, preferences=None):
        """_containers is a list of TrueCont Objects"""
        if not self.findBinary():
            raise TrueException.TrueCryptNotFound
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
        dict = {'path': path, 'target': target}
        if dict in containers: return False # Dont write in in twice!
        containers.append(dict)

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
        else:
            return False

    def getList(self):
        """
        Returns a list of tuples with (Number of container, (path, target, status, error))
        """
        list = []
        cnt = -1
        for c in self._containers:
            cnt += 1
            cont = iter(c) # Iterate through containers atributes
            list += [(cnt, (cont.next(), cont.next(), cont.next(), cont.next()))]
        return list

    def mount(self, num, target=None, password=None, mount_options=None):
        """
        mount the TrueCont to given target

        num (int) - Number of a TrueCont Object in the self._containers list
        target (str) - Target directory
        """
        return self._containers[num].open(password, target, mount_options, self.__sudo_passwd)    

    def close(self, num):
        self._containers[num].close(self.__sudo_passwd)

    def isDouble(self, path):
        paths = set()
        for c in self._containers:
            paths.add(c.path)
        if not path in paths:
            return 0
        else:
            return 1

    def open(self, path, password=None, target=None):
        if not self.isDouble(path):
           cont = TrueCont(path, password, target)
           self._containers += [cont]
           self.addtoyaml(self._containers.index(cont))

    def findBinary(self):
        for path in  os.defpath.split(':')[1:]:
            path.join('truecrypt')
            if os.path.isfile(path):
                return True
        return False

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
        if not voltype in ["normal", "hidden"]:
            return tcerr.voltype
        if not fs in ["fat", "none"]:
            return tcerr.filesystem
        import string
        from random import choice

        # Create a file in /tmp with 320 random ASCI chars to give truecrypt random input
        chars = string.letters + string.digits
        random = "".join([choice(chars) for c in xrange(320)])
        randfile = tempfile.NamedTemporaryFile()
        randfile.write(random)
        # File created
        def create_sudo(self, child):
            """packed into a function because we maybe need to call it again and again..."""
            res = child.expect([response.ENTER_SUDO_PASSWORD, response.SUDO_WRONG_PASSWORD, response.VOLUME_CREATED, response.EOF], timeout=200)
            if res == 0:
                child.sendline(sudo_passwd)
                self.create_sudo(child)
            elif res == 1:
                os.remove(randfilename) # Remove the random-file
                self._error = tcerr.missing_sudo
                self._status = tcerr.missing_sudo
                child.close()
                return self._error
            elif res == 2 or res == 3:
                os.remove(randfilename) # Remove the random-file
                self._status = tcerr.umounted
                return tcerr.created
            else:
                os.remove(randfilename) # Remove the random-file 
                print "DEBUGGING INFORMATION"
                print 
                print child
                return tcerr.unknown_error
 
        self.size = size
        command = "sudo truecrypt -u -p %s  --size %s --type %s --encryption %s --hash %s --filesystem %s --keyfile '' --overwrite --random-source %s -c %s" % (self.password, self.size, voltype, ea, ha, fs, randfile.name, self.path)
        child = pexpect.spawn(command)
        create_sudo(self, child) 
        randfile.close() # Remove the tempfile

    def frstStatus(self): # TODO implement searching if it is mounted
        if os.path.isfile(self.path):
            return tcerr.umounted
        elif not os.path.isfile(self.path):
            return tcerr.not_found
        else:
            return tcerr.unknown_error

    def open(self, password=None, target=None, mount_options=None, sudo_passwd=None):
        """
        Mounts the Container to <target> and will create the target directory if able
        """
        if password:
            self.password = password
        if not self.password:
            self._error = tcerr.missing_password
            return self._error
        if target:
            self.target = target
        if not self.target:
            self._error = tcerr.no_target
            return self._error
        if not os.path.isdir(self.target):
            try:
                os.makedirs(self.target)
            except:
                self._error = tcerr.cannot_create_dir
                return self._error
        command = "sudo  truecrypt -u %s %s -p %s" % (self.path, target, self.password)
        if mount_options: command.join("-M %s" % mount_options)
        def mount_sudo(self, child, sudo_passwd=None):
            """packed into a function because we maybe need to call it again and again..."""
            res = child.expect([response.ENTER_SUDO_PASSWORD, response.SUDO_WRONG_PASSWORD, response.VOLUME_MOUNTED, pexpect.EOF, response.ALREADY_MAPPED], timeout=200)
            if res == 0:
                if not sudo_passwd:
                    return tcerr.missing_sudo
                child.sendline(sudo_passwd)
                return mount_sudo(self, child)
            elif res == 1:
                self._error = tcerr.missing_sudo
                self.kill_sudo(child.pid, sudo_passwd)
                return self._error
            elif res == 2 or res == 3:
                self._status = tcerr.mounted
                return self._status
            elif res == 4:
                self._status = tcerr.allready_mounted
                return self._status
            else:
                print "DEBUGGING INFORMATION"
                print 
                print child
                child.close()
                return tcerr.unknown_error

        child = pexpect.spawn(command)
        mount_sudo(self, child, sudo_passwd)
 
    def close(self, sudo_passwd=None):
        """
        Unmounts the Container
        """
        def close_sudo(self, child, sudo_passwd=None):
            """packed into a function because we maybe need to call it again and again..."""
            res = child.expect([response.ENTER_SUDO_PASSWORD, response.SUDO_WRONG_PASSWORD, response.DISMOUNTING_SUCCESSFULL, pexpect.EOF], timeout=200)
            if res == 0:
                if not sudo_passwd:
                    return tcerr.missing_sudo
                child.sendline(sudo_passwd)
                return close_sudo(self, child)
            elif res == 1:
                self._error = tcerr.missing_sudo
                self.kill_sudo(child.pid)
                return self._error
            elif res == 2 or res == 3:
                self._status = tcerr.umounted
                return self._status
            else:
                print "DEBUGGING INFORMATION"
                print 
                print child
                child.close()
                return tcerr.unknown_error
        command = "sudo truecrypt -d %s" % self.path
        child = pexpect.spawn(command)
        close_sudo(self, child, sudo_passwd)

    def __iter__(self):
        yield self.path
        yield self.target
        yield self._status
        yield self._error

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

    def kill_sudo(self, pid, sudo_passwd=None):
        """extra function to kill a priviliged process"""
        def killchild_sudo(child):
            res = child.expect([response.ENTER_SUDO_PASSWORD, response.SUDO_WRONG_PASSWORD, pexpect.EOF], timeout=10)
            if res == 0:
                if not sudo_passwd:
                    return tcerr.missing_sudo
                child.sendline(sudo_passwd)
                return killchild_sudo(self, child)
            elif res == 1:
                self._error = tcerr.missing_sudo
                child.close()
                return self._error
            elif res == 2:
                return True
            else:
                print "DEBUGGING INFORMATION"
                print 
                print child
                child.close()
                return tcerr.unknown_error

        command = "sudo kill -9 %s" % pid
        child = pexpect.spawn(command)
        return killchild_sudo(child)

class TrueException(Exception):
    """Error Class"""
    class TrueCryptNotFound(Exception):
        sys.stderr.write("Error: truecrypt binary was not found!\n")

if __name__ == "__main__":
    path = "/home/dax/test1.tc"
    target = "/tmp/tc2"
    passwd = "test"
    size = "10M"
    voltype = "normal"
    ha = "SHA-1"
    ea = "AES"
    fs = "fat"
    sudo = "blub"

    t = TrueCrypt(sudo)
    print t.getList()
    t.mount(0, target, passwd)
    print t.getList()
    t.close(0)
    print t.getList()
    t.save() 
