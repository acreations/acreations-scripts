#!/usr/bin/python

from base import Base

import httplib
import logging as log
import re

class ExternalIPCheck(Base):

	def check_external_ip_addr(self):
		log.debug("Check external ip address")
		self._ipaddr = None
		self._ipaddr or self.source_loopia()

	def get_ipaddr(self):
		return self._ipaddr

	def on_create_option_parser(self, parser):
		parser.description = "Get the device external IP address"

	def on_start(self):
		self.check_external_ip_addr()

		log.info("Found ip address: %s" % self._ipaddr)

	def source_loopia(self):
		server = "dns.loopia.se"
		script = "/checkip/checkip.php"

		log.debug("Server: %s" % server)
		conn = httplib.HTTPConnection(server)

		log.debug("Serivce %s" % script)
  		conn.request("GET", script)

  		resp = conn.getresponse()

  		if resp.status != 200:
  			log.debug("The response from server is not valid: %s" % resp.status)
  			return None

  		result = re.findall(r'[0-9]+(?:\.[0-9]+){3}', resp.read())

  		if result:
  			self._ipaddr = result[0]

if __name__ == '__main__':
	ExternalIPCheck().run()