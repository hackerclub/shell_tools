#!/usr/bin/env python

import os
import sys
import json
import subprocess
import time

serviceHash = {}

err = lambda v: sys.stderr.write("[-] %s\n" % v)

def die(v):
	err(v)
	sys.exit(1)

def loadServices():
	global serviceHash

	f = open("/etc/services")
	lines = f.read().split("\n")

	for line in lines:
		if not line.startswith("#") and line != '':
			parts = line.split()
			service = parts[0]
			port = parts[1].split("/")[0]
			serviceHash[service] = port

	# add a link to dns, coz no one calls it 'domain'
	serviceHash['dns'] = '53'
	serviceHash['rdp'] = '3389'

def pingCheck(host):
	cmd = "ping -c 1 %s" % host
	try:
		subprocess.check_output(cmd.split())
	except subprocess.CalledProcessError:
		return ("-", "closed", "ping")

	return ("-", "open", "ping")

def serviceCheck(host, services):
	ports = []
	portMapping = {}
	try:
		for service in services:
			port = serviceHash[service]
			portMapping[port] = service
			ports.append(port)	
	except KeyError as e:
		die("unable to find port for service " + str(e) + ", try finding the proper service name in /etc/services")

	portListing = ",".join(map(str, ports))

	cmd = "nmap -T4 -sS -p %s %s" % (portListing, host)
	try:
		out = subprocess.check_output(cmd.split())
	except:
		die("call to nmap -sS errored, are you sure you are root?")

	down = False
	# process the output
	try:
		services = out.split("SERVICE")[1].split("MAC")[0].split("\n")[1:-1]
	except: # probably host is down
		down = True

	stateList = []
	if not down:
		for service in services:
			port, state, _ = service.split()
			port = port.split("/")[0]
			stateList.append((port, state, portMapping[port]))
	else:
		for port in portMapping.keys():
			stateList.append((port, "closed", portMapping[port]))
		

	return stateList

def main(argc, argv):
	loadServices()

	hostFile = 'hosts.json'
	if (argc > 1):
		hostFile = argv[1]



	os.system("clear")
	while True:
		report = ""
		report += time.ctime() + "\n\n"
		hosts = json.loads(open(hostFile).read())
		for host in hosts.keys():
			services = hosts[host]
			ports = []

			# so dumb~
			# ping check
			special = ""
			if ("icmp" in services):
				special = "icmp"
			if ("ping" in services):
				special = "ping"

			if special != "":
				ports.append(pingCheck(host))
				del services[services.index(special)]

			ports += serviceCheck(host, services)
				
			report += host + ":\n"
			for port in ports:
				# add cool coloring here
				state = port[1]
				if state == 'open':
					color = "\033[01;32m"
				else:
					color = "\033[01;31m"
				state = state.ljust(6, " ")
				sport  = port[0].ljust(5, " ")
				report += "  %s%s\033[01;0m %s %s\n" % (color, state.upper(), sport, port[2])
			report += "\n"

		os.system("clear")
		print report
		time.sleep(30)

if __name__ == "__main__":
	main(len(sys.argv), sys.argv)
