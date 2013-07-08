#!/usr/bin/python

from config import Config
from os import path, access, R_OK 

import logging as log

class ConfigFileUpdater(Config):

	PATTERN   = "########## %s - %s ##########"
	TEMP_FILE = "update.tmp" 

	def has_run(self):
		target = open(self.get_file_source(), 'r').read()
		return (target.find(self._get_header()) >= 0) or (target.find(self._get_footer()) >= 0)

	def get_file_source(self):
		return None

	def get_file_update(self):
		return "update"

	def get_mark_tag(self):
		return "change it"

	def run_configuration(self):
		self._save_source_content()

		command = "mv %s %s" % (self.TEMP_FILE, self.get_file_source())

		self.run_command(command)

	def validate(self):
		source = self.get_file_source()
		update = self.get_file_update()

		validate_source = source and path.isfile(source) and access(source, R_OK)
		validate_update = update and path.isfile(update) and access(update, R_OK)

		if not validate_source:
			log.warn("Source does not exist or is not accessible")

		if not validate_update:
			log.warn("Update does not exist or is not accessible")

		return validate_source and validate_update

	def _get_header(self):
		return self.PATTERN % ("HEADER", self.get_mark_tag())

	def _get_footer(self):
		return self.PATTERN % ("FOOTER", self.get_mark_tag())

	def _read_source(self):
		source = open(self.get_file_source(), "r")

		result = list()
		header = self._get_header()
		footer = self._get_footer()

		skip   = False
		for line in source:
			if header in line:
				log.debug("Found header (%s)", header)
				skip  = True
			elif footer in line:
				log.debug("Found footer (%s)", footer)
				skip = False
			elif skip:
				log.debug("Skipping line: " + line)
			else:
				result.append(line)

		source.close()

		return result

	def _read_update(self):
		update = open(self.get_file_update(), "r")
		result = update.read()
		update.close()
		return result

	def _save_source_content(self):
		source = self._read_source()
		update = self._read_update()
		target = open(self.TEMP_FILE, "w+")

		source.append(self._get_header() + "\n")
		source.append(update)
		source.append(self._get_footer() + "\n")

		target.write(''.join(source))
		target.close()