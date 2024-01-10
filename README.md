pyproxmox
=========

Update to py3 and Proxmox 6/7 from https//github.com/Daemonthread/pyproxmox
## A Python wrapper for the Proxmox 6.x and 7.x API

### Installation and dependency
    
    pip install pyproxmox3 requests

###### Example usage

1. Import everything from the module

		from pyproxmox3 import ProxAuth, PyProxmox

2. Create an instance of the prox_auth class by passing in the
url or ip of a server in the cluster, username and password

		INIT_AUTHENT = ProxAuth('vnode01.example.org', 'apiuser@pve', 'examplePassword')

ATTENTION! The realm can change : @pve or @pam, it depends on your configuration.

3. Create and instance of the pyproxmox class using the auth object as a parameter

		PROXMOX_EXEC = PyProxmox(INIT_AUTHENT)

4. Run the pre defined methods of the pyproxmox class

		STATUS = PROXPROXMOX_EXEC_EXEC.get_cluster_status()

NOTE They all return data in JSON format.
 
#### Methods requiring post_data

These methods need to passed a correctly formatted dictionary.
for example, if I was to use the createOpenvzContainer for the above example node
I would need to pass the post_data with all the required variables for proxmox.


Example for lxc :

	POST_DATA = {'ostemplate':'local:vztmpl/debian-10-standard_10.7-1_amd64.tar.gz',
				'vmid':'901','cores':'2','description':'test container',
				'rootfs':'10','hostname':'test.example.org','memory':'1024',
				'password':'testPassword','swap':'1024', 'ostype':'debian',
				'storage':'Stockage1'}
	
	PROXMOX_EXEC.create_openvz_container('vnode01', POST_DATA)

Example for kvm :

	POST_DATA = {'vmid':'9001', 'cores':'4', 'sockets': 1, 'description':'test kvm',
				'name':'test.example.org', 'memory':'1024', 'scsi0': 'Stockage1:102/vm-102-disk-0.qcow2,size=32G',
				'scsihw': 'virtio-scsi-pci', 'net0': 'virtio,bridge=vmbr1',
				'ide0': 'local:iso/fbsd-122-custom.iso,media=cdrom','ostype':'l26'}
	
	PROXMOX_EXEC.create_virtual_machine('vnode01', POST_DATA)

For more information on the accepted variables please see http//pve.proxmox.com/pve2-api-doc/

### Current List of Methods

#### GET Methods

##### Cluster Methods
		get_cluster_status()
"Get cluster status information. Returns JSON"

		get_cluster_backup_schedule()
"List vzdump backup schedule. Returns JSON"

		get_cluster_vm_next_id()
"Get next VM ID of cluster. Returns JSON"

		get_cluster_node_list()
"Node list. Returns JSON"

		get_cluster_log()
"log from Cluster. Returns JSON"

		get_cluster_acl()
"ACL from Cluster. Returns JSON"

##### Node Methods
		get_node_config(node)
"List available networks. Returns JSON"

		get_node_networks(node)
"List available networks. Returns JSON"
  
		get_node_interface(node, interface)
"Read network device configuration. Returns JSON"

		get_node_container_index(node)
"LXC container index (per node). Returns JSON"
 
		get_node_virtual_index(node)
"Virtual machine index (per node). Returns JSON"

		get_node_service_list(node)
"Service list. Returns JSON"
   
		get_node_service_state(node, service)
"Read service properties"

		get_node_storage(node)
"Get status for all datastores. Returns JSON"
  
		get_node_finished_tasks(node)
"Read task list for one node (finished tasks). Returns JSON"

		get_node_dns(node)
"Read DNS settings. Returns JSON"

		get_node_status(node)
"Read node status. Returns JSON"

		get_node_syslog(node)
"Read system log. Returns JSON"

		get_node_rrd(node)
"Read node RRD statistics. Returns PNG"
Ex: POST_DATA = {'node': 'r610'}"

		get_node_rrd_data(node)
"Read node RRD statistics. Returns RRD"

		get_node_task_by_upid(node, upid)
"Get tasks by UPID. Returns JSON"

		get_node_task_log_by_upid(node, upid)
"Read task log. Returns JSON"

		get_node_task_status_by_upid(node, upid)
"Read task status. Returns JSON"

##### Scan

		get_node_scan_methods(node)
"Get index of available scan methods, Returns JSON"

		get_remote_iscsi(node)
"Scan remote iSCSI server."

		get_node_lvmgroups(node)
"Scan local LVM groups"

		get_remote_nfs(node)
"Scan remote NFS server"

		get_node_usb(node)
"List local USB devices"

    
##### LXC Methods

		get_lxc_index(node, vmid)
"Directory index. Returns JSON"

		get_lxc_status(node, vmid)
"Get virtual machine status. Returns JSON"

		get_lxc_config(node, vmid)
"Get container configuration. Returns JSON"

		get_lxc_rrd(node, vmid)
"Read VM RRD statistics. Returns PNG"

		get_lxc_rrd_data(node, vmid)
"Read VM RRD statistics. Returns RRD"

##### Agent Methods
		get_agent(node, vmid, endpoint)
"Get vm informations via agent. Returns JSON"

##### KVM Methods
		get_virtual_list(node)
"List virtual machine. Returns JSON"

		get_virtual_index(node, vmid)
"Directory index. Returns JSON"

		get_virtual_status(node, vmid)
"Get virtual machine status. Returns JSON"

		get_virtual_config(node, vmid)
"Get virtual machine configuration. Returns JSON"

		get_virtual_rrd(node, vmid)
