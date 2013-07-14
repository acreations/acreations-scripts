#!/usr/bin/python

from base import Base

import logging as log		
import os

class Config(Base):

	def get_description(self):
		return "Base class for configuration"

	def has_run(self):
		return False

	def on_create_option_parser(self, parser):
		parser.description = self.get_description()
		parser.add_option("-f", "--force", action="store_true", help="Force run configuration")

	def on_start(self):
		name = self.get_description()
		opts = self.get_opts()

		if self.validate():
			if not self.has_run() or opts.force:
				log.info("Configure: %s" % name)
				self.run_configuration()
				self.finish()
			else:
				log.info("configuration '%s' has already run" % name)
		else:
			log.warn("Validation failed for configuration '%s'" % name)

	def run_command(self, command):
		if self.sudo_needed():
			log.debug("Running command as sudo")
			os.system("sudo %s" % command)
		else:
			os.system(command)
		
		self.finish()

	def sudo_needed(self):
		return False

	def validate(self):
		'''
		Validate if the script should run or not, must be provided otherwise
		always failing
		'''
		return False

	def run_configuration(self):
		pass

