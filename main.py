import ldap
import toml
import sys
import secrets
import string
import argparse
import re
import pathlib

def init_ldap(server, user, pw):
    con = ldap.initialize(server)
    con.protocol_version=ldap.VERSION3
    con.simple_bind_s(user, pw)
    return con

if __name__ == '__main__':

    pars = argparse.ArgumentParser()
    pars.add_argument("-s", "--server", type=str, dest="server", help="LDAP Server (Syntax: <protocol>://host:port, e.g. ldap://192.168.1.1:389 or ldaps://192.168.1.1.:646)")
    pars.add_argument("-u", "--user", type=str, dest="user", help="User, e.g. 'uid=root,cn=users,dc=yourserver,dc=com'")
    pars.add_argument("-p", "--password", type=str, dest="password", help="Password")
    pars.add_argument("-b", "--basedn", type=str, dest="basedn", help="BaseDN, for example 'cn=users,dc=yourserver,dc=com'")
    pars.add_argument("--filter_user", type=str, dest="filter_user", help="LDAP user filter, e.g. '(&(uid=*)(objectClass=posixAccount))'")
    pars.add_argument("--regex_groups", type=str, dest="regex_groups", help="LDAP group regex, e.g. 'cn=(.*),cn=groups,dc=yourserver,dc=com'. If your group result is 'cn=administrator,cn=groups,dc=yourserver,dc=com', then the word 'administrator' gets properly exctracted. You can use https://regex101.com for testing.")
    pars.add_argument("--attrib_user", type=str, dest="attrib_user", help="Attribute name for FabAccess user name, e.g. 'uid'")
    pars.add_argument("--attrib_groups", type=str, dest="attrib_groups", help="Attribute name for FabAccess user roles, e.g. 'memberOf'")
    pars.add_argument("--attrib_password", type=str, dest="attrib_password", help="Attribute name for FabAccess user password hash, e.g. 'sambaNTPassword'. For OpenLDAP there is Argon2 hash support!")
    pars.add_argument("--output", type=pathlib.Path, dest="output", help="Target directory + file where to write the toml file. Please provide the full name. If not given, users.toml will be written")

    options = pars.parse_args()

    if not any(vars(options).values()):
        pars.print_help()
        exit(1)

    if options.filter_user is None or options.filter_user == "":
        print("Please provide --filter_user argument")
        exit(1)

    if options.regex_groups is None or options.regex_groups == "":
        print("Please provide --regex_groups argument")
        exit(1)

    if options.attrib_user is None or options.attrib_user == "":
        print("Please provide --attrib_user argument")
        exit(1)

    if options.attrib_groups is None or options.attrib_groups == "":
        print("Please provide --attrib_groups argument")
        exit(1)

    if options.attrib_password is None or options.attrib_password == "":
        print("Please provide --attrib_password argument")
        exit(1)

    try:
        con = init_ldap(options.server, options.user, options.password)
    except Exception as e:
        print("Could not connect to LDAP server: {}".format(str(e)))
        sys.exit(1)

    ldap_attributes = [options.attrib_user, options.attrib_groups, options.attrib_password] # List of attributes that you want to fetch.
    #ldap_attributes = ["*"] # Wildcard filter - show all!

    query_user = options.filter_user
    ldap_users = con.search_s(options.basedn, ldap.SCOPE_SUBTREE, options.filter_user, ldap_attributes)

    users = []
    for data_dict in [entry for dn, entry in ldap_users if isinstance(entry, dict)]:
        users.append(data_dict[options.attrib_user][0].decode("utf-8"))

    pw = []
    for user in users:

        for data_dict in [entry for dn, entry in ldap_users if isinstance(entry, dict)]:
            if data_dict[options.attrib_user][0].decode("utf-8") == user:
                groups = []
                for group in data_dict[options.attrib_groups]:
                    group_dec = group.decode("utf-8")
                    pattern = r"{}".format(options.regex_groups)
                    groups += re.findall(pattern, group_dec)
                if len(groups) == 0:
                    groups.append("default_role")

                password = data_dict[options.attrib_password][0].decode("utf-8")

        userdict = dict()
        userdict["passwd"] = password
        userdict["roles"] = groups

        pw.append(userdict)

    if options.output is not None:
        target = options.output
    else:
        target = pathlib.Path("users.toml")
    with open(target, "w") as f:
        # the trailing comma in users.toml comes from command "toml.dump()". These are fine!
        toml.dump(dict(zip(users, pw)), f)

    print("{} users dumped to {}".format(len(users), target.absolute()))
