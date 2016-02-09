import os
from sys import argv
import syslog


class Action_enum:
    ADD = "add"
    UPDATE = "update"
    DELETE = "delete"

action_ENUM = Action_enum()

ipt_action = ""

rule = argv[0]
action = argv[1]
ip = argv[2]
user = argv[3]

# decide if we will add the fw acl ruleset or remove
# the ruleset for the user
if action == action_ENUM.ADD:
    ipt_action = "-A"
if action == action_ENUM.DELETE:
    ipt_action = "-D"

syslog.syslog("action: " + ipt_action + " " + rule + " on user: " +
              user + " ip: " + ip)
