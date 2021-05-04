#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test proxmox api access."""

import sys
import json
import pathlib
from configparser import ConfigParser
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning
from proxmox import ProxAuth, PyProxmox

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

POST_DATA = {'vmid':NEXT_ID, 'cores':'4', 'sockets': 1, 'description':'test kvm',
            'name':'test.example.org', 'memory':'1024',
            'scsi0': 'Stockage1:102/vm-{}-disk-0.qcow2,size=32G'.format(NEXT_ID),
            'scsihw': 'virtio-scsi-pci', 'net0': 'virtio,bridge=vmbr1',
            'ide0': 'local:iso/fbsd-122-custom.iso,media=cdrom','ostype':'l26'}

STATUS = PROXMOX_EXEC.create_virtual_machine(NODE, POST_DATA)
RESULT_STATUS = json.loads(STATUS)
print(RESULT_STATUS["data"])
print(RESULT_STATUS["status"]["code"])
