![deploy](https://github.com/snakems/snakems.ansible/actions/workflows/main.yml/badge.svg)
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
[snakems.ansible.keepass](https://github.com/snakems/snakems.ansible/blob/main/docs/snakems.ansible.keepass_inventory.md)|KeePass inventory source

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