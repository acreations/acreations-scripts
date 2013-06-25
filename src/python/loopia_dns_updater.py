from base import Base
from notify import NotifyBase
from external_ip import ExternalIPCheck

import httplib
import logging as log
import os

class LoopiaDNSUpdater(NotifyBase):

	CONF_SECTION = "Loopia DNS Updater"

	URL_DNS  = "https://dns.loopia.se/XDynDNSServer/XDynDNS.php"
	CMD_CURL = "/usr/bin/curl"		

	def get_mailto(self):
		configs = self.get_configs()

		return configs.get(self.CONF_SECTION, "mailto")

	def get_smtp_server(self):
		configs = self.get_configs()

		return configs.get(self.CONF_SECTION, "smtp_server")

	def get_title(self):
		return "SUMMARY LOOPIA DNS UPDATER"

	def get_subject(self):
		return "[%s] LOOPIA DNS UPDATER" % self._response

	def on_create_config_parser(self, config):
		if not config.has_section(self.CONF_SECTION):
			log.error("Configuration has not section %s" % self.CONF_SECTION)
			exit(1)

	def on_create_option_parser(self, parser):
		parser.description = "Update Loopia DNS"

	def on_start(self):
		#self._set_external_ip_address()
		#self._validate_or_die_ip_addr()
		self._validate_or_die_curl()
		self._validate_or_die_credentials()
		
		#command  = "curl -s --user '%s' '%s?hostname=%s&myip=%s'" % (self._credentials, self._url, self._host, self._ipAddress)
		#self._response = os.popen(command).read()
		self._response = "NOCHG"
		self.finish()

	def _set_external_ip_address(self):
		log.info("Check external ip address")

		ipChecker = ExternalIPCheck() 
		ipChecker.run()

		self._ipAddress = ipChecker.get_ipaddr()

	def _validate_or_die_curl(self):
		if not self.file_runnable(self.CMD_CURL):
			log.error("Curl does not exist or is not runnable")
			exit(4)

	def _validate_or_die_credentials(self):
		configs = self.get_configs()

		self._credentials = configs.get(self.CONF_SECTION, "credentials");
		self._host = configs.get(self.CONF_SECTION, "host");

		if not self._credentials:
			log.error("Username cannot be empty")
			exit(5)

		if not self._host:
			log.error("Password cannot be empty")
			exit(6)

		if configs.has_option(self.CONF_SECTION, "url"):
			self._url = configs.get(SELF.CONF_SECTION, "url")
		else:
			self._url = self.URL_DNS

	def _validate_or_die_ip_addr(self):
		if not self._ipAddress:
			log.error("Could not find ip address")
			exit(3)


if __name__ == '__main__':
	LoopiaDNSUpdater().run()