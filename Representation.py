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
from IPv4 import IPv4Addr, IPv4Network
from Ethernet import MacAddress
from Comparable import Comparable

_dns_name_re = re.compile(r"[a-zA-Z][a-zA-Z0-9]+")
def validdnsname(text):
	return _dns_name_re.fullmatch(text) is not None

_dns_hinfo_re = re.compile(r"[-_a-zA-Z0-9/ ]+")
def validdnshinfoentry(text):
	return _dns_hinfo_re.fullmatch(text) is not None

_dns_txt_re = re.compile(r"[-/=()+a-zA-Z0-9 @\.]+")
def validdnstxtentry(text):
	return _dns_txt_re.fullmatch(text) is not None

class DNSInfo():
	def __init__(self, xmlroot, xmlnode):
		if xmlnode.getchild("hinfo"):
			self._hinfo = (xmlnode.hinfo["arch"], xmlnode.hinfo["os"])
			if not validdnshinfoentry(self._hinfo[0]):
				raise Exception("'%s' is no valid HINFO architecture entry" % (self._hinfo[0]))
			if not validdnshinfoentry(self._hinfo[1]):
				raise Exception("'%s' is no valid HINFO operating system entry" % (self._hinfo[1]))
		else:
			self._hinfo = None

		self._text = [ ]
		if xmlnode.getchild("text"):
			for textnode in xmlnode.text:
				text = textnode["value"]
				if not validdnstxtentry(text):
					raise Exception("'%s' is no valid TXT entry" % (text))
				self._text.append(text)

		self._cnames = [ ]
		if xmlnode.getchild("cname"):
			for cnamenode in xmlnode.cname:
				cname = cnamenode["name"]
				if not validdnsname(cname):
					raise Exception("'%s' is no valid CNAME entry" % (cname))
				self._cnames.append(cname)

	def hashinfo(self):
		return self._hinfo is not None

	def hinfoarch(self):
		return self._hinfo[0]

	def hinfoos(self):
		return self._hinfo[1]

	def gettext(self):
		return iter(self._text)

	def getcnames(self):
		return iter(self._cnames)

class DHCPInfo():
	def __init__(self, xmlroot, xmlnode):
		self._range = (IPv4Addr(xmlnode.range["from"]), IPv4Addr(xmlnode.range["to"]))
		if xmlnode.getchild("broadcast"):
			self._broadcast = IPv4Addr(xmlnode.broadcast["ip"])
		else:
			self._broadcast = None

		self._dnsserver = [ ]
		if xmlnode.getchild("dnsserver"):
			for dnsserver in xmlnode.dnsserver:
				self._dnsserver.append(IPv4Addr(dnsserver["ip"]))

		if xmlnode.getchild("router"):
			self._router = IPv4Addr(xmlnode.router["ip"])
		else:
			self._router = None

		self._ntpserver = [ ]
		if xmlnode.getchild("ntpserver"):
			for ntpserver in xmlnode.ntpserver:
				self._ntpserver.append(IPv4Addr(ntpserver["ip"]))

		if xmlnode.getchild("leasetime"):
			self._leasetimedefault = int(xmlnode.leasetime["default"])
			self._leasetimemax = int(xmlnode.leasetime["max"])
		else:
			self._leasetimedefault = None
			self._leasetimemax = None

		if xmlnode.getchild("pxe"):
			self._pxefilename = xmlnode.pxe["filename"]
			self._pxenext = IPv4Addr(xmlnode.pxe["next"])
		else:
			self._pxefilename = None
			self._pxenext = None

	def getrangefrom(self):
		return self._range[0]

	def getrangeto(self):
		return self._range[1]

	def getbroadcast(self):
		return self._broadcast

	def getdnsservers(self):
		return iter(self._dnsserver)

	def getntpservers(self):
		return iter(self._ntpserver)

	def getrouter(self):
		return self._router

	def getleasetimedefault(self):
		return self._leasetimedefault

	def getleasetimemax(self):
		return self._leasetimemax

	def getpxefilename(self):
		return self._pxefilename

	def getpxenext(self):
		return self._pxenext

class DNSServerInfo():
	def __init__(self, xmlroot, xmlnode):
		self._authority = IPv4Addr(xmlnode.authority["ip"])

	def getauthority(self):
		return self._authority

class Host(Comparable):
	def __init__(self, xmlroot, xmlnode):
		self._name = xmlnode["name"]
		if not validdnsname(self._name):
			raise Exception("%s is no valid hostname" % (self._name))
		self._ip = IPv4Addr(xmlnode["ip"])
		self._mac = MacAddress(xmlnode["mac"])
		if xmlnode.getchild("dns") is not None:
			self._dns = DNSInfo(xmlroot, xmlnode.dns)
		else:
			self._dns = None
		self._network = None

	def cmpkey(self):
		return (self._ip, self._name)

	def __str__(self):
		return "%s <%s, %s>" % (self._name, self._ip, self._mac)

	def getname(self):
		return self._name

	def getip(self):
		return self._ip

	def getmac(self):
		return self._mac

	def getdns(self):
		return self._dns

	def getnetwork(self):
		return self._network

	def setnetwork(self, network):
		assert((self._network is None) and (network is not None))
		self._network = network

class Network(Comparable):
	def __init__(self, xmlroot, xmlnode):
		self._net = IPv4Network(xmlnode["subnet"])
		self._name = xmlnode["name"]
		self._hostsbyip = { }
		if xmlnode.getchild("dhcp") is not None:
			self._dhcp = DHCPInfo(xmlroot, xmlnode.dhcp)
		else:
			self._dhcp = None
		if xmlnode.getchild("dns") is not None:
			self._dns = DNSServerInfo(xmlroot, xmlnode.dns)
		else:
			self._dns = None

	def cmpkey(self):
		return self._net

	def addhost(self, host):
		self._hostsbyip[host.getip()] = host

	def getname(self):
		return self._name

	def getnet(self):
		return self._net

	def contains(self, host):
		return self._net.contains(host.getip())

	def hasdhcp(self):
		return self._dhcp is not None

	def getdhcp(self):
		return self._dhcp

	def hasdns(self):
		return self._dns is not None

	def getdns(self):
		return self._dns

	def __iter__(self):
		return iter(self._hostsbyip.values())

	def getsortedhosts(self):
		return sorted(list(self._hostsbyip.values()))

	def getnextavailableip(self):
		for ip in self._net:
			if ip not in self._hostsbyip:
				return ip
