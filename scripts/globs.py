class Global_vars:
    """ Global variable holder """
    ACL_MEMBER_FILE = "/etc/openvpn/scripts/acl_members"
    ACL_RULES_PATH = "/etc/openvpn/scripts/acl_rules/"
    USER_SESSION_PATH = "/etc/openvpn/scripts/sessions/"
    DEBUG = False
    USER_ACL = ""

class Openvpn_incoming_var:
    """struct like placeholder for
    all openvpn variables we get when script is called
    in openvpn learn-address hook """
    action = ""
    ip = ""
    user = ""
