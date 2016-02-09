#!/usr/bin/python
from template_rule import *


# === ADD your iptables ruleset below  here === ####

os.system("iptables " + ipt_action + " " + ip + " -s " + ip + " -d 11.0.0.70/32 -p tcp --dport 80  -j ACCEPT")

# === ADD your iptables ruleset above here === ####
