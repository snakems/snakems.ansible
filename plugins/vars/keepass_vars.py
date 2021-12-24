#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Mironenko Sergey <sergey@mironenko.pp.ua>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    name: keepass_vars
    plugin_type: vars
    short_description: KeePass vars plugin
    requirements:
        - pykeepass
        - whitelist in configuration
    description:
        - Get vars by hostname or host, port from KeePass database.
    author:
        - Mironenko Sergey (@snakems)
    options:
        keepass_database:
            description: Path to KeePass database
            required: True
            ini:
                - key: database
                  section: keepass
            env:
                - name: ANSIBLE_KEEPASS_DATABASE
        keepass_key:
            description: Path to key-file. Set if needed
            ini:
                - key: key
                  section: keepass
            env:
                - name: ANSIBLE_KEEPASS_KEY
        keepass_pass:
            description: Pasword for KeePass database. Plain or encrypted by ansible-vault
            required: True
            ini:
                - key: password
                  section: keepass
            env:
                - name: ANSIBLE_KEEPASS_PASSWORD
                - name: ANSIBLE_KEEPASS_PASS
        keepass_filter_title:
            description: If entry not found by hostname, try search by mask. Macroses: {{ hostname }}
            default: "{{ hostname }}"
            ini:
                - key: filter_title
                  section: keepass
            env:
                - name: ANSIBLE_FILTER_TITLE
'''
# TODO Add options keepass_filter_title and keepass_filter_url
try:
    from __main__ import display
except ImportError:
    from ansible.utils.display import Display
    display = Display()
from ansible.errors import AnsibleError
from ansible.plugins.vars import BaseVarsPlugin
from ansible.inventory.host import Host
from getpass import getpass
from pykeepass import PyKeePass
from pykeepass.exceptions import CredentialsError, HeaderChecksumError, PayloadChecksumError
from urllib.parse import urlparse
import re


class VarsModule(BaseVarsPlugin):

    REQUIRES_WHITELIST = True

    def _extract_vars_from_entry(self, entry):
        vars = {}
        vars['ansible_user'] = entry.username
        vars['ansible_password'] = entry.password
        host_url = entry.url
        if not re.match('^.*?://', entry.url, flags=re.IGNORECASE):
            host_url = f"ssh://{host_url}"
        host_data = urlparse(host_url)
        vars['ansible_connection'] = host_data.scheme
        vars['ansible_host'] = host_data.hostname
        if host_data.port is not None:
            vars['ansible_port'] = host_data.port
        # Check additional vars for host
        if len(entry.custom_properties) > 0:
            for host_var in entry.custom_properties:
                vars[host_var] = entry.custom_properties[host_var]
        return vars

    def get_vars(self, loader, path, entities, cache=True):
        ''' parses the inventory file '''
        if not isinstance(entities, list):
            entities = [entities]
        super(VarsModule, self).get_vars(loader, path, entities)
        # Init KeePass database
        kp = None
        keepass_pass = ""
        if self.get_option("keepass_pass") is not None:
            keepass_pass = self.get_option("keepass_pass")
        while True:
            if keepass_pass == "":
                keepass_pass = getpass(prompt="Enter password for database {}: ".format(self.get_option("keepass_database")))
            if keepass_pass != "":
                try:
                    if loader._vault.is_encrypted(self.get_option("keepass_pass")):
                        if len(loader._vault.secrets) > 0:
                            keepass_pass = loader._vault.decrypt(self.get_option("keepass_pass").replace('\\n', '\n')).decode()
                        else:
                            raise AnsibleError("'keepass_pass' encrypted by vault, but vault-password not provided. Please use option --ask-vault-password")
                    if self.get_option("keepass_key") is not None:
                        kp = PyKeePass(self.get_option("keepass_database"), password=keepass_pass, keyfile=self.get_option("keepass_key"))
                    else:
                        kp = PyKeePass(self.get_option("keepass_database"), password=keepass_pass)
                    break
                except IOError:
                    display.error('Could not open the database or keyfile.')
                except FileNotFoundError:
                    display.error('Could not open the database or keyfile.')
                except CredentialsError:
                    display.error("KeePass credentials not correct")
                except (HeaderChecksumError, PayloadChecksumError):
                    display.error('Could not open the database, as the checksum of the database is wrong. This could be caused by a corrupt database.')
                finally:
                    keepass_pass = ""
        # Find credentials
        for entity in entities:
            if isinstance(entity, Host):
                # Try find entry by title
                entry = kp.find_entries_by_title(entity.name, first=True)
                if entry is not None:
                    _vars = self._extract_vars_from_entry(entry)
                    return _vars
        return {}
