from optparse import OptionParser

import logging as log

class Base:
	'''
	Base class for all the script. Contain some option parsing and initiation of the logger
	'''

	def __init__(self):
		self._init_option_parser_()
		self._init_logger_()
		
	def _init_logger_(self):
		options = self.get_opts()

		level = log.INFO

		if options.verbose:
			level = log.DEBUG

		if options.quiet:
			level = log.ERROR

		log.basicConfig(format=self.get_log_format(), level=level)

	def _init_option_parser_(self):
		self._parser = OptionParser()
		self._parser.add_option("-v", "--verbose" , action="store_true" , help="verbose mode")
  		self._parser.add_option("-q", "--quiet"   , action="store_true" , help="quiet mode except errors")
		self.on_create_option_parser(self._parser)
		
	def get_args(self):
		return self._args

	def get_opts(self):
		return self._opts

	def get_log_format(self):
		return '%(asctime)s %(levelname)s: %(message)s'

	def on_create_option_parser(self, parser):
		pass

	def on_start(self):
		pass

	def run(self):
		self._opts,self._args = self._parser.parse_args()

		log.debug("Start running the script")
		log.debug("Options:   %s" % self.get_opts())
		log.debug("Arguments: %s" % self.get_args())

		self.on_start()