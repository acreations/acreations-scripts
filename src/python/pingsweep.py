#!/usr/bin/python

from notify import NotifyBase

import filecmp
import logging as log
import os	
import subprocess

class Pingsweep(NotifyBase):

	CONF_SECTION = "Pingsweep"

	def get_help_configuration(self):
		return ""

	def get_mailto(self):
		return self.get_configs().get(self.CONF_SECTION, "mailto")

	def get_message(self, data):
		return """
		%s
		""" % self.RESULT

	def get_smtp_server(self):
		configs = self.get_configs()

		if self._completed and configs.has_section(self.CONF_SECTION):
			return self.get_configs().get(self.CONF_SECTION, "smtp_server")

	def get_title(self):
		return "SUMMARY OF PINGSWEEP"

	def has_mail_configuration(self):
		return self.get_configs().has_section(self.CONF_SECTION)

	def on_create_option_parser(self, parser):
		parser.description = "Description of the script"
		parser.add_option("-f", "--force",  action="store_true", help="Force to send mail updates")

	def on_start(self):
		self._locate_ip_address()

		self._validate_or_die()
		
		self._run()

		if self.TRIGGERED or self.get_opts().force:
			self.finish()
		else:
			log.debug("Ping sweep has not changed since last time")

	def _locate_ip_address(self):
		log.debug("Locate machines ip address")

		command = "ifconfig | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1'"
		process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		ip, err = process.communicate()

		if ip:
			self.IP_ADDR = ip.strip()
			log.debug("Found ipaddress: %s" % self.IP_ADDR)

	def _run(self):
		subnet  = self.IP_ADDR[:self.IP_ADDR.rindex('.')]
		command = "nmap -sP %s.1-254" % subnet
		target  = "/tmp/pingsweep"

		os.system("touch %s.new" % target)
		os.system("touch %s.old" % target)

		process  = subprocess.Popen("%s > %s.new" % (command,target), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		out, err = process.communicate()

		self._completed = False

		if not err:
			process  = subprocess.Popen("cat %s" % (target), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
			out, err = process.communicate()

			if out:
				self.RESULT     = out
				self._completed = True
			else:
				self.RESULT = "Could not find any result"	

			self.TRIGGERED = not filecmp.cmp("%s.new" % target, "%s.old" % target)

			log.debug("Host changed: %s" % self.TRIGGERED)

			os.system("mv %s.new %s.old" % (target, target))

	def _validate_or_die(self):

		if not self.IP_ADDR:
			log.error("Could not determine ipaddress of local machine")
			exit(1)

if __name__ == '__main__':
	Pingsweep().run()
