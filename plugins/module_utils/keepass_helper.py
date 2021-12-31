#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Mironenko Sergey <sergey@mironenko.pp.ua>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
from getpass import getpass
try:
    from __main__ import display
except ImportError:
    from ansible.utils.display import Display
    display = Display()
from ansible.errors import AnsibleError
from pykeepass import PyKeePass
from pykeepass.exceptions import CredentialsError, HeaderChecksumError, PayloadChecksumError


def get_entry_path(entry):
    return '/'.join('' if p is None else p for p in entry.path)


def promt_keepass_password(db):
    return getpass(prompt="Enter password for database {}: ".format(db))


def init_kp_db(obj, loader):
    kp = None
    keepass_database = obj.get_option("keepass_database")
    keepass_pass = obj.get_option("keepass_pass") if (obj.get_option("keepass_pass") is not None) else promt_keepass_password(keepass_database)
    if loader._vault.is_encrypted(keepass_pass):
        if len(loader._vault.secrets) > 0:
            keepass_pass = loader._vault.decrypt(keepass_pass.replace('\\n', '\n')).decode()
        else:
            raise AnsibleError("'keepass_pass' encrypted by vault, but vault-password not provided. Please use option --ask-vault-password")
    while True:
        try:
            kp = PyKeePass(obj.get_option("keepass_database"), password=keepass_pass, keyfile=obj.get_option("keepass_key"))
            break
        except IOError:
            display.error('Could not open the database or keyfile.')
        except FileNotFoundError:
            display.error('Could not open the database or keyfile.')
        except CredentialsError:
            display.error("KeePass credentials not correct")
        except (HeaderChecksumError, PayloadChecksumError):
            display.error('Could not open the database, as the checksum of the database is wrong. This could be caused by a corrupt database.')
        keepass_pass = promt_keepass_password(obj.get_option("keepass_database"))
    return kp


def init_kp_db_for_inventory(obj):
    return init_kp_db(obj, obj.loader)
