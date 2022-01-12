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
        keepass_title_mask:
            description: "If entry not found by hostname, try search by mask. Macroses: {{ hostname }}"
            default: "{{ hostname }}"
            ini:
                - key: title_mask
                  section: keepass
            env:
                - name: ANSIBLE_TITLE_MASK
'''

try:
    from __main__ import display
except ImportError:
    from ansible.utils.display import Display
    display = Display()
from ansible.plugins.vars import BaseVarsPlugin
from ansible.inventory.host import Host
from pykeepass import PyKeePass
from urllib.parse import urlparse
import re
from jinja2 import Environment
from ..module_utils.keepass_helper import get_entry_path, init_kp_db


class VarsModule(BaseVarsPlugin):

    REQUIRES_WHITELIST = False

    def _extract_vars_from_entry(self, entry):
        entry_vars = {'keepass_entry_path': get_entry_path(entry)}
        entry_vars['ansible_user'] = entry.username
        entry_vars['ansible_password'] = entry.password
        host_url = entry.url
        if not re.match('^.*?://', entry.url, flags=re.IGNORECASE):
            host_url = f"ssh://{host_url}"
        host_data = urlparse(host_url)
        entry_vars['ansible_connection'] = host_data.scheme
        entry_vars['ansible_host'] = host_data.hostname
        if host_data.port is not None:
            entry_vars['ansible_port'] = host_data.port
        # Check additional vars for host
        if len(entry.custom_properties) > 0:
            for host_var in entry.custom_properties:
                entry_vars[host_var] = entry.custom_properties[host_var]
        return entry_vars

    def _get_url(self, entity_vars):
        _url = None
        if entity_vars.get("ansible_host") is not None:
            _url = entity_vars.get("ansible_host")
            if entity_vars.get("ansible_connection") is not None:
                _url = "{}://{}".format(entity_vars.get("ansible_connection"), _url)
            if entity_vars.get("ansible_port") is not None:
                _url = "{}:{}".format(_url, entity_vars.get("ansible_port"))
        return _url

    def get_vars(self, loader, path, entities, cache=True):
        ''' parses the inventory file '''
        if not isinstance(entities, list):
            entities = [entities]
        super(VarsModule, self).get_vars(loader, path, entities)
        # Init KeePass database
        kp: PyKeePass = init_kp_db(self, loader)
        # Find credentials
        for entity in [e for e in entities if isinstance(e, Host)]:
            # Try fund by title
            _title_by_mask = Environment(autoescape=True).from_string(self.get_option("keepass_title_mask")).render(hostname=entity.name)
            _titles = [entity.vars.get("keepass_title")] if entity.vars.get("keepass_title") is not None else []
            _titles.append(entity.name)
            _titles.extend([_title_by_mask] if _title_by_mask not in _titles else [])
            for _title in _titles:
                entry = kp.find_entries_by_title(_title, first=True)
                if entry is not None:
                    return self._extract_vars_from_entry(entry)
            # Try find by connection data
            _url = self._get_url(entity.vars)
            entry = kp.find_entries_by_url(_url, regex=True, first=True)
            if entry is not None:
                return self._extract_vars_from_entry(entry)
        return {}
