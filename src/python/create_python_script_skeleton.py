#!/usr/bin/python

from base import Base

import logging as log
import os 

class CreatePythonScriptSkeleton(Base):

	SCRIPT_SKELETON_BASE   = "create_python_script_base"
	SCRIPT_SKELETON_NOTIFY = "create_python_script_notify" 

	PYTHON_EXT = ".py"

	def on_create_option_parser(self, parser):
		parser.description = "Generate a skeleton for python script"
		parser.add_option("-n", "--name",   action="store",      help="script name")
		parser.add_option("",   "--notify", action="store_true", help="notify base")

	def on_start(self):
		self._validate_or_die()
		self._sanitize_script_name()

		log.info("Create script with name: '%s'" % self._target_name)

		self._basepath = os.path.dirname(os.path.realpath(__file__))
		self._skeleton = self._get_skeleton_file_path()
		self._target   = self._target_name + self.PYTHON_EXT
		self._class    = self._convert_to_class_name()

		f = file(self._skeleton, "r")
		skeleton = f.read().format(CLASS_NAME=self._class)
		f.close()

		f = file(self._target, "w")
		f.write(skeleton)
		f.close()

		os.system("chmod 755 %s" % self._target)

	def _convert_to_class_name(self):
		result = self._target_name

		result = result.replace("_", " ")
		result = result.title()
		result = result.replace(" ", "")

		return result

	def _get_skeleton_file_path(self):
		opts = self.get_opts()

		result = self._basepath + os.sep

		if opts.notify:
			result = result + self.SCRIPT_SKELETON_NOTIFY
		else:
			result = result + self.SCRIPT_SKELETON_BASE

		return result


	def _sanitize_script_name(self):
		if self._target_name.endswith(self.PYTHON_EXT):
			self._target_name = self._target_name[:-3]

	def _validate_or_die(self):
		opts = self.get_opts()

		if not opts.name:
			log.error("The script must have a name")
			exit(1);

		self._target_name = opts.name

if __name__ == '__main__':
	CreatePythonScriptSkeleton().run()