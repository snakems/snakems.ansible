[![License](https://img.shields.io/github/license/snakems/snakems.ansible.svg?style=flat)](https://github.com/snakems/snakems.ansible/blob/master/LICENSE) ![deploy](https://github.com/snakems/snakems.ansible/actions/workflows/main.yml/badge.svg) [![galaxy](https://img.shields.io/badge/galaxy-snakems.ansible-660198.svg?style=flat)](https://galaxy.ansible.com/snakems/ansible) ![Version on Galaxy](https://img.shields.io/badge/dynamic/json?style=flat&label=galaxy-version&prefix=v&url=https://galaxy.ansible.com/api/v2/collections/snakems/ansible/&query=latest_version.version)   
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=snakems_snakems.ansible&metric=bugs)](https://sonarcloud.io/summary/new_code?id=snakems_snakems.ansible) [![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=snakems_snakems.ansible&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=snakems_snakems.ansible) [![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=snakems_snakems.ansible&metric=vulnerabilities)](https://sonarcloud.io/summary/new_code?id=snakems_snakems.ansible) [![Duplicated Lines (%)](https://sonarcloud.io/api/project_badges/measure?project=snakems_snakems.ansible&metric=duplicated_lines_density)](https://sonarcloud.io/summary/new_code?id=snakems_snakems.ansible)
# Ansible Collection - snakems.ansible

My collection ansible plugins and modules.

<!--start requires_ansible-->
## Ansible version compatibility

This collection has been tested against following Ansible versions: **>=2.9.10**.

Plugins and modules within a collection may be tested with only specific Ansible versions.
A collection may contain metadata that identifies these versions.
PEP440 is the schema used to describe the versions of Ansible.
<!--end requires_ansible-->

## Python version compatibility

This collection requires Python 3.6 or greater.

## Included content

<!--start collection content-->
### Inventory plugins
Name | Description
--- | ---
[snakems.ansible.keepass_inventory](https://github.com/snakems/snakems.ansible/blob/master/docs/snakems.ansible.keepass_inventory.md)|KeePass inventory source        

### Vars plugins
Name | Description
--- | ---
[snakems.ansible.keepass_vars](https://github.com/snakems/snakems.ansible/blob/master/docs/snakems.ansible.keepass_vars.md)|KeePass variables data      

## Installing this collection

You can install the collection with the Ansible Galaxy CLI:

    ansible-galaxy collection install snakems.ansible

You can also include it in a `requirements.yml` file and install it with `ansible-galaxy collection install -r requirements.yml`, using the format:

```yaml
---
collections:
  - name: snakems.ansible
```

The python module dependencies are not installed by `ansible-galaxy`.  They can
be manually installed using pip:

    pip install requirements.txt

or:

    pip install pykeepass