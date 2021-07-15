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
INI_CONF = "../proxmox_api.ini"

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

disable_warnings(InsecureRequestWarning)

INIT_AUTHENT = ProxAuth(URL, USERAPI, PASSWORD)

PROXMOX_EXEC = PyProxmox(INIT_AUTHENT)

STATUS = PROXMOX_EXEC.get_cluster_status()
RESULT_STATUS = json.dumps(STATUS["data"], indent=4, sort_keys=True)
print("Check connexion : ")
print(RESULT_STATUS)
