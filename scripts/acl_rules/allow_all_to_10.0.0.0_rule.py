#!/usr/bin/python
from template_rule import *

# === ADD your iptables ruleset below  here === ####

os.system("iptables " + ipt_action + " " + ip + " -s " + ip + " -d 10.0.0.0/24 -j ACCEPT")

# === ADD your iptables ruleset above here === ####
