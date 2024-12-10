# FabAccess users.toml LDAP Import

# Zweck

Dieses Script verbindet sich bei Ausführung mit den angegebenen Credentials zu einem LDAP(S)-Server und sucht nach passenden Nutzern, um eine FabAccess-kompatible `users.toml` Datei zu erzeugen.

Das Script dient außerdem auch als Beispielvorlage für andere Entwickler, die ggf. andere Anwendungen bzw. Benutzerquellen an FabAccess anbinden wollen und nach geeigneten Code-Quellen suchen.

**Wichtig**: Dieses Script ersetzt **keine** native LDAP-Integration in FabAccess!

# Installation
```bash
sudo apt install build-essential python3-dev libldap2-dev libsasl2-dev ldap-utils
```

```bash
cd /opt/fabinfra/scripts/
git clone https://github.com/vmario89/fabaccess-users-toml-ldap.git

cd /opt/fabinfra/scripts/fabaccess-users-toml-ldap/
chmod +x /opt/fabinfra/scripts/fabaccess-users-toml-ldap/main.py
chown -R bffh:bffh /opt/fabinfra/scripts/fabaccess-users-toml-ldap/
```

# Benutzung

## Hilfe / Parameter anzeigen

```shell
cd /opt/fabinfra/scripts/fabaccess-users-toml-ldap/
python3 main.py --help
```

```shell
usage: main.py [-h] [-s SERVER] [-u USER] [-p PASSWORD] [-b BASEDN] [--filter_user FILTER_USER] [--regex_groups REGEX_GROUPS] [--attrib_user ATTRIB_USER] [--attrib_groups ATTRIB_GROUPS]
               [--attrib_password ATTRIB_PASSWORD] [--output OUTPUT]

options:
  -h, --help            show this help message and exit
  -s SERVER, --server SERVER
                        LDAP Server (Syntax: <protocol>://host:port, e.g. ldap://192.168.1.1:389 or ldaps://192.168.1.1.:636)
  -u USER, --user USER  User, e.g. 'uid=root,cn=users,dc=yourserver,dc=com'
  -p PASSWORD, --password PASSWORD
                        Password
  -b BASEDN, --basedn BASEDN
                        BaseDN, for example 'cn=users,dc=yourserver,dc=com'
  --filter_user FILTER_USER
                        LDAP user filter, e.g. '(&(uid=*)(objectClass=posixAccount))'
  --regex_groups REGEX_GROUPS
                        LDAP group regex, e.g. 'cn=(.*),cn=groups,dc=yourserver,dc=com'. If your group result is 'cn=administrator,cn=groups,dc=yourserver,dc=com', then the word
                        'administrator' gets properly exctracted. You can use https://regex101.com for testing.
  --attrib_user ATTRIB_USER
                        Attribute name for FabAccess user name, e.g. 'uid'
  --attrib_groups ATTRIB_GROUPS
                        Attribute name for FabAccess user roles, e.g. 'memberOf'
  --attrib_password ATTRIB_PASSWORD
                        Attribute name for FabAccess user password hash, e.g. 'sambaNTPassword'. For OpenLDAP there is Argon2 hash support!
  --output OUTPUT       Target directory + file where to write the toml file. Please provide the full name. If not given, users.toml will be written

```

## `users.toml` Datei schreiben

```shell
cd /opt/fabinfra/scripts/fabaccess-users-toml-ldap/
python3 main.py --server ldap://192.168.188.1:389 --user="uid=admin,cn=users,dc=yourserver,dc=com" --password pw --basedn "cn=users,dc=yourserver,dc=com" --filter_user "uid=*" --regex_groups "cn=(.*),cn=groups,dc=yourserver,dc=com" --attrib_user uid --attrib_groups memberOf --attrib_password sambaNTPassword --output /opt/fabinfra/bffh-data/config/users.toml
```

Nach dem Erstellen der Datei sollte diese überprüft und im Anschluss per `bffhd --load users.toml` geladen werden, um die Änderungen entsprechend zu reflektieren.

## Weiterführende Dokumentation

Für das Erstellen von `regex_groups` kann [https://regex101.com](https://regex101.com) genutzt werden. Eine Anleitung für einen beispielhaften Synology LDAP Server findet sich in der FabAccess Dokumentation https://docs.fab-access.org/books/plugins-und-schnittstellen/page/ldap-anbindung. 

# Bekannte Probleme

Dieses Script stellt keine saubere Lösung für die Nutzung von LDAP mit FabAccess bffh dar (zumindest nicht mit Version 0.4.2):

* etwaige Passwortänderungen am zentralen LDAP-Server müssen erneut in die `users.toml` Datei übertragen werden

* ändert der Nutzer oder der Administrator für den Nutzer das Passwort über die Client App, dann würde der Nutzer beim nächstens `users.toml` Import wieder überschrieben. Diese Änderungen werden also auch nicht an den LDAP-Server gesendet

* die Password Hashes aus dem LDAP Server können in der Regel nicht mit FabAccess verwendet werden, da sie kein Argon2-Format aufweisen. Einzig OpenLDAP unterstützt Argon2 überhaupt. Aus adminstrativen Gründen macht eine Umstellung aller Nutzerpassworthashes auf Argon2 jedoch keinen Sinn. Eine native Integration von LDAP direkt in FabAccess ist also unumgänglich.

# Hinweise

Das Script basiert auf der Idee von https://gitlab.bht-berlin.de/innovisionlab/ldapbodge

## Python Module

Das Script wurde getestet mit:

```bash
python -V
3.12.3

pip list installed
pip 24.0
pyasn1 0.6.1
pyasn1_modules 0.4.1
python-ldap 3.4.4
toml 0.10.2
```
