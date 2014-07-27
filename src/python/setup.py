#!/usr/bin/python

from notify import NotifyBase

import imp
import logging as log
import fnmatch
import os
import socket
import sys

class Setup(NotifyBase):

	CONF_SECTION = "Setup" 
	CONF_ROOT    = "root"

	success = list()
	fails   = list()

	def get_mailto(self):
		return self.get_configs().get(self.CONF_SECTION, "mailto")

	def get_message(self, data):
		return """
		Commmon: %s
		Local  : %s

		Success: %s
		Failed : %s""" % (len(self.common), len(self.local), len(self.success), len(self.fails))

	def get_smtp_server(self):
		if self.get_configs().has_option(self.CONF_SECTION, "smtp_server"):
			return self.get_configs().get(self.CONF_SECTION, "smtp_server")

	def get_title(self):
		return "SUMMARY OF SETUP"

	def has_mail_configuration(self):
		return self.get_configs().has_section(self.CONF_SECTION)

	def on_create_option_parser(self, parser):
		parser.description = "Description of the script"
		parser.add_option("-l", "--list", action="store_true", help="List configurations")
		parser.add_option("-r", "--root", action="store", help="Root path of configurations")

	def on_start(self):
		self._set_configurations()
		self._validate_or_die()

		self.common = self.get_configurations(self._data['common'])
		self.local  = self.get_configurations(self._data['local'])

		opts = self.get_opts()

		if opts.list:
			if self.common:
				self._print_configuration(self.common, "Common configurations:")
			
			if self.local:
				self._print_configuration(self.local,  "Local configurations:")

			print "   * -> run      - -> not run "
		else:
			self.run_configure()		

	def run_configure(self):
		log.info("Root script directory: %s", self._data[self.CONF_ROOT])

		log.info("Found %s common configurations" % len(self.common))
		self.setup(self.common)

		log.info("Found %s local configurations" % len(self.local))
		self.setup(self.local)

		self.finish()

	def setup(self, configs):
		for conf in configs:
			normalized = self._normalize(conf)

			directory, filename = os.path.split(os.path.realpath(conf))
				
			os.chdir(directory)
		
			if os.system("%s" % conf) == 0:
				log.info("Successfully run configuration: %s", normalized)
				self.success.append(conf)
			else:
				log.error("Failed to run configuration: %s", normalized)
				self.success.append(conf)

		os.chdir(self._data[self.CONF_ROOT])


	def get_configurations(self, path):
		result = []
		for base, dirs, filenames in os.walk(path, followlinks=True):
			for filename in fnmatch.filter(filenames, 'configure.py'):
				result.append(os.path.realpath(os.path.join(base, filename)))
		return result

	def _normalize(self, path):
		result = path
		result = result.replace(self._data['common'], "")
		result = result.replace(self._data['local'], "")
		result = result.replace("/configure.py", "")

		return result

	def _print_configuration(self, configs, title):
		maximum = len(max([os.path.split(self._normalize(c))[1] for c in configs], key=len)) + 1

		print """
%s

  Run %s Description
  === %s %s
""" % (title, "Scriptname" + (" ") * (maximum - len("Scriptname")), "=" * maximum, "=" * maximum)
				
		for conf in configs:
			scriptname = os.path.split(self._normalize(conf))[1]
			directory  = os.path.split(conf)[0]
			
			klass = imp.load_source('module_%s' % scriptname, conf).ConfigRunner()
			
			print "   %s  %s %s" % ("*" if klass.has_run() else "-", 
				scriptname + (" ") * (maximum - len(scriptname)), klass.get_description())
		
		print

	def _set_configurations(self):
		configs = self.get_configs()

		self._data = dict()
		self._data[self.CONF_ROOT] = ""

		if configs.has_section(self.CONF_SECTION):

			if configs.has_option(self.CONF_SECTION, self.CONF_ROOT):
				self._data[self.CONF_ROOT] = configs.get(self.CONF_SECTION, self.CONF_ROOT)

		opts = self.get_opts()

		if opts.root:
			self._data[self.CONF_ROOT] = opts.root

		self._data['common'] = os.path.realpath("%s/common/configs/" % self._data[self.CONF_ROOT])
		self._data['local']  = os.path.realpath("%s/%s/configs/" % (self._data[self.CONF_ROOT], socket.gethostname()))

	def _validate_or_die(self):
		if not self._data[self.CONF_ROOT]:
			log.error("Root path for configurations not set")
			exit(1)

		if not os.path.isdir(self._data[self.CONF_ROOT]):
			log.error("Root path for configurations does not exist")
			exit(2)
			
		self._data[self.CONF_ROOT] = os.path.realpath(self._data[self.CONF_ROOT])


if __name__ == '__main__':
	Setup().run()
