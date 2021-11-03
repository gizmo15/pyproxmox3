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

VM_ID = "713"
POST_DATA = {'hotplug': "network,disk,usb,memory,cpu"} 

STATUS_SET_OPTIONS = PROXMOX_EXEC.set_virtual_machine_options(NODE, VM_ID, POST_DATA)
print(STATUS_SET_OPTIONS)
RESULT_STATUS_SET_OPTIONS = json.loads(STATUS_SET_OPTIONS)
print(RESULT_STATUS_SET_OPTIONS["data"])
print(RESULT_STATUS_SET_OPTIONS["status"]["code"])
