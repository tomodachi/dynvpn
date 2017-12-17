import os
from sys import argv
import syslog

rule = argv[0]
ip = argv[1]
user = argv[2]

syslog.syslog("action: " + " " + rule + " on user: " + user + " ip: " + ip)

# default rules here
os.system("nft add rule ip filter " + ip + " ip daddr { 10.0.0.1,10.0.3.254 } udp dport 53 accept")
