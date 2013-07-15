from ConfigParser import SafeConfigParser
from datetime import datetime
from optparse import OptionParser

import ConfigParser
import logging as log
import os

class Base:
	'''
	Base class for all the script. Contain some option parsing and initiation of the logger
	'''

	DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
	DEFAULT_CONFIGURATION = "configuration/default"

	def _init_config_parser_(self):
		self._config = SafeConfigParser()

		options = self.get_opts()

		if options.config and os.path.isfile(options.config):
			try:
				log.info("Use configuration: %s", options.config)
				self._config.read(options.config)
			except ConfigParser.ParsingError, err:
				log.error("Cannot parse selected configuration %s" % options.config)
				exit(1)
		
		if os.path.isfile(self.DEFAULT_CONFIGURATION):
			try:
				log.info("Use default configuration: %s", self.DEFAULT_CONFIGURATION)
				self._config.read(options.config)
			except ConfigParser.ParsingError, err:
				log.error("Cannot parse default configuration %s" % self.DEFAULT_CONFIGURATION)
				exit(1)

		self.on_create_config_parser(self._config)

		return self._config


	def _init_logger_(self):
		options = self.get_opts()

		level = log.INFO

		if options.verbose:
			level = log.DEBUG

		if options.quiet:
			level = log.ERROR

		log.basicConfig(format=self.get_log_format(), level=level)

		return log

	def _init_option_parser_(self):
		OptionParser.format_epilog = lambda self, formatter: self.epilog
		
		self._parser = OptionParser(epilog=self.get_epilog())
		self._parser.add_option("-c", "--config", action="store", help="custom configuration file")
		self._parser.add_option("-v", "--verbose" , action="store_true" , help="verbose mode")
  		self._parser.add_option("-q", "--quiet"   , action="store_true" , help="quiet mode except errors")
		self.on_create_option_parser(self._parser)
		self._opts,self._args = self._parser.parse_args()

		return self._parser

	def finish(self):
		log.info("Finish running script")
		self._finish_time = datetime.now().strftime(self.DATETIME_FORMAT)
		self.on_finish()

	def file_runnable(self, fpath):
		return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

	def get_args(self):
		return self._args

	def get_configs(self):
		return self._config

	def get_epilog(self):
		result = list()
		
		help_config = self.get_help_configuration()
		if help_config:
			result.append("\nSample configurations: ")
			result.append(help_config)
			
		help_examples = self.get_help_examples()
		if help_examples:
			result.append("\nExamples: ")
			result.append(help_examples)
		
		help_footer = self.get_help_footer()
		if help_footer:
			result.append(help_footer)
	
		return "\n".join(result)

	def get_finish_time(self):
		return self._finish_time

	def get_help_configuration(self):
		return None
		
	def get_help_examples(self):
		return None
		
	def get_help_footer(self):
		return None

	def get_opts(self):
		return self._opts

	def get_log_format(self):
		return '%(asctime)s %(levelname)s: %(message)s'

	def get_start_time(self):
		return self._start_time

	def on_create_config_parser(self, config):
		pass

	def on_create_option_parser(self, parser):
		pass

	def on_finish(self):
		pass

	def on_start(self):
		pass

	def start(self):
		log.info("Start running script")
		self._start_time = datetime.now().strftime(self.DATETIME_FORMAT)
		self.on_start()

	def run(self):
		self._init_option_parser_()
		self._init_logger_()
		self._init_config_parser_()
	
		log.debug("Start running the script")
		log.debug("Options:   %s" % self.get_opts())
		log.debug("Arguments: %s" % self.get_args())

		self.start()
