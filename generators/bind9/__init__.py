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

import time

class Generator():
	def __init__(self, controller):
		self._controller = controller

	def generate(self):
		for network in self._controller.getnetworks():
			if network.hasdns():
				data = {
					"network":	network,
					"serial":	time.strftime("%Y%m%d%H"),
				}
				self._controller.instanciate("db.tmpl", "/etc/bind/db." + network.getname(), data = data)
				self._controller.instanciate("rev.tmpl", "/etc/bind/" + network.getnet().getrevrepr() + ".in-addr.arpa", data = data)

