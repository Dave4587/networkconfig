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

import re
from Comparable import Comparable

class IPv4Addr(Comparable):
	_ipv4_re = re.compile(r"(\d+)\.(\d+)\.(\d+)\.(\d+)")

	def __init__(self, text = None):
		self._text = text
		if text is not None:
			match = self._ipv4_re.fullmatch(text)
			self._require(match is not None)
			(v1, v2, v3, v4) = [ int(x) for x in match.groups() ]
			self._require(all(0 <= x <= 255 for x in [ v1, v2, v3, v4 ]))
			self._ip = (v1 << 24) | (v2 << 16) | (v3 << 8) | (v4 << 0)
		else:
			self._ip = 0
		self._text = None

	def cmpkey(self):
		return self._ip

	def _require(self, condition):
		if not condition:
			raise Exception("%s is no valid IPv4 address." % (self._text))

	def setdecimal(self, value):
		assert(isinstance(value, int))
		assert(0 <= value <= ((2 ** 32) - 1))
		self._ip = value
		return self

	def get(self):
		return self._ip

	def revrepr(self):
		return "%d.%d.%d.%d" % ((self._ip >> 0) & 0xff, (self._ip >> 8) & 0xff, (self._ip >> 16) & 0xff, (self._ip >> 24) & 0xff)

	def __str__(self):
		return "%d.%d.%d.%d" % ((self._ip >> 24) & 0xff, (self._ip >> 16) & 0xff, (self._ip >> 8) & 0xff, (self._ip >> 0) & 0xff)

class IPv4Network(Comparable):
	_ipv4_net_re = re.compile(r"([0-9.]+)/(\d+)")

	def __init__(self, text):
		self._text = text
		match = self._ipv4_net_re.fullmatch(text)
		self._required(match is not None)
		match = match.groups()

		try:
			self._net = IPv4Addr(match[0])
		except Exception:
			self._net = None
		self._required(self._net is not None)

		cidr = int(match[1])
		self._required(0 <= cidr <= 32)

		self._mask = IPv4Addr()
		maskval = (1 << cidr) - 1
		invmaskval = 0
		for i in range(32):
			if maskval & (1 << (31 - i)):
				invmaskval |= (1 << i)
		self._mask.setdecimal(invmaskval)

		self._required(self._mask.get() & self._net.get() == self._net.get())
		self._text = None

	def getcidr(self):
		mask = self._mask.get()
		cidr = 0
		while mask != 0:
			if mask & (1 << 31):
				cidr += 1
			else:
				# Not a CIDR network!
				return None
			mask = (mask << 1) & 0xffffffff
		return cidr

	def cmpkey(self):
		return (self._net, self._mask)

	def getnet(self):
		return self._net

	def getmask(self):
		return self._mask

	def getrevrepr(self):
		assert(self.getcidr() in [ 8, 16, 24 ])
		split = self._net.revrepr().split(".")[-self.getcidr() // 8:]
		return ".".join(split)

	def _required(self, condition):
		if not condition:
			raise Exception("%s is no valid short IPv4 network declaration." % (self._text))

	def contains(self, ip):
		return (ip.get() & self._mask.get()) == self._net.get()

	def __iter__(self):
		current = self.getnet().get() + 1
		maxnet = self.getnet().get() + ((~self.getmask().get()) & 0xffffffff)
		while current < maxnet:
			yield IPv4Addr().setdecimal(current)
			current += 1

	def __str__(self):
		return "%s/%s" % (self._net, self._mask)

if __name__ == "__main__":
	x = IPv4Addr("1.02.3.255")
	y = IPv4Network("192.168.1.0/24")
	print(x, y)
	print(x, y.contains(x))
	x = IPv4Addr("192.168.1.44")
	print(x, y.contains(x))
	x = IPv4Addr("192.168.2.44")
	print(x, y.contains(x))

	print(IPv4Network("10.0.0.0/8").getrevrepr())
	print(IPv4Network("172.16.0.0/16").getrevrepr())
	print(IPv4Network("192.168.123.0/24").getrevrepr())
	print(IPv4Network("192.168.99.128/25").getrevrepr())