"Read VM RRD statistics. Returns JSON"

		get_virtual_rrd_data(node, vmid)
"Read VM RRD statistics. Returns JSON"

		get_snapshots_virtual_machine(node, vmid)
"Get list of snapshots a virtual machine. Returns JSON"

		create_snapshot_virtual_machine(node, vmid, snapname, description='')
"Create Snapshot from VM. Returns JSON"

		delete_snapshot_virtual_machine(node, vmid, snapname, force=False)
"Destroy the vm snapshot (also delete all used/owned volumes). Returns JSON"

##### Storage Methods

		get_storage_volume_data(node, storage, volume)
"Get volume attributes. Returns JSON"

		get_storage_config(storage)
"Read storage config. Returns JSON"
    
		get_node_storage_content(node, storage)
"List storage content. Returns JSON"

		get_node_storage_rrd(node, storage)
"Read storage RRD statistics. Returns JSON"

		get_node_storage_rrd_data(node, storage)
"Read storage RRD statistics. Returns JSON"

#### POST Methods

	
##### LXC Methods
	
		create_lxc_container(node, post_data)
"Create or restore a container. Returns JSON
Requires a dictionary of tuples formatted [('postname1','data'),('postname2','data')]"

		shutdown_lxc_container(node, vmid)
"Shutdown the container. Returns JSON"

		start_lxc_container(node, vmid)
"Start the container. Returns JSON"

		stop_lxc_container(node, vmid)
"Stop the container. Returns JSON"

		migrate_lxc_container(node, vmid, target)
"Migrate the container to another node. Creates a new migration task. Returns JSON"

##### KVM Methods

		create_virtual_machine(node, post_data)
"Create or restore a virtual machine. Returns JSON
Requires a dictionary of tuples formatted [('postname1','data'),('postname2','data')]"
		
		clone_virtual_machine(node,vmid, post_data)
"Create a copy of virtual machine/template. Returns JSON
Requires a dictionary of tuples formatted [('postname1','data'),('postname2','data')]
Ex: POST_DATA = {'name':'test2.example.org', 'newid':'9002'}"
		
		reset_virtual_machine(node, vmid)
"Reset a virtual machine. Returns JSON"
		
		resume_virtual_machine(node, vmid)
"Resume a virtual machine. Returns JSON"
	
		shutdown_virtual_machine(node, vmid)
"Shut down a virtual machine. Returns JSON"
	
		start_virtual_machine(node, vmid)
"Start a virtual machine. Returns JSON"
	
		stop_virtual_machine(node, vmid)
"Stop a virtual machine. Returns JSON"

		suspend_virtual_machine(node, vmid)
"Suspend a virtual machine. Returns JSON"
		
		migrate_virtual_machine(node, vmid, post_data)
		options : online=False, force=False, bwlimit=False, migration_network=False,
"Migrate a virtual machine. Returns JSON"

		monitor_virtual_machine(node, vmid, command)
"Send monitor command to a virtual machine. Returns JSON"
		
		vncproxy_virtual_machine(node, vmid)
"Creates a VNC Proxy for a virtual machine. Returns JSON"

		rollback_virtual_machine(node, vmid, snapname)
"Rollback a snapshot of a virtual machine. Returns JSON"

		get_snapshot_config_virtual_machine(node, vmid, snapname)
"Get snapshot config of a virtual machine. Returns JSON"

		create_node_network(node, post_data)
"Create network device. Returns JSON
Ex: POST_DATA = {'iface': 'vmbr5', 'type': 'bridge'}"

		reload_node_network(node, post_data)
"Reload network configuration. Returns JSON
Ex: POST_DATA = {'node': 'r610'}"

		reload_node_iface(node, iface, post_data)
"Reload network configuration. Returns JSON
Ex: POST_DATA = {'iface': IFACE, 'node': NODE, 'type': 'bridge'}"

##### Storage Methods

		allocate_node_storage_vm(node, storage, post_data)
"Create disk for a specific VM. Returns JSON"
#### DELETE Methods
    
##### LXC
    
		delete_lxc_container(node, vmid)
"Deletes the specified lxc container"

##### NODE
    
		delete_node_network_config(node)
"Revert network configuration changes."
  
		delete_node_interface(node, interface)
"Delete network device configuration"
    
##### KVM
    
		delete_virtual_machine(node, vmid)
"Destroy the vm (also delete all used/owned volumes)."
        
##### POOLS
		list_pools()
"List all pool. Returns JSON"

		get_pool_content(poolid)
"Get Pool content. Returns JSON"

		create_pool(post_data)
"Create pool. Returns JSON"

		set_pool_data(poolid, post_data)
"Update pool data."

		delete_pool(poolid)
"Delete Pool"

##### STORAGE
		delete_storage_configuration(storageid)
"Delete storage configuration"

#### PUT Methods

##### NODE
		set_node_dns_domain(node, domain)
"Set the nodes DNS search domain"

		set_node_subscription_key(node, key)
"Set the nodes subscription key"
        
		set_node_time_zone(node, timezone)
"Set the nodes timezone"

##### LXC
		set_lxc_container_options(node, vmid, post_data)
"Set lxc virtual machine options."
  
##### KVM
		set_virtual_machine_options(node, vmide, post_data)
"Set KVM virtual machine options."

		send_key_event_virtual_machine(node, vmid, key)
"Send key event to virtual machine"

		unlink_virtual_machine_disk_image(node, vmid, post_data)
"Unlink disk images
Ex: POST_DATA = {'idlist': 'ide0'}"

##### STORAGE
		update_storage_configuration(storageid, post_data)
"Update storage configuration"
