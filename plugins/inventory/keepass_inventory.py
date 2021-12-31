#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Mironenko Sergey <sergey@mironenko.pp.ua>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = '''
    name: keepass_inventory
    plugin_type: inventory
    short_description: KeePass inventory source
    requirements:
        - pykeepass
    description:
        - Get inventory hosts from KeePass database.
        - Uses a YAML configuration file that ends with C(keepass.(yml|yaml), keepass_hosts.(yml|yaml)).
    author:
        - Mironenko Sergey (@snakems)
    options:
        plugin:
            description: Token that ensures this is a source file for the plugin.
            required: True
            choices: ['keepass_inventory', 'snakems.ansible.keepass_inventory']
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
            description: Pasword for KeePass database. If not set, it will be prompted
            ini:
                - key: password
                  section: keepass
            env:
                - name: ANSIBLE_KEEPASS_PASSWORD
                - name: ANSIBLE_KEEPASS_PASS
        keepass_root:
            description: Directory from which to take hosts
            required: True
            ini:
                - key: root
                  section: keepass
            env:
                - name: ANSIBLE_KEEPASS_ROOT
'''

EXAMPLES = '''
# Minimal example using environment vars or instance role credentials
# Fetch all hosts in root ansible. Password will be prompted
plugin: keepass_inventory
keepass_database: "test.kdbx"
keepass_root: "ansible"

# Example using key and predefined password. Set password in config not recommended
plugin: keepass_inventory
keepass_database: "test.kdbx"
keepass_pass: "123456"
keepass_key: "test.key"
keepass_root: "ansible"

# Example using encrypted password by ansible-vault
plugin: keepass_inventory
keepass_database: "test.kdbx"
keepass_pass: !vault |
          $ANSIBLE_VAULT;1.1;AES256
          35303030656130353330316138333833306364323664303534306532353230623737353937623563
          6137346636393733633335666261383535613033643835390a623262616632363461653765646534
          66343630333539326331306261393538316537356638376232663138366665336466316564386132
          6666313536323031370a626531626630316533356262646363333466383931316135396362353430
          6662
keepass_key: "test.key"
keepass_root: "ansible"
'''

try:
    from __main__ import display
except ImportError:
    from ansible.utils.display import Display
    display = Display()
import re
from urllib.parse import urlparse
from ansible.plugins.inventory import (BaseInventoryPlugin, Cacheable,
                                       Constructable)
from pykeepass import PyKeePass
from ..module_utils.keepass_helper import get_entry_path, init_kp_db_for_inventory


class InventoryModule(BaseInventoryPlugin, Constructable, Cacheable):

    NAME = 'keepass_inventory'

    def _add_host(self, entry, group_name):
        """ Add host with vars to the group """
        hostname = entry.title
        # Check if hostname 'group_vars' then add custom properties to vars for selected group
        if hostname == "group_vars" and len(entry.custom_properties) > 0:
            for group_var in entry.custom_properties:
                self.inventory.set_variable(group_name, group_var, entry.custom_properties[group_var])
            return
        # Add host to group
        self.inventory.add_host(hostname, group=group_name)
        # Determine and add vars to host
        self.inventory.set_variable(hostname, "keepass_entry_path", get_entry_path(entry))
        self.inventory.set_variable(hostname, "ansible_user", entry.username)
        self.inventory.set_variable(hostname, "ansible_password", entry.password)
        # Determine connection type, host,, port
        host_url = entry.url
        if not re.match('^.*?://', entry.url, flags=re.IGNORECASE):
            host_url = f"ssh://{host_url}"
        host_data = urlparse(host_url)
        self.inventory.set_variable(hostname, "ansible_connection", host_data.scheme)
        self.inventory.set_variable(hostname, "ansible_host", host_data.hostname)
        if host_data.port is not None:
            self.inventory.set_variable(hostname, "ansible_port", host_data.port)
        # Check additional vars for host
        if len(entry.custom_properties) > 0:
            for host_var in entry.custom_properties:
                self.inventory.set_variable(hostname, host_var, entry.custom_properties[host_var])

    def _add_group(self, group, parent=None):
        """ Add group with children hosts to inventrory."""
        group_name = group.name
        self.inventory.add_group(group_name)
        if parent is not None:
            self.inventory.add_child(parent, group_name)
        for sub_group in group.subgroups:
            self._add_group(sub_group, group_name)
        for entry in group.entries:
            self._add_host(entry, group_name)

    def verify_file(self, path):
        ''' return true/false if this is possibly a valid file for this plugin to consume '''
        valid = False
        if super(InventoryModule, self).verify_file(path) and path.endswith(('keepass.yaml', 'keepass.yml', 'keepass_hosts.yaml', 'keepass_hosts.yml')):
            valid = True
        return valid

    def parse(self, inventory, loader, path, cache=False):
        super(InventoryModule, self).parse(inventory, loader, path, cache)
        self._read_config_data(path)
        kp: PyKeePass = init_kp_db_for_inventory(self)
        main_root = kp.find_groups(name=self.get_option("keepass_root"), first=True)
        for group in main_root.subgroups:
            self._add_group(group)
        for entry in main_root.entries:
            self._add_host(entry, "all")
