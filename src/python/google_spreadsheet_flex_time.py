#!/usr/bin/python

from base import Base
from datetime import date

import logging as log		
import datetime
import os

class GoogleSpreadsheetFlexTime(Base):

	delimiter = "\t"

	def on_create_option_parser(self, parser):
		parser.description = "Create a tab seperate csv flex time to import to google spreadsheets"
		parser.add_option("-y", "--year",  action="store", help="year")

	def get_header(self):
		result = ['','Mon','Tue','Wed','Thu','Fri','Sat','Sun','Total','']
		return self.delimiter.join(result)

	def get_time_row(self, target):
		result = list()
		month  = target.month

		result.append('')
		for i in range(1,8):
			if i == target.isoweekday() and target.month == month:
				result.append(target.isoformat())
				target += datetime.timedelta(days=1)
			else:
				result.append('')
		result.append('')

		return self.delimiter.join(result)

	def get_lunch_time_row(self):
		result = ['Lunch extra','','','','','','','','','']
		return self.delimiter.join(result)

	def get_in_time_row(self):
		result = ['In','','','','','','','','','']
		return self.delimiter.join(result)

	def get_out_time_row(self):
		result = ['Out','','','','','','','','','']
		return self.delimiter.join(result)

	def get_total_time_row(self, row):

		actual = row + 1 # Add one extra for header

		script_day = "=calculateFlexTime(%s,%s,%s)"
		script_sum = "=SUM(%s:%s)"

		result = list()
		result.append('Total')

		for i in ('B%s','C%s','D%s','E%s','F%s','G%s','H%s'):
			result.append(script_day % (i % (actual - 3), i % (actual - 2), i % (actual - 1)))
		result.append(script_sum % ("B%s" % actual, "H%s" % actual))

		return self.delimiter.join(result)

	def get_month(self, month):
		target  = date(int(self.get_opts().year),month,1)
		result  = list()

		result.append(self.get_header())

		extra = self.delimiter + self.delimiter

		for i in range(0,10):

			result.append(self.get_time_row(target))

			result.append(self.get_in_time_row())
			result.append(self.get_out_time_row())

			result.append(self.get_lunch_time_row())
			result.append(self.get_total_time_row(len(result) + 1))

			target += datetime.timedelta(weeks=1,days=-target.weekday())

			if target.month != month:
				break

		result.insert(1, self.get_month_total_flex(len(result) + 1))

		return "\n".join(result)

	def get_month_total_flex(self, size):
		result = ['','','','','','','','','','', 'Total flex','=SUM(I1:I%s)' % size]
		return self.delimiter.join(result)

	def _create_month_csv_template(self, month):
		file = open(self.directory + '/%s.tab' % date(int(self.get_opts().year),month,1).strftime("%B")[0:3], 'w+')
		file.write(self.get_month(month))
		file.close()

	def _create_dashboard_csv_template(self):
		result = list()

		result.append(self.delimiter.join(['Month', 'Total flex']))

		for i in range(1,13):
			month  = date(int(self.get_opts().year),i,1).strftime("%B")
			short  = month[0:3]
			result.append(self.delimiter.join([month, "=%s!L2" % short]))

		result.append(self.delimiter.join(['', '']))
		result.append(self.delimiter.join(['Previous year', '']))
		result.append(self.delimiter.join(['Total this year', '=SUM(B2:B15)']))

		file = open(self.directory + '/Dashboard.tab', 'w+')
		file.write("\n".join(result))
		file.close()


	def on_start(self):
		self.validate_or_die()

		self.directory = "%s_flex_times" % self.get_opts().year

		if not os.path.exists(self.directory):
   	 		os.makedirs(self.directory)
		
   	 	for i in range(1,13):
   	 		self._create_month_csv_template(i)

   	 	self._create_dashboard_csv_template()

		log.info("You can find all csv in %s" % self.directory)

	def validate_or_die(self):
		opts = self.get_opts();

		if not opts.year:
			log.error("Year not defined")
			exit(1)


if __name__ == '__main__':
	GoogleSpreadsheetFlexTime().run()