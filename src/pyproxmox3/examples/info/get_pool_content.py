#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Get pool content."""

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
CONTENT_POOL = PROXMOX_EXEC.get_pool_content("poolname")
RESULT_POOL = json.loads(CONTENT_POOL)
for member in RESULT_POOL['data']['members']:
    print(member['id'])
    print(member['name'])
