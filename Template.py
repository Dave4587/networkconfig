#	networkconfig - Generator for home router configuration and networks
#	Copyright (C) 2012-2019 Johannes Bauer
#
#	This file is part of networkconfig.
#
#	networkconfig is free software; you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation; this program is ONLY licensed under
#	version 3 of the License, later versions are explicitly excluded.
#
#	networkconfig is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with networkconfig; if not, write to the Free Software
#	Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#	Johannes Bauer <JohannesBauer@gmx.de>

import sys

import mako.template, mako.exceptions
from mako.lookup import TemplateLookup

from Logger import Logger
from TabFormat import TabFormat
from CppFormatter import CppFormatter

class Template():
	def __init__(self, filename):
		lookupdir = "templates/"
		lookup = TemplateLookup([ lookupdir ])
		self._template = mako.lookup.Template(open(lookupdir + filename, "r").read(), lookup = lookup)
		self._t = TabFormat([ 65, 81 ])
		self._log = Logger()[self.__class__.__name__]

	def _tabformat(self, s):
		return self._t.format(s)

	def render(self, **args):
		parameters = {
			"tab": self._tabformat,
		}
		parameters.update(args)
		try:
			renderresult = self._template.render(**parameters)
		except:
			self._log.critical("Templating error, cannot continue. Mako-decoded stacktrace follows:")
			self._log.critical(mako.exceptions.text_error_template().render())
			sys.exit(1)

		cppfmt = CppFormatter()
		output = cppfmt.format(renderresult.split("\n"))
		renderresult = output.getvalue()

		return renderresult
