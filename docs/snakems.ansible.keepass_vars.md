# snakems.ansible.keepass_vars
### KeePass vars plugin
- [Synopsis](#synopsis)
- [Requirements](#requirements)
- [Parameters](#parameters)
- [Using](#using)

## Synopsis
Get vars from KeePass database by hostname (Entry title) or connection data.

## Requirements  
The below requirements are needed on the local Ansible controller node that executes this plugin.
- pykeepass

## Parameters
Parammeter | Required | Configuration | Description
--|--|--|--
keepass_database|Yes|ini entries:<br />[keepass]<br />database = VALUE<br /><br />env: ANSIBLE_KEEPASS_DATABASE|Path to KeePass database 
keepass_key|No|ini entries:<br />[keepass]<br />key = VALUE<br /><br />env: ANSIBLE_KEEPASS_KEY|Path to key-file.
keepass_pass|No|ini entries:<br />[keepass]<br />password = VALUE<br /><br />env: ANSIBLE_KEEPASS_PASSWORD<br />env: ANSIBLE_KEEPASS_PASS|Pasword for KeePass database. If not set, it will be prompted 
keepass_root|Yes|ini entries:<br />[keepass]<br />root = VALUE<br /><br />env: ANSIBLE_KEEPASS_ROOT|Directory in KeePass Database from which to take hosts
keepass_title_mask|No|ini entries:<br />[keepass]<br />title_mask = VALUE<br /><br />env: ANSIBLE_TITLE_MASK|Mask for searching entry. Macroses: {{ hostname }}.
keepass_title|No|Vars: keepass_title|Entry name in Keepass

## Using
### Config ansible.cfg
```
[defaults]
vars_plugins_enabled  = host_group_vars, snakems.ansible.keepass_vars

[keepass]
database = test.kdbx
key = test.key
root = ansible
password = "$ANSIBLE_VAULT;1.1;AES256\n35303030656130...6662"
title_mask = ssh_{{ hostname }}
```

### Examples
```
# hosts.ini
[test]
; return prod-1 entry, if not found try search ssh_prod-1
prod-1

; return prod-2-new entry
prod-2 keepass_title=prod-2-new
```