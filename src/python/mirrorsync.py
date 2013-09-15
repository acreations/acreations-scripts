#!/usr/bin/python

from notify import NotifyBase

import logging as log
import os	

class Mirrorsync(NotifyBase):

	CONF_SECTION = "Mirrorsync"
	CONF_SOURCE  = "SOURCE"
	CONF_TARGET  = "TARGET"
	CONF_FAILURE = "FAILURE"
	CONF_FLAGS   = "FLAGS"

	def get_help_configuration(self):
		return """
  Section must be provided
  
  [%s]
  
  config        info                              mandatory
  =========================================================
  mailto      - receivers                             *
  smtp_server                                         *
    
  SOURCE      - Backup from source                    *
  TARGET      - Sync source to directory              *
  
""" % self.CONF_SECTION

	def get_mailto(self):
		return self.get_configs().get(self.CONF_SECTION, "mailto")

	def get_message(self, data):
		return """
		Failures:    %s

		Backup from: %s
		Backup to:   %s""" % (self._temp[self.CONF_FAILURE], self._temp[self.CONF_SOURCE], self._temp[self.CONF_TARGET])

	def get_smtp_server(self):
		configs = self.get_configs()

		if self._completed and configs.has_section(self.CONF_SECTION):
			return self.get_configs().get(self.CONF_SECTION, "smtp_server")

	def get_title(self):
		return "SUMMARY OF MIRRORSYNC"

	def has_mail_configuration(self):
		return self.get_configs().has_section(self.CONF_SECTION)

	def on_create_option_parser(self, parser):
		parser.description = "Description of the script"
		parser.add_option("-s", "--source",  action="store", help="Source directory (backup from)")
		parser.add_option("-t", "--target",  action="store", help="Target directory (backup to)")

	def on_start(self):
		self._temp = dict()
		self._temp[self.CONF_TARGET] = "."

		self._read_configuration()
		self._read_options()
		self._read_flags()

		self._validate_or_die()

		self._backup()

		self.finish()

	def _backup(self):
		opts = self.get_opts();

		self._completed = False
		self._temp[self.CONF_FAILURE] = 0
		self._progress = ""

		if opts.verbose:
			self._progress = "--progress"
			self._temp[self.CONF_FLAGS] = self._temp[self.CONF_FLAGS] + "v"

		command = "rsync %s --exclude '@eaDir' --delete-after %s %s %s" % (self._temp[self.CONF_FLAGS], self._progress, self._temp[self.CONF_SOURCE], self._temp[self.CONF_TARGET])
		
		while not self._completed and self._temp[self.CONF_FAILURE] < 10:
			code = os.system(command)
		
			if (code is not 0):
				log.debug("Failures %s", self._temp[self.CONF_FAILURE])
				self._temp[self.CONF_FAILURE] += 1
			else:
				self._completed = True
			
	def _read_configuration(self):
		configs = self.get_configs()

		if configs.has_section(self.CONF_SECTION):

			if configs.has_option(self.CONF_SECTION, self.CONF_SOURCE):
				self._temp[self.CONF_SOURCE] = configs.get(self.CONF_SECTION, self.CONF_SOURCE)

			if configs.has_option(self.CONF_SECTION, self.CONF_TARGET):
				self._temp[self.CONF_TARGET] = configs.get(self.CONF_SECTION, self.CONF_TARGET)

	def _read_flags(self):
		configs = self.get_configs()

		self._temp[self.CONF_FLAGS] = "-a"

		if configs.has_section(self.CONF_SECTION):

			if configs.has_option(self.CONF_SECTION, self.CONF_FLAGS):
				self._temp[self.CONF_FLAGS] = configs.get(self.CONF_SECTION, self.CONF_FLAGS)

	def _read_options(self):
		opts = self.get_opts();

		if opts.source:
			self._temp[self.CONF_SOURCE] = opts.source

		if opts.target:
			self._temp[self.CONF_TARGET] = opts.target

	def _validate_or_die(self):
		if self.CONF_SOURCE not in self._temp:
			log.error("Source directory (backup from) is not provided")
			exit(1)
		elif not os.path.exists(self._temp[self.CONF_SOURCE]):
			log.error("Source directory (backup from) does not exist: %s", self._temp[self.CONF_SOURCE])
			exit(2)
		else:
			log.debug("Set source directory to: %s " % self._temp[self.CONF_SOURCE])

		if self.CONF_TARGET not in self._temp:
			log.error("Source directory (backup from) is not provided")
			exit(3)
		elif not os.path.exists(self._temp[self.CONF_TARGET]):
			log.error("Source directory (backup from) does not exist: %s", self._temp[self.CONF_TARGET])
			exit(4)
		else:
			log.debug("Set source directory to: %s " % self._temp[self.CONF_TARGET])

if __name__ == '__main__':
	Mirrorsync().run()
