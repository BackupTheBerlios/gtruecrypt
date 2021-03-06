#!/usr/bin/python
#
#	  truecrypt.py - truecrypt wrapper libary
#
#   author:	  Jens Kadenbach
#   copyright:   2007 by Jens Kadenbach
#   license:	 GNU General Public License, version 2 only
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
import re
import commands
import yaml
import tcerr
import tcresponse as response
import pexpect
import tempfile
import sys
from other import which
import gobject
import dbus
import dbus.service
import dbus.mainloop.glib

#TODO Add more filesystems for creation

class gTCd (dbus.service.Object):
	"""Wrapper class to access TrueCrypt functions and to store and load options"""
	def __init__(self, a, b, preferences=None):
		dbus.service.Object.__init__(self, a, b)
		"""_containers is a list of TrueCont Objects"""
		if not self.findBinary():
			raise TrueException.TrueCryptNotFound
		self.__version__ = "0.3-alpha"
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
		"def getList(self):""Add to the options"""
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
		#TODO: We need !!! to have a session based system.
		if not preferences:
			path = "/home/stein/.gtruecrypt"
			if not os.path.isdir(path):
				os.makedirs(path)
			path += "/saved_containers"
			return path
		else:
			return preferences

	def create(self, path, password, voltype, size, fs, ha, ea):
		"""
		Create a TrueCont Object and let it create a real TrueCrypt-container
		voltype normal or hidden
		size	in bytes or like "10M", look in TrueCrypts manpage!
		fs  fat or none # I will implement ext3 as soon as possible
		ha  Hash algorithm
		ea  Encryption algorithm

		returns __str__ of TrueCont Object
		"""
		if not self.isDouble(path):
			cont = TrueCont(path, password)
			print cont.create(voltype, size, fs, ha, ea)
			self._containers += [cont]
			self.addtoyaml(self._containers.index(cont))
			print self._containers.index(cont)
			self.save()
			return str(cont)
		else:
			return False

	def setList(self, num=None, path=None, target=None, password=None):
		"""
		Setting up allready made entries
		"""
		if not num:
			return self.open(self, path, target, password)
		else:
			cont = self._containers[num]
			if path:	cont.path	   = path
			if target:  cont.target	 = target
			if password:cont.password   = password
			return cont

	@dbus.service.method("org.gtruecrypt.daemon.getListInterface",
						 out_signature='a(i(ssss))')
	def getList(self):
		"""
		Returns a list of tuples with (Number of container, (path, target, status, error))
		"""
		list = []
		cnt = -1
		for c in self._containers:
			cnt += 1
			cont = iter(c) # Iterate through containers atributes
			list += [(int(cnt), (cont.next(), str(cont.next()), cont.next(), cont.next()))]
		return list

	@dbus.service.method("org.gtruecrypt.daemon.mountInterface")
	def mount(self, num, target=None, password=None, mount_options=None):
		"""
		mount the TrueCont to given target

		num (int) - Number of a TrueCont Object in the self._containers list
		target (str) - Target directory
		"""
		try:
			return self._containers[num].open(password, target, mount_options)
		except IndexError:
			raise TrueException.ContainerNotFound("%s not found" % num)

	@dbus.service.method("org.gtruecrypt.daemon.closeInterface",
						in_signature='i')
	def close(self, num):
		self._containers[num].close()

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
		try:
			path =  which.which('truecrypt')
			return True
		except which.WhichError:
			return False

class TrueCont (object):
	def __init__(self, path, password = None, target=None):
		self.path = path
		self.password = password
		self.target = target
		self._status = self.frstStatus()
		self._error = ''

	def __debug(child):
		raise TrueException.UnknownError("Unknown Error while creating!\
			\ndump follows: %s" % child.__str__())
		child.close()

	def create(self,voltype, size, fs, ha, ea):
		"""
		voltype normal or hidden
		size	in bytes or like "10M", look in TrueCrypts Manpage!
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
		randfile.flush()
		# File created
		self.size = size
		command = "truecrypt -u -p %s  --size %s --type %s --encryption %s --hash %s --filesystem %s --keyfile '' --overwrite --random-source %s -c %s" % (self.password, self.size, voltype, ea, ha, fs, randfile.name, self.path)
		child = pexpect.spawn(command)
		res = child.expect(
			[response.VOLUME_CREATED,
			response.EOF],
			timeout=10)

		if res in [0 ,1]:
			self._status = tcerr.umounted
			return tcerr.created
		else:
			self.__debug(child)

		#randfile.close() # Remove the tempfile

	def getMapped(self):
		"""Will Return a nice Tuple of mapped TrueCrypt objects"""
		mapped = commands.getoutput("truecrypt --list")
		return mapped

	def frstStatus(self):
		if os.path.isfile(self.path):
			# get the mapped containers
			self.mapped_result = self.getMapped()
			res = re.search(" "+self.path, self.mapped_result)
			res2 = re.search(" "+self.path+'.', self.mapped_result)
			if res == None:
				return tcerr.umounted
			else:
				if res2 == None:
					return tcerr.mounted
				return tcerr.umounted
		elif not os.path.isfile(self.path):
			return tcerr.not_found
		else:
			return tcerr.unknown_error

	def open(self, password=None, target=None, mount_options=None):
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
		if not os.path.isdir(target):
			try:
				os.makedirs(self.target)
			except:
				self._error = tcerr.cannot_create_dir
				return self._error
		if not os.path.isfile(self.path):
			self._error = tcerr.not_found
			return self._error
		command = "truecrypt -u %s %s -p %s" % (self.path, target, self.password)
		if mount_options: command.join("-M %s" % mount_options)
		child = pexpect.spawn(command)
		res = child.expect([
				response.INCORRECT_VOLUME,
				response.VOLUME_MOUNTED,
				pexpect.EOF,
				response.ALREADY_MAPPED,
				response.ENTER_SYS_PASS],
				timeout=10)
		"""
		added: wrong_password-stuff...
		"""
		if res == 0:
			self._error = tcerr.wrong_password
			return self._error
		elif res in [1, 2]:
			self._status = tcerr.mounted
			return self._status
		elif res == 3:
			self._status = tcerr.allready_mounted
			return self._status
		elif res == 4:
					raise TrueException.PrivilegeError
					return False
		else:
			return self.__debug(child)

	def close(self):
		"""
		Unmounts the Container
		"""
		if not self._status == tcerr.mounted:
			return tcerr.umounted

		command = "truecrypt -d %s" % self.path
		child = pexpect.spawn(command)
		res = child.expect([
				response.DISMOUNTING_SUCCESSFULL,
				pexpect.EOF], timeout=10)
		if res in [1, 2]:
			self._status = tcerr.umounted
			return self._status
		else:
			self.__debug(child)

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
		return str(self.path)

class TrueException(Exception):
	"""Error Class"""
	class TrueCryptNotFound(Exception):
		pass
	class PrivilegeError(Exception):
		pass
	class UnknownError(Exception):
		pass
	class AllreadyMounted(Exception):
		pass
	class ContainerNotFound(Exception):
		pass


if __name__ == '__main__':
	dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
	session_bus = dbus.SystemBus()
	name = dbus.service.BusName("org.gtruecrypt.daemon", session_bus)
	object = gTCd(session_bus, '/gTCd')
	mainloop = gobject.MainLoop()
	print "Running..."
	mainloop.run()