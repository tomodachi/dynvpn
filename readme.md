### dynvpn ###

dynvpn is a set of small python programs for dynamicaly generating a iptables ruleset for a connected users ip
based on what acl_group(s) the connecting user belongs to. This proves quite usefull to get a more "enterprisey VPN"
where you often want to limit access to network resources based on your criterias.

# Requirements:
- iptables
- openvpn
- python



# Openvpn client connection state transition

1.  User connects to OpenVPN server
2.  User is verified with private cert key and possibly more depending on your setup.
3.  After authentication the cn (user common name taken from the certificata file generated for each account) is checked against the acl_members file where for each group a user belongs to (for example group2 group1 ) the learn_adress script will execute a file called group2.py applying that set of iptables rules for the unique ip the user is connected to the OpenVPN server with. 
The firewall policy should be set to  to drop all traffic so only explicit allow traffic declared in such a group file will be permitted for that ip during the life of a VPN session.
4.  User disconnects
User disconnection is handled by a ping time out set in server.conf. When ping time out time has passed the connection is dropped. This will cause OpenVPN to execute the learn-address hook with the action DELETE. This will cause the group.py file to be be execeuted again , but this time with a delete action removing the rules for that ip.


# Python program files overview #

* learn_address

Is called in server.conf learn address hook.
It allows openvpn to launch a custom program when openvpn learns of a new adress of a connecting user.
In our scenario the program calls learn_address doing step 3-4 described above the learn adress hook in OpenVPN sends three variables to the script: Action, IP, User where an action can be:
- ADD      - when a new connection comes in
- DELETE   - when a connection is reported as disconnected (se #4 above)
- UPDATE   - when a connection is updates *usually when there is a new ip. We do a DELETE/ADD when this happens*

The file can also be called from the shell to test a VPN connection if you run it like this:
```bash
./learn_address ACTION IP USERNAME
```


* globs.py

contains global variables and paths to files for the program learn adress and manage_acl_users
It also has a debug flag that can be flipped to increase logging


* acl_members

This file contains the mapping between users and groups
where user is the auth name for openvpn.
The group is referencing a physical file (without its .py ending)
containing users group information stored in the following format:

user1 group1 group2
user2 group2 group1
...

* acl_rules/

This folder is where ACL rules are kept and searched for when a user is to be mapped to a group.
Path to it is specified in globs.py
each file has to end with .py
has to include the python magic in the begining of file
check any file except for the template_rule.py for an example


* acl_rules/template_rule.py

this is a base template included in all acl rule files
doing some generic tasks that happen in each rule file


* /tmp/openvpn-sessions/

this is the destination folder for session files
It creates a file for each user that is currently connected to the VPN
stating the ip and username of a connection.
Since this is used when a user is disconnected to clean up rules dont remove them.
They are automatically removed as sessions disconnect. The reason we need to keep a connection
b etween IP and user ourselves is that for some silly reason openvpn does not send the ip of
a connecting user when a DELETE is sent in the learn-address hook.


* allow_all_to_10.0.0.0_rule.py

A sample firewall rule used that gives access to something network.
Each acl rule file is an independent program that can be launched directly from the shell of
the OpenVPN server to test out new firewall rules for a connected users ip.

Simply run ./prod_rule.py [add | delete] [client-ip] [username]
since this is the way each acl a user belongs to is launched from the openvpn server
when it runs the learn-address hook


* manage_acl_members

this file allows adding / removing users from the acl_members file
it does some sanity checking like, lowercase, checking if user /  group exist etc.
to use it simply run:
 ./manage_acl_members add mateusz.mojsiejuk prod_rule risk_rule

# How the VPN scripts interacts with networking and firewalling #

For traffic to pass from the OpenVPN client into our networks it first has to auth (check #1 further info).
After auth openvpn pushes some explicit routes for our network declared in server.conf

When traffic is routable from the client.
it will come to the the FORWARDING table in iptables on the OpenVPN server.
The default policy for the forwarding table in iptables should be set to drop all traffic.
So that each rule we execute with an ACCEPT statement will be the kind of traffic that is allowed to pass for that users ip.
So the magic that allows access our networks happens here.

The acl_rules/ contains rule files that will be applied if a user belongs to that acl rule a unique chain is created for the connecting IP named after the ip of the connecting user. A jump point from the FORWARDING table is created for the source ip, creating a single match rule that takes the users ip packets into the custom chain for that user.


# TODO #
- rewrite acl_members and management of file in some more easily parsable format like json or yaml
- the custom chain file contains overly explicit matching rules (in iptables forward only packets matching source ip of client jump to the custom chain, but in the custom chain we then again only allow source p ackets from that ip
- easier way of deploying new acl_rule files, currently one has to manually create them in the acl_rules/ folder
- perhaps a testsuite so we can verify there are no regressions when making changes
