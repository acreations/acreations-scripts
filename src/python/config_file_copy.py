#!/usr/bin/python

from config import Config
from os import path, access, R_OK 

import logging as log

class ConfigFileCopy(Config):

	def has_run(self):
		return path.isfile(self.get_file_target())

	def get_file_target(self):
		return None

	def get_file_source(self):
		return "source"

	def run_configuration(self):
		command = "cp %s %s" % (self.get_file_source(), self.get_file_target())	

		self.run_command(command)

	def validate(self):
		source = self.get_file_source()

		validate_source = source and path.isfile(source) and access(source, R_OK)

		if not validate_source:
			log.warn("Source does not exist or is not accessible")

		return validate_source