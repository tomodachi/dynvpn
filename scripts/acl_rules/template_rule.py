import os
from sys import argv
import syslog

rule = argv[0]
ip = argv[1]
user = argv[2]

syslog.syslog("action: " + " " + rule + " on user: " + user + " ip: " + ip)
