#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A python wrapper for the Proxmox 2.x API.

Example usage:

1) Create an instance of the prox_auth class by passing in the
url or ip of a server, username and password:

a = prox_auth('vnode01.example.org','apiuser@pve','examplePassword')

2) Create and instance of the pyproxmox class using the auth object as a parameter:

b = pyproxmox(a)

3) Run the pre defined methods of the pyproxmox class.
NOTE: they all return data, usually in JSON format:

status = b.get_clusterStatus('vnode01')

For more information see https://github.com/Daemonthread/pyproxmox.
"""

import sys
import json
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning
import requests


# Authentication class
class ProxAuth:
    """
    The authentication class, requires three strings:

    1. An IP/resolvable url (minus the https://)
    2. Valid username, including the @pve or @pam
    3. A password

    Creates the required ticket and CSRF prevention token for future connections.

    Designed to be instanciated then passed to the new pyproxmox class as an init parameter.
    """
    def __init__(self, url, username, password):
        self.url = url
        self.connect_data = {"username": username, "password": password}
        self.full_url = "https://{}:8006/api2/json/access/ticket".format(self.url)

        self.setup_connection()

    def setup_connection(self):
        """Setup connection to api."""
        self.ticket = ""
        self.csrf = ""

        self.response = requests.post(self.full_url, verify=False, data=self.connect_data)
        result = self.response

        if not self.response.ok:
            raise AssertionError('Authentification Error: HTTP Result: \n {}'.format(self.response))

        self.returned_data = {'status': {'code': self.response.status_code, 'ok': self.response.ok,
                                         'reason': self.response.reason}}
        self.returned_data.update(result.json())

        self.ticket = {'PVEAuthCookie': self.returned_data['data']['ticket']}
        self.csrf = self.returned_data['data']['CSRFPreventionToken']


# The meat and veg class
class PyProxmox:
    """
    A class that acts as a python wrapper for the Proxmox 2.x API.
    Requires a valid instance of the prox_auth class when initializing.

    GET and POST methods are currently implemented along with quite a few
    custom API methods.
    """
    # INIT
    def __init__(self, auth_class):
        """Take the prox_auth instance and extract the important stuff"""
        self.auth_class = auth_class
        self.get_auth_data()

    def get_auth_data(self,):
        """Get authentication data."""
        self.url = self.auth_class.url
        self.ticket = self.auth_class.ticket
        self.csrf = self.auth_class.csrf

    def connect(self, conn_type, option, post_data):
        """
        The main communication method.
        """
        self.full_url = "https://{}:8006/api2/json/{}".format(self.url, option)

        httpheaders = {'Accept': 'application/json',
                       'Content-Type': 'application/x-www-form-urlencoded'}
        disable_warnings(InsecureRequestWarning)
        if conn_type == "post":
            httpheaders['CSRFPreventionToken'] = str(self.csrf)
            self.response = requests.post(self.full_url, verify=False,
                                          data=post_data,
                                          cookies=self.ticket,
                                          headers=httpheaders)

        elif conn_type == "put":
            httpheaders['CSRFPreventionToken'] = str(self.csrf)
            self.response = requests.put(self.full_url, verify=False,
                                         data=post_data,
                                         cookies=self.ticket,
                                         headers=httpheaders)
        elif conn_type == "delete":
            httpheaders['CSRFPreventionToken'] = str(self.csrf)
            self.response = requests.delete(self.full_url, verify=False,
                                            data=post_data,
                                            cookies=self.ticket,
                                            headers=httpheaders)
        elif conn_type == "get":
            self.response = requests.get(self.full_url, verify=False,
                                         cookies=self.ticket)

        try:
            self.returned_data = self.response.json()
            self.returned_data.update({'status': {'code': self.response.status_code,
                                                'ok': self.response.ok,
                                                'reason': self.response.reason}})
            return self.returned_data
        except json.JSONDecodeError:
            print("Error in trying to process JSON")
            print(self.response)
            if (self.response.status_code == 401 and
               (not sys._getframe(1).f_code.co_name == sys._getframe(0).f_code.co_name)):
                print("Unexpected error: {} : {}".format(str(sys.exc_info()[0]),
                                                         str(sys.exc_info()[1])))
                print("try to recover connection auth")
                self.auth_class.setup_connection()
                self.get_auth_data()
                return self.connect(conn_type, option, post_data)

    # Methods using the GET protocol to communicate with the Proxmox API.
    # Cluster Methods

    def get_cluster_status(self):
        """Get cluster status information. Returns JSON"""
        data = self.connect('get', 'cluster/status', None)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return json.loads(data_json)

    def get_cluster_resources(self):
        """Get cluster resources. Returns JSON"""
        data = self.connect('get', 'cluster/resources', None)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return json.loads(data_json)

    def get_cluster_backup_schedule(self):
        """List vzdump backup schedule. Returns JSON"""
        data = self.connect('get', 'cluster/backup', None)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    def get_cluster_vm_next_id(self):
        """Get next VM ID of cluster. Returns JSON"""
        data = self.connect('get', 'cluster/nextid', None)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    def get_cluster_node_list(self):
        """Node list. Returns JSON"""
        data = self.connect('get', 'nodes/', None)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    def get_cluster_log(self):
        """log from Cluster. Returns JSON"""
        data = self.connect('get', 'cluster/log', None)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    # Node Methods
    def get_node_config(self, node):
        """Get node config. Returns JSON"""
        data = self.connect('get', 'nodes/{}/config'.format(node), None)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    def get_node_networks(self, node):
        """List available networks. Returns JSON"""
        data = self.connect('get', 'nodes/{}/network'.format(node), None)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    def get_node_interface(self, node, interface):
        """Read network device configuration. Returns JSON"""
        data = self.connect('get', 'nodes/{}/network/{}'.format(node, interface), None)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    def get_node_lxc_index(self, node):
        """LXC lxc index (per node). Returns JSON"""
        data = self.connect('get', 'nodes/{}/lxc'.format(node), None)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    def get_node_virtual_index(self, node):
        """Virtual machine index (per node). Returns JSON"""
        data = self.connect('get', 'nodes/{}/qemu'.format(node), None)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    def get_node_service_list(self, node):
        """Service list. Returns JSON"""
        data = self.connect('get', 'nodes/{}/services'.format(node), None)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    def get_node_service_state(self, node, service):
        """Read service properties. Returns JSON"""
        data = self.connect('get', 'nodes/{}/services/{}/state'.format(node, service), None)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    def get_node_storage(self, node, storage=None):
        """Get status for all datastores. Returns JSON"""
        data = self.connect('get', 'nodes/{}/storage'.format(node), storage)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    def get_node_finished_tasks(self, node):
        """Read task list for one node (finished tasks). Returns JSON"""
        data = self.connect('get', 'nodes/{}/tasks'.format(node), None)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    def get_node_dns(self, node):
        """Read DNS settings. Returns JSON"""
        data = self.connect('get', 'nodes/{}/dns'.format(node), None)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    def get_node_status(self, node):
        """Read node status. Returns JSON"""
        data = self.connect('get', 'nodes/{}/status'.format(node), None)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    def get_node_syslog(self, node):
        """Read system log. Returns JSON"""
        data = self.connect('get', 'nodes/{}/syslog'.format(node), None)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    def get_node_rrd(self, node, post_data):
        """Read node RRD statistics. Returns PNG"""
        data = self.connect('get', 'nodes/{}/rrd'.format(node), post_data)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    def get_node_rrd_data(self, node, post_data):
        """Read node RRD statistics. Returns RRD"""
        data = self.connect('get', 'nodes/{}/rrddata'.format(node), post_data)
        #data_json = json.dumps(data, indent=4, sort_keys=True)
        return data

    def get_node_task_by_upid(self, node, upid):
        """Get tasks by UPID. Returns JSON"""
        data = self.connect('get', 'nodes/{}/tasks/{}'.format(node, upid), None)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    def get_node_task_log_by_upid(self, node, upid):
        """Read task log. Returns JSON"""
        data = self.connect('get', 'nodes/{}/tasks/{}/log'.format(node, upid), None)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    def get_node_task_status_by_upid(self, node, upid):
        """Read task status. Returns JSON"""
        data = self.connect('get', 'nodes/{}/tasks/{}/status'.format(node, upid), None)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    # Scan
    def get_node_scan_methods(self, node):
        """Get index of available scan methods. Returns JSON"""
        data = self.connect('get', 'nodes/{}/scan'.format(node), None)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    def get_remote_iscsi(self, node):
        """Scan remote iSCSI server. Returns JSON"""
        data = self.connect('get', 'nodes/{}/scan/iscsi'.format(node), None)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    def get_node_lvmgroups(self, node):
        """Scan local LVM groups. Returns JSON"""
        data = self.connect('get', 'nodes/{}/scan/lvm'.format(node), None)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    def get_remote_nfs(self, node):
        """Scan remote NFS server. Returns JSON"""
        data = self.connect('get', 'nodes/{}/scan/nfs'.format(node), None)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    def get_node_usb(self, node):
        """List local USB devices. Returns JSON"""
        data = self.connect('get', 'nodes/{}/scan/usb'.format(node), None)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    # Access
    def get_cluster_acl(self):
        """ACL from Cluster. Returns JSON"""
        data = self.connect('get', 'access/acl', None)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    # LXC Methods
    def get_lxc_index(self, node, vmid):
        """Directory index. Returns JSON"""
        data = self.connect('get', 'nodes/{}/lxc/{}'.format(node, vmid), None)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    def get_lxc_status(self, node, vmid):
        """Get virtual machine status. Returns JSON"""
        data = self.connect('get', 'nodes/{}/lxc/{}/status/current'.format(node, vmid), None)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    def get_lxc_config(self, node, vmid):
        """Get container configuration. Returns JSON"""
        data = self.connect('get', 'nodes/{}/lxc/{}/config'.format(node, vmid), None)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    def get_lxc_rrd(self, node, vmid):
        """Read VM RRD statistics. Returns PNG"""
        data = self.connect('get', 'nodes/{}/lxc/{}/rrd'.format(node, vmid), None)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    def get_lxc_rrd_data(self, node, vmid):
        """Read VM RRD statistics. Returns RRD"""
        data = self.connect('get', 'nodes/{}/lxc/{}/rrddata'.format(node, vmid), None)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    # Agent methods
    def get_agent(self, node, vmid, endpoint):
        """Get vm informations via agent. Returns JSON"""
        data = self.connect('get', f'/nodes/{node}/qemu/{vmid}/agent/{endpoint}', None)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    # KVM Methods
    def get_virtual_list(self, node):
        """List virtual machine. Returns JSON"""
        data = self.connect('get', 'nodes/{}/qemu'.format(node), None)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    def get_virtual_index(self, node, vmid):
        """Directory index. Returns JSON"""
        data = self.connect('get', 'nodes/{}/qemu/{}'.format(node, vmid), None)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    def get_virtual_status(self, node, vmid):
        """Get virtual machine status. Returns JSON"""
        data = self.connect('get', 'nodes/{}/qemu/{}/status/current'.format(node, vmid), None)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    def get_virtual_config(self, node, vmid, current=False):
        """Get virtual machine configuration. Returns JSON"""
        if current:
            data = self.connect('get', 'nodes/{}/qemu/{}/config'.format(node, vmid), None)
        else:
            data = self.connect('get', 'nodes/{}/qemu/{}/config'.format(node, vmid), current)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    def get_virtual_rrd(self, node, vmid):
        """Read VM RRD statistics. Returns JSON"""
        data = self.connect('get', 'nodes/{}/qemu/{}/rrd'.format(node, vmid), None)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    def get_virtual_rrd_data(self, node, vmid):
        """Read VM RRD statistics. Returns JSON"""
        data = self.connect('get', 'nodes/{}/qemu/{}/rrddata'.format(node, vmid), None)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    # Storage Methods
    def get_storage_volume_data(self, node, storage, volume):
        """Get volume attributes. Returns JSON"""
        data = self.connect('get', 'nodes/{}/storage/{}/content/{}'.format(node, storage,
                                                                           volume), None)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    def get_storage_config(self, storage):
        """Read storage config. Returns JSON"""
        data = self.connect('get', 'storage/{}'.format(storage), None)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    def get_node_storage_content(self, node, storage):
        """List storage content. Returns JSON"""
        data = self.connect('get', 'nodes/{}/storage/{}/content'.format(node, storage), None)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    def get_node_storage_rrd(self, node, storage):
        """Read storage RRD statistics. Returns JSON"""
        data = self.connect('get', 'nodes/{}/storage/{}/rrd'.format(node, storage), None)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    def get_node_storage_rrd_data(self, node, storage):
        """Read storage RRD statistics. Returns JSON"""
        data = self.connect('get', 'nodes/{}/storage/{}/rrddata'.format(node, storage), None)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    def allocate_node_storage_vm(self, node, storage, post_data):
        """Create disk for a specific VM. Returns JSON"""
        data = self.connect('post', 'nodes/{}/storage/{}/content'.format(node, storage), post_data)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    # Methods using the POST protocol to communicate with the Proxmox API.
    # LXC Methods
    def create_lxc_container(self, node, post_data):
        """
        Create or restore a container. Returns JSON
        Requires a dictionary of tuples formatted [('postname1','data'),('postname2','data')]
        """
        data = self.connect('post', 'nodes/{}/lxc'.format(node), post_data)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    def shutdown_lxc_container(self, node, vmid):
        """Shutdown the container. Returns JSON"""
        post_data = None
        data = self.connect('post', 'nodes/{}/lxc/{}/status/shutdown'.format(node, vmid),
                            post_data)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    def start_lxc_container(self, node, vmid):
        """Start the container. Returns JSON"""
        post_data = None
        data = self.connect('post', 'nodes/{}/lxc/{}/status/start'.format(node, vmid), post_data)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    def stop_lxc_container(self, node, vmid):
        """Stop the container. Returns JSON"""
        post_data = None
        data = self.connect('post', 'nodes/{}/lxc/{}/status/stop'.format(node, vmid), post_data)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    def migrate_lxc_container(self, node, vmid, target):
        """Migrate the container to another node. Creates a new migration task. Returns JSON"""
        post_data = {'target': str(target)}
        data = self.connect('post', 'nodes/{}/lxc/{}/migrate'.format(node, vmid), post_data)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    # KVM Methods
    def create_virtual_machine(self, node, post_data):
        """
        Create or restore a virtual machine. Returns JSON
        Requires a dictionary of tuples formatted [('postname1','data'),('postname2','data')]
        """
        data = self.connect('post', 'nodes/{}/qemu'.format(node), post_data)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    def clone_virtual_machine(self, node, vmid, post_data):
        """
        Create a copy of virtual machine/template. Returns JSON
        Requires a dictionary of tuples formatted [('postname1','data'),('postname2','data')]
        """
        data = self.connect('post', 'nodes/{}/qemu/{}/clone'.format(node, vmid), post_data)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    def reset_virtual_machine(self, node, vmid):
        """Reset a virtual machine. Returns JSON"""
        post_data = None
        data = self.connect('post', 'nodes/{}/qemu/{}/status/reset'.format(node, vmid), post_data)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    def resume_virtual_machine(self, node, vmid):
        """Resume a virtual machine. Returns JSON"""
        post_data = None
        data = self.connect('post', 'nodes/{}/qemu/{}/status/resume'.format(node, vmid), post_data)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    def shutdown_virtual_machine(self, node, vmid):
        """Shut down a virtual machine. Returns JSON"""
        post_data = None
        data = self.connect('post', 'nodes/{}/qemu/{}/status/shutdown'.format(node, vmid),
                            post_data)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    def start_virtual_machine(self, node, vmid):
        """Start a virtual machine. Returns JSON
         :param     node:    node name
         :param     vmid:    vm id (e.g. 167)
         :type      node:       str
         :type      vmid:       int
         :return:   {   'status':        { 'code': http returncode, 'reason': http return string,
                                           'ok': return status }
                        'data':          { 'task String (UPID)'}
         :rtype     dict
        """
        post_data = None
        data = self.connect('post', 'nodes/{}/qemu/{}/status/start'.format(node, vmid), post_data)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    def stop_virtual_machine(self, node, vmid):
        """Stop a virtual machine. Returns JSON"""
        post_data = None
        data = self.connect('post', 'nodes/{}/qemu/{}/status/stop'.format(node, vmid), post_data)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    def suspend_virtual_machine(self, node, vmid):
        """Suspend a virtual machine. Returns JSON"""
        post_data = None
        data = self.connect('post', 'nodes/{}/qemu/{}/status/suspend'.format(node, vmid), post_data)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    def migrate_virtual_machine(self, node, vmid, post_data):
        """Migrate a virtual machine. Returns JSON"""
        data = self.connect('post', 'nodes/{}/qemu/{}/migrate'.format(node, vmid), post_data)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    def monitor_virtual_machine(self, node, vmid, command):
        """Send monitor command to a virtual machine. Returns JSON"""
        post_data = {'command': str(command)}
        data = self.connect('post', 'nodes/{}/qemu/{}/monitor'.format(node, vmid), post_data)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    def vncproxy_virtual_machine(self, node, vmid):
        """Creates a VNC Proxy for a virtual machine. Returns JSON"""
        post_data = None
        data = self.connect('post', 'nodes/{}/qemu/{}/vncproxy'.format(node, vmid), post_data)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    def rollback_virtual_machine(self, node, vmid, snapname):
        """Rollback a snapshot of a virtual machine. Returns JSON"""
        post_data = None
        data = self.connect('post', 'nodes/{}/qemu/{}/snapshot/{}/rollback'.format(node, vmid,
                                                                                   snapname),
                            post_data)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    def get_snapshot_config_virtual_machine(self, node, vmid, snapname):
        """Get snapshot config of a virtual machine. Returns JSON"""
        post_data = None
        data = self.connect('get', 'nodes/{}/qemu/{}/snapshot/{}/config'.format(node, vmid,
                                                                                snapname),
                            post_data)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    def get_snapshots_virtual_machine(self, node, vmid):
        """Get list of snapshots a virtual machine. Returns JSON"""
        post_data = None
        data = self.connect('get', 'nodes/{}/qemu/{}/snapshot'.format(node, vmid), post_data)
        if isinstance(data['data'], list):
            try:
                # data['data'].remove([s for s in data['data'] if s['name']=='current'])
                for snap in data['data'][:]:
                    if snap['name'] == 'current':
                        data['data'].remove(snap)
            except ValueError:
                print("Unexpected error:", sys.exc_info()[0])
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    def create_snapshot_virtual_machine(self, node, vmid, snapname, description='', vmstate=False):
        """
        Create Snapshot from VM. Returns JSON
        :param node: name of the node
        :param vmid: id of the vm
        :param snapname: title of the snapshot
        :param description: snapshot description
        :param vmstate: set if vmstatus should be saved too (useful for running vms)
        :return: dictionary with rest result and returned data
        """
        if vmstate:
            vmstate = 0
        else:
            vmstate = 1
        post_data = {'snapname': snapname, 'description': description, 'vmstate': vmstate}
        data = self.connect('post', 'nodes/{}/qemu/{}/snapshot'.format(node, vmid), post_data)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    # Network
    def create_node_network(self, node, post_data):
        """Create network device. Returns JSON"""
        data = self.connect('post', 'nodes/{}/network'.format(node),
                            post_data)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    def reload_node_network(self, node):
        """Reload all network. Returns JSON"""
        data = self.connect('put', 'nodes/{}/network'.format(node),
                            None)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    def reload_node_iface(self, node, iface, post_data):
        """Reload specific iface. Returns JSON"""
        data = self.connect('put', 'nodes/{}/network/{}'.format(node, iface),
                            post_data)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    # Methods using the DELETE protocol to communicate with the Proxmox API.
    # LXC
    def delete_lxc_container(self, node, vmid):
        """Deletes the specified lxc container. Returns JSON"""
        data = self.connect('delete', 'nodes/{}/lxc/{}'.format(node, vmid), None)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    # NODE
    def delete_node_network_config(self, node, vmbr):
        """Revert network configuration changes. Returns JSON"""
        data = self.connect('delete', 'nodes/{}/network/{}'.format(node, vmbr), None)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    def delete_node_interface(self, node, interface):
        """Delete network device configuration. Returns JSON"""
        data = self.connect('delete', 'nodes/{}/network/{}'.format(node, interface), None)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    # KVM
    def delete_virtual_machine(self, node, vmid):
        """Destroy the vm (also delete all used/owned volumes). Returns JSON"""
        data = self.connect('delete', 'nodes/{}/qemu/{}'.format(node, vmid), None)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    def delete_snapshot_virtual_machine(self, node, vmid, snapname, force=False):
        """Destroy the vm snapshot (also delete all used/owned volumes). Returns JSON
           :param force: (Boolean) For removal from config file,
                                   even if removing disk snapshots fails. """
        post_data = None
        if force:
            post_data = {}
            post_data['force'] = '1'
        data = self.connect('delete', 'nodes/{}/qemu/{}/snapshot/{}'.format(node, vmid, snapname),
                            post_data)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    # STORAGE
    def delete_storage_configuration(self, storageid):
        """Delete storage configuration. Returns JSON"""
        data = self.connect('delete', 'storage/{}'.format(storageid), None)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    # Methods using the PUT protocol to communicate with the Proxmox API.
    # NODE
    def set_node_dns_domain(self, node, domain):
        """Set the nodes DNS search domain. Returns JSON"""
        post_data = {'search': str(domain)}
        data = self.connect('put', 'nodes/{}/dns'.format(node), post_data)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    def set_node_subscription_key(self, node, key):
        """Set the nodes subscription key. Returns JSON"""
        post_data = {'key': str(key)}
        data = self.connect('put', 'nodes/{}/subscription'.format(node), post_data)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    def set_node_time_zone(self, node, timezone):
        """Set the nodes timezone. Returns JSON"""
        post_data = {'timezone': str(timezone)}
        data = self.connect('put', 'nodes/{}/time'.format(node), post_data)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    # LXC
    def set_lxc_container_options(self, node, vmid, post_data):
        """Set lxc virtual machine options. Returns JSON"""
        data = self.connect('put', 'nodes/{}/lxc/{}/config'.format(node, vmid), post_data)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    # KVM
    def set_virtual_machine_options(self, node, vmid, post_data):
        """Set KVM virtual machine options. Returns JSON"""
        data = self.connect('put', 'nodes/{}/qemu/{}/config'.format(node, vmid), post_data)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    def send_key_event_virtual_machine(self, node, vmid, key):
        """Send key event to virtual machine. Returns JSON"""
        post_data = {'key': str(key)}
        data = self.connect('put', 'nodes/{}/qemu/{}/sendkey'.format(node, vmid), post_data)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    def unlink_virtual_machine_disk_image(self, node, vmid, post_data):
        """Unlink disk images. Returns JSON"""
        data = self.connect('put', 'nodes/{}/qemu/{}/unlink'.format(node, vmid), post_data)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    # POOLS
    def list_pools(self):
        """List all pool. Returns JSON"""
        data = self.connect('get', 'pools', None)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    def get_pool_content(self, poolid):
        """Get Pool content. Returns JSON"""
        data = self.connect('get', 'pools/{}'.format(poolid), None)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json 

    def create_pool(self, post_data):
        """Create pool. Returns JSON"""
        data = self.connect('post', 'pools', post_data)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    def set_pool_data(self, poolid, post_data):
        """Update pool data. Returns JSON"""
        data = self.connect('put', 'pools/{}'.format(poolid), post_data)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    def delete_pool(self, poolid):
        """Delete Pool. Returns JSON"""
        data = self.connect('delete', 'pools/{}'.format(poolid), None)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json

    # STORAGE
    def update_storage_configuration(self, storageid, post_data):
        """Update storage configuration. Returns JSON"""
        data = self.connect('put', 'storage/{}'.format(storageid), post_data)
        data_json = json.dumps(data, indent=4, sort_keys=True)
        return data_json


if __name__ == "__main__":
    print("Module to interact with proxmox api")
