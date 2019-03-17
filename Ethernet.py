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

from RE import RE
from Comparable import Comparable

class MacAddress(Comparable):
	def __init__(self, text):
		self._text = text
		re = RE("^([0-9a-fA-F]{2})[:-]([0-9a-fA-F]{2})[:-]([0-9a-fA-F]{2})[:-]([0-9a-fA-F]{2})[:-]([0-9a-fA-F]{2})[:-]([0-9a-fA-F]{2})$")
		self._required(re.match(text))

		self._mac = [ int(x, 16) for x in re.getall() ]
		self._required([ 0 <= x <= 255 for x in self._mac ])

	def _required(self, condition):
		if not condition:
			raise Exception("%s is not a valid ethernet MAC address." % (self._text))

	def cmpkey(self):
		return tuple(self._mac)

	def __str__(self):
		return ":".join([ "%02x" % (x) for x in self._mac ])

if __name__ == "__main__":
	x = MacAddress("00:1A:22:33-44:55")
	y = MacAddress("00:1a:22-33-44:55")
	print(x, y)
	print(x == x, x != x)
	print(y == y, y != y)
	print(x < y, x == y, x != y)
