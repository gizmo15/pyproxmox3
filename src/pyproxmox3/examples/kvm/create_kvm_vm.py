#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test proxmox api access."""

import sys
import json
import pathlib
from configparser import ConfigParser
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning
from pyproxmox3 import ProxAuth, PyProxmox

# Read conf.ini
INI_CONF = "./proxmox_api.ini"

if not pathlib.Path(INI_CONF).exists():
    print("Config file not found!")
    print("Need the config file in {}".format(INI_CONF))
    sys.exit(1)

CONFIG = ConfigParser()
CONFIG.read(INI_CONF)

# DB parameters
URL = CONFIG.get('api', 'ipaddress')
USERAPI = CONFIG.get('api', 'user')
PASSWORD = CONFIG.get('api', 'passwd')
NODE = CONFIG.get('api', 'node')

disable_warnings(InsecureRequestWarning)

INIT_AUTHENT = ProxAuth(URL, USERAPI, PASSWORD)

PROXMOX_EXEC = PyProxmox(INIT_AUTHENT)

NEXT_ID = PROXMOX_EXEC.get_cluster_vm_next_id()
NEXT_ID = json.loads(NEXT_ID)
NEXT_ID = NEXT_ID["data"]

STORAGE = 'Stockage1'
FILENAME = "vm-{}-disk-0.qcow2".format(NEXT_ID)
SIZE = '32G'

POST_DATA = {'vmid':NEXT_ID, 'cores':'2', 'sockets': 1, 'description':'test kvm',
            'name':'test.example.org', 'memory':'2048',
            'virtio0': '{}:{}/{},size={}'.format(STORAGE, NEXT_ID, FILENAME, SIZE),
            'scsihw': 'virtio-scsi-pci', 'net0': 'virtio,bridge=vmbr1',
            'ide0': 'local:iso/fbsd-13.0-zfs-custom.iso,media=cdrom','ostype':'l26'}

STATUS_CREATE = PROXMOX_EXEC.create_virtual_machine(NODE, POST_DATA)
RESULT_STATUS_CREATE = json.loads(STATUS_CREATE)
print(RESULT_STATUS_CREATE["data"])
print(RESULT_STATUS_CREATE["status"]["code"])

POST_DATA = {'filename': FILENAME, 'node': NODE, 'size': SIZE, 'storage': STORAGE, 'vmid': NEXT_ID} 

STATUS_ALLOCATE = PROXMOX_EXEC.allocate_node_storage_vm(NODE, STORAGE, POST_DATA)
print(STATUS_ALLOCATE)
RESULT_STATUS_ALLOCATE = json.loads(STATUS_ALLOCATE)
print(RESULT_STATUS_ALLOCATE["data"])
print(RESULT_STATUS_ALLOCATE["status"]["code"])
