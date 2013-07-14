#!/usr/bin/python

from base import Base

import logging as log
import os
import os.path
import re

class ExternalDrive(Base):

	CONF_SECTION = "edrive"

	def get_disk_directory(self):
		configs = self.get_configs()

		if configs.has_option(self.CONF_SECTION, "disk_dir"):
			return configs.get(self.CONF_SECTION, "disk_dir")

		return "/dev/disk/by-id"

	def get_mount_directory(self):
		configs = self.get_configs()

		if configs.has_option(self.CONF_SECTION, "mount_dir"):
			return configs.get(self.CONF_SECTION, "mount_dir")

		return "opt/media"

	def is_truecrypt_volume(self, drive):
		configs = self.get_configs()
		option  = "%s_mount" % drive

		if configs.has_option(self.CONF_SECTION, option):
			return configs.get(self.CONF_SECTION, option).lower() == "truecrypt"

		return False

	def on_create_option_parser(self, parser):
		parser.description = "Script used to mount predefined external drives"
		parser.add_option("-m", "--mount",  action="store",      help="Mount edrive")
		parser.add_option("-u", "--umount", action="store",      help="Umount edrive")
		parser.add_option("-l", "--list",   action="store_true", help="List edrive(s)")
		parser.add_option("-a", "--avail",   action="store_true", help="Available edrive(s)")

	def on_start(self):
		self.drives = self._get_edrives()
		self._validate_or_die()

		opts = self.get_opts()

		if opts.mount:
			self.selected = self._get_selected_disks(opts.mount)
			self._validate_selected_or_die()
			self._create_directories()

			for drive in self.selected:
				source = "%s/%s" % (self.get_disk_directory(), self._get_uuid(drive))
				target = "%s/%s" % (self.get_mount_directory(), drive)

				if os.path.exists(source):
					if not os.path.ismount(target):
						if self.is_truecrypt_volume(drive):
							os.system("truecrypt %s %s" % (source, target))
						else:
							os.system("sudo mount %s %s" % (source, target))
					else:
						log.warn("Directory '%s' is already mounted", target)
				else:
					log.warn("%s is not connected to the system" % drive)

		elif opts.umount:
			self.selected = self._get_selected_disks(opts.umount)
			self._validate_selected_or_die()
			self._create_directories()

			for drive in self.selected:
				source = "%s/%s" % (self.get_disk_directory(), self._get_uuid(drive))
				target = "%s/%s" % (self.get_mount_directory(), drive)

				if os.path.exists(source):
					if not os.path.ismount(target):
						if self.is_truecrypt_volume(drive):
							os.system("truecrypt -d %s" % target)
						else:
							os.system("sudo umount %s" % target)
					else:
						log.warn("Directory '%s' is already mounted", target)
				else:
					log.warn("Edrive %s is not connected to the system" % drive)

		elif opts.list:
			print self._help_list_drives()
		elif opts.avail:
			print self._help_available_drives()
		else:
			log.error("No options given")

	def _create_directories(self):
		for drive in self.selected:
			target = "%s/%s" % (self.get_mount_directory(), drive)
			if not os.path.isdir(target):
				log.debug("Create mount directory for %s", target)
				os.system("sudo mkdir -p %s " % target)

	def _help_available_drives(self):
		drives = list()

		for drive in self.drives:
			source = "%s/%s" % (self.get_disk_directory(), self._get_uuid(drive))
			if os.path.exists(source):
				drives.append(drive)

		return '''
Available edrive(s)

%s
		''' % "\n".join(drives)

	def _help_list_drives(self):
		return '''
List edrive(s):

%s
		''' % "\n".join(self.drives)

	def _is_all_tag(self, text):
	    compare = text.lower()
	    return compare == 'all' or compare == 'a'

	def _get_selected_disks(self, disks):
		result = list()

		if self._is_all_tag(disks):
			result = self.drives
		else:
			result = re.sub(r'\s+', '', disks).split(",")
		return result

	def _get_edrives(self):
		return re.sub(r'\s+', '', self.get_configs().get(self.CONF_SECTION, "edrives")).split(",")

	def _get_uuid(self, edrive):
		configs = self.get_configs()
		if configs.has_option(self.CONF_SECTION, edrive):
			return configs.get(self.CONF_SECTION, edrive)
		return None

	def _validate_or_die(self):
		for drive in self.drives:
			if not self._get_uuid(drive):
				log.error("There does not exist a uuid option for: %s" % drive)
				exit(1)

	def _validate_selected_or_die(self):
		for drive in self.selected:
			if not drive in self.drives:
				log.error("No mapping exist for %s, exiting ... " % drive)
				exit(2)

if __name__ == '__main__':
	ExternalDrive().run()