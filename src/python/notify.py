from base import Base
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from smtplib import SMTPException

import getpass
import logging as log
import os
import smtplib
import socket

class NotifyBase(Base):
	'''
	A notification base to use when user want to send an email with some result
	'''

	def get_header(self, data):
		return """
		=====================================
		= {PID} - {TITLE}
		=====================================

		Start time: \t {START_TIME}
		Finish time: \t {FINISH_TIME}""".format(**data)

	def get_mailto(self):
		return None

	def get_message(self, data):
		return ""

	def get_footer(self, data):
		return """
		Sincerely,
		{USER}@{HOSTNAME}
		""".format(**data)

	def get_sender(self):
		return "%s@%s" % (self._get_username(), self._get_hostname())

	def get_smtp_server(self):
		return None

	def get_smtp_port(self):
		return 587

	def get_subject(self):
		return "[FINISH] %s " % self.get_title()

	def get_title(self):
		return ""

	def on_finish(self):
		log.debug("Notify system administrator")

		self.set_default_data()

		if not self._data['SMTP_SERVER']:
			log.info("SMTP server not set, skipping sending email...")
		elif not self._data['SMTP_PORT']:
			log.info("SMTP port not set, skipping sending email...")
		elif not self._data['MAILTO']:
			log.info("Receivers not set, skipping sending email... ")
		elif not self._data['SENDER']:
			log.info("Sender not set, skipping sending email... ")
		else:
			self._data['START_TIME']  = self.get_start_time()
			self._data['FINISH_TIME'] = self.get_finish_time()
			
			self._data['TITLE']    = self.get_title()
			
			self._data['PID']      = self._get_pid()
			
			self._data['HOSTNAME'] = self._get_hostname()
			self._data['USER']     = self._get_username()

			self._data['SUBJECT'] = self.get_subject()
			self._data['HEADER']  = self.get_header(self._data)
			self._data['MESSAGE'] = self.get_message(self._data)
			self._data['FOOTER']  = self.get_footer(self._data)

			message = self._get_mail_template(self._data)

			self.send_mail(self._data, message)

	def on_set_default_data(self, data):
		pass

	def send_mail(self, data, message):
		smtp_server = "%s:%s" % (data['SMTP_SERVER'], data['SMTP_PORT'])

		log.debug("Receivers - %s", data['MAILTO'])
		log.debug("Subject - %s", data['SUBJECT'])
		log.debug("Body - %s", message)
		log.debug("SMTP server - %s", smtp_server )
		receivers = ["%s" % data['MAILTO']]

		try:
			smtpObj = smtplib.SMTP(smtp_server)
			smtpObj.sendmail(data['SENDER'], receivers, message.as_string())
			smtpObj.close()
		   	log.info("Successfully sent email")
		except SMTPException, e:
		   	log.error("Unable to send email %s", e)

	def set_default_data(self):
		self._data = dict()

		self._data['SMTP_SERVER'] = self.get_smtp_server()
		self._data['SMTP_PORT']   = self.get_smtp_port()

		self._data['SENDER']      = self.get_sender()
		self._data['MAILTO']      = self.get_mailto()

		self.on_set_default_data(self._data)

	def _get_hostname(self):
		return socket.gethostname()

	def _get_mail_template(self, data):
		result = MIMEMultipart()

		result['From'] = data['SENDER']
		result['To']   = data['MAILTO']
		result['Subject'] = data['SUBJECT']
	
		body = """
		%s
		%s
		%s
		""" % (self._data['HEADER'], self._data['MESSAGE'], self._data['FOOTER'])

		result.attach(MIMEText(body, 'plain'))
	
		return result

	def _get_pid(self):
		return os.getpid()

	def _get_username(self):
		return getpass.getuser()
