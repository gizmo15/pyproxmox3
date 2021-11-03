#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Get pools list."""

import sys
import json
import pathlib
from configparser import ConfigParser
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning
from pyproxmox3 import ProxAuth, PyProxmox

disable_warnings(InsecureRequestWarning)
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

INIT_AUTHENT = ProxAuth(URL, USERAPI, PASSWORD)

PROXMOX_EXEC = PyProxmox(INIT_AUTHENT)
LIST_POOLS = PROXMOX_EXEC.list_pools()
RESULT_LIST = json.loads(LIST_POOLS)

for entry in RESULT_LIST['data']:
    print(entry['poolid'])
