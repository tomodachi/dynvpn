### dynvpn ###

dynvpn is a set of small python programs for dynamicaly applying firewall profiles to users 
based on group memberships. This proves quite usefull to get a more "enterprisey VPN"
For example maybe we want  "Alice" to only be able to access your bugtracker on port 80, while you want "Bob" to also be able to 
ssh into it to verify backups etc. 

# Requirements:
- iptables
- openvpn
- python2.7


# Openvpn client connection state transition

1.  User connects to VPN 
2.  User is authenticated
3.  After authentication the cn (common name taken from the certificate file generated for vpn client certificate holder) is checked against the acl_members file where for each group a user belongs to (for example group2 group1 ) the learn_adress script will execute a file called group2.py applying that set of iptables rules for the unique ip the user is connected to the OpenVPN server with. 
4.  User disconnects
User disconnection is handled by a ping time out set in server.conf. When time out is reached the connection is dropped causing OpenVPN to call the learn-address hook with the action DELETE. 
Dropping the vpn connection and removing any firewall rules for that VPN session. 


# Python program files overview #

* learn_address

Is the hook script called when a a vpn session is established  
It allows openvpn to launch a custom program when openvpn learns of a new adress of a connecting user.
In our scenario the program calls learn_address doing step 3-4 described above the learn adress hook in OpenVPN sends three variables to the script: Action, IP, User where an action can be:
- add      - when a new connection is established
- delete   - when a connection is reported as disconnected (se #4 above)
- update   - when a connection is updates *usually when there is a new ip. We do a DELETE/ADD when this happens*

learn_Address be called from the shell to testing the firewall actions: 
```bash
./learn_address ACTION IP USERNAME
```


* globs.py

contains global variables and paths to files for the program learn adress and manage_acl_users
It also has a debug flag that can be flipped to increase logging


* acl_members

This file contains the mapping between users and groups
where user is the auth name for openvpn.
Each group is referencing a python file containing firewall rules 
users group information stored in the following format: 

john_doe allow_ssh allow_dns 
jane_doe allow_ntp 
...

* acl_rules/

This folder is where ACL rules are kept and searched for when a user is to be mapped to a group.
Path to it is specified in globs.py
has to include the python magic in the begining of file
check any file except for the template_rule.py for an example


* acl_rules/template_rule.py

this is a base template that should be included in your custom acl files
doing some generic tasks that happen in each rule file 


* /tmp/openvpn-sessions/

this is the destination folder for session files
It creates a file for each currently connected user 
stating the ip and username and applied rules for a user 


* allow_all_to_10.0.0.0_rule.py

A sample firewall rule used that gives access to something network.
Each acl rule file is an independent program that can be launched directly from the shell of
the OpenVPN server to test out new firewall rules for a connected users ip.


* manage_acl_members

this file allows adding / removing users from the acl_members file
it does some sanity checking like, lowercase, checking if user /  group exist etc.
to use it simply run:
 ./manage_acl_members add mateusz.mojsiejuk prod_rule risk_rule

# How the VPN scripts interacts with networking and firewalling #

For traffic to pass from the OpenVPN client into our networks it first has to auth (check #1 further info).
After auth openvpn pushes some explicit routes for our network declared in server.conf

Traffic from a connected vpn client 
will reach FORWARDING table on the vpn server.
The default policy for the forwarding table should be set to drop all traffic. 
Meaning that only traffic matching the explicit ALLOW rules in the rules mapped to a user will be allowed to pass 

The acl_rules/ contains rule files that are applied to mapped users.  For each connecting user a jump reference is created in the forwarding table for the users connecting IP 
in this table each acl rule files rules will be applied 


# TODO #
- rewrite acl_members and management of file in some more easily parsable format like json or yaml
- easier way of deploying new acl_rule files, currently one has to manually create them in the acl_rules/ folder
- perhaps a test suite so we can verify there are no regressions when making changes
