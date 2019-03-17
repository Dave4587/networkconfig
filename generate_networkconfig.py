#!/usr/bin/python3
import os
import sys
import argparse
from XMLParser import XMLParser
from Representation import Host, Network
from Controller import Controller

parser = argparse.ArgumentParser(prog = sys.argv[0], description = "Server configuration file generator", add_help = True)
parser.add_argument("infile", metavar = "filename", type = str, help = "Input XML filename")
#parser.add_argument("-args", metavar = "dict", type = str, help = "Passes a Python dictionary which is available as reference from within scripts")
parser.add_argument("-gendir", metavar = "path", type = str, help = "Input directory where generator file are located (default is %(default)s", default = "generators/")
parser.add_argument("-outdir", metavar = "path", type = str, help = "Output directory to put files in (default is %(default)s", default = "outdir/")
args = parser.parse_args(sys.argv[1:])


# Load data from XML
xml = XMLParser().parsefile(args.infile)
hosts = set()
for host in xml.hosts.host:
	hosts.add(Host(xml, host))

networks = set()
for network in xml.networks.network:
	networks.add(Network(xml, network))

# Resolve that every host is in exactly one network
for host in hosts:
	contained = False
	for network in networks:
		if network.contains(host):
			contained = True
			host.setnetwork(network)
			network.addhost(host)
	if not contained:
		raise Exception("Host %s with IP %s is not contained within any declared network." % (host.getname(), host.getip()))

# Ensure that network suffixes are unique
netnames = set()
for network in networks:
	if network.getname() in netnames:
		raise Exception("Duplicate network name: %s" % (network.getname()))
	netnames.add(network.getname())

# Ensure that names are unique within networks
for network in networks:
	names = set()
	for host in network:
		if host.getname() in names:
			raise Exception("Duplicate hostname: %s.%s" % (host.getname(), network.getname()))
		names.add(host.getname())

# Ensure that MAC and IP addresses are unique within the whole config domain
macs = { }
ips = { }
for host in hosts:
	if host.getmac() in macs:
		raise Exception("Duplicate MAC address: %s by %s collides with %s" % (host.getmac(), str(host), str(macs[host.getmac()])))
	if host.getip() in ips:
		raise Exception("Duplicate IP address: %s by %s collides with %s (next available is %s)" % (host.getip(), str(host), str(ips[host.getip()]), host.getnetwork().getnextavailableip()))
	ips[host.getip()] = host
	macs[host.getmac()] = host

def getgenerator(basedir, modname):
	oldpath = list(sys.path)
	sys.path = [ basedir ]
	module = __import__(modname)
	sys.path = oldpath
	return module.Generator


# Prepare generator controller data
data = {
	"hosts":		hosts,
	"networks":		networks,
}

# Load generators
for generatorname in os.listdir(args.gendir):
	genclass = getgenerator(args.gendir, generatorname)

	# Prepare specific controller
	ctrl = Controller(generatorname, data, args)
	
	# Instanciate generator and execute
	generator = genclass(ctrl)
	generator.generate()

