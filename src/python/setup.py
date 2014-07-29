#!/usr/bin/python

from notify import NotifyBase

import imp
import logging as log
import fnmatch
import os
import socket
import sys
import time

class Setup(NotifyBase):

	CONF_SECTION = "Setup"
	CONF_ROOT    = "root"
	CONF_SAVE    = "save"

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
		parser.add_option("-r", "--run", action="store", help="Run specific (comma separated)")

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

			print "   * -> success run | - -> failed run | ? -> not run"
			print
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

		if not os.path.isdir(self._data['success']):
			os.system("mkdir -p %s" % self._data['success'])

		if not os.path.isdir(self._data['failed']):
			os.system("mkdir -p %s" % self._data['failed'])

		for conf in configs:

			if hasattr(self, 'special') and str(self.counter) not in self.special:
				self.counter += 1
				continue

			normalized = self._normalize(conf)

			directory, filename = os.path.split(os.path.realpath(conf))
				
			basename = os.path.basename(directory)

			os.chdir(directory)
		
			if os.system("python %s" % conf) == 0:
				log.info("Successfully run configuration: %s", normalized)
				self.success.append(conf)

				if os.path.isfile('%s/%s' % (self._data['success'], basename)):
					os.system('rm -f %s/%s' % (self._data['success'], basename))

				os.system('touch %s/%s' % (self._data['success'], basename))

			else:
				log.error("Failed to run configuration: %s", normalized)
				self.fails.append(conf)

				if os.path.isfile('%s/%s' % (self._data['failed'], basename)):
					os.system('rm -f %s/%s' % (self._data['failed'], basename))

				os.system('touch %s/%s' % (self._data['failed'], basename))

			self.counter += 1

		os.chdir(self._data[self.CONF_ROOT])

	def get_configurations(self, path):
		result = []
		for base, dirs, filenames in os.walk(path, followlinks=True):
			for filename in fnmatch.filter(filenames, 'configure.py'):
				result.append(os.path.realpath(os.path.join(base, filename)))

		result.sort()

		return result

	def _get_run_status(self, scriptname):

		if os.path.isfile('%s/%s' % (self._data['success'], scriptname)):
			return '*'

		if os.path.isfile('%s/%s' % (self._data['failed'], scriptname)):
			return "-"

		return "?"

	def _get_run_time(self, scriptname):

		if os.path.isfile('%s/%s' % (self._data['success'], scriptname)):
			return time.ctime(os.path.getmtime('%s/%s' % (self._data['success'], scriptname)))

		if os.path.isfile('%s/%s' % (self._data['failed'], scriptname)):
			return time.ctime(os.path.getmtime('%s/%s' % (self._data['failed'], scriptname)))

		return " " * 24

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

  No Configuration %s Run Last time run             Description
  == %s === %s %s
""" % (title, (" ") * (maximum - 14), "=" * maximum, "=" * 25, "=" * maximum)
				
		for conf in configs:
			scriptname = os.path.split(self._normalize(conf))[1]
			directory  = os.path.split(conf)[0]
			
			status   = self._get_run_status(scriptname)
			pad_num  = (" ") * (2 - len(str(self.counter)))
			pad_name = (" ") * (maximum - len(scriptname))
			run_time = self._get_run_time(scriptname)

			klass  = imp.load_source('module_%s' % scriptname, conf)

			description = "Not defined"

			if hasattr(klass, 'description'):
				description = klass.description.capitalize()

			print "  %s  %s %s  %s  %s" % (pad_num + str(self.counter), 
				scriptname + pad_name, status, run_time, description)
		
			self.counter += 1

		print

	def _set_configurations(self):
		configs = self.get_configs()

		self._data = dict()
		self._data[self.CONF_ROOT] = ""
		self._data[self.CONF_SAVE] = "/tmp"

		if configs.has_section(self.CONF_SECTION):

			if configs.has_option(self.CONF_SECTION, self.CONF_ROOT):
				self._data[self.CONF_ROOT] = configs.get(self.CONF_SECTION, self.CONF_ROOT)

			if configs.has_option(self.CONF_SECTION, self.CONF_SAVE):
				self._data[self.CONF_SAVE] = configs.get(self.CONF_SECTION, self.CONF_SAVE)

		opts = self.get_opts()

		if opts.run:
			self.special = opts.run.split()

		self._data['common'] = os.path.realpath("%s/common/configs/" % self._data[self.CONF_ROOT])
		self._data['local']  = os.path.realpath("%s/%s/configs/" % (self._data[self.CONF_ROOT], socket.gethostname()))

		self._data[self.CONF_SAVE] += "/%s" % os.path.basename(__file__)
		self._data['success'] = "%s/success" % self._data[self.CONF_SAVE]
		self._data['failed']  = "%s/failed"  % self._data[self.CONF_SAVE]

		self.counter = 1

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
