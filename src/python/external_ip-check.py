from base import Base

import httplib
import re

class ExternalIPCheck(Base):

	def check_external_ip_addr(self):
		self._ipaddr = None
		self._ipaddr or self.source_loopia()

	def get_ipaddr(self):
		return self._ipaddr

	def on_create_option_parser(self, parser):
		parser.description = "Get the device external IP address"

	def on_start(self):
		self.check_external_ip_addr()

		print get_ipaddr()

	def source_loopia(self):
		conn = httplib.HTTPConnection("dns.loopia.se")
  		conn.request("GET", "/checkip/checkip.php")

  		resp = conn.getresponse()

  		if resp.status != 200:
  			return None

  		result = re.findall(r'[0-9]+(?:\.[0-9]+){3}', response.read())

  		if result:
  			self._ipaddr = result[0]

ExternalIPCheck().run()