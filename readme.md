# Neo4j Inventory Plugin

[Neo4j Python Driver](https://github.com/neo4j/neo4j-python-driver) - has examples of how to run queries

[Dynamic Inventory Presentation](https://www.ansible.com/managing-meaningful-inventories) - second half talks about how to write an inventory plugin

[Writing Inventory Plugins](https://termlen0.github.io/2019/11/16/observations/) - great blog with code samples of a dynamic inventory plugin and how to write one

## Files in the inventory folder

* **neo4j_groupby_os.yml** - in playbook directory, entry point for the inventory script.
Reference this file when referencing an inventory.
This file allows parameters to be passed to the actual plugin script.
For different queries there can be multiple files referencing the same plugin.
* **inventory_plugins\neo4j_inventory.py** - the plugin script.
This is called by the config file and processes inputs, and returns the inventory objects
* **ansible.cfg** - general ansible config file.
This sample lists additional inventory plugins to load.
The custom plugin must be listed here.

> **_NOTE:_**  When using inventory plugins, those files must be kept separate from any playbooks that reference it, at least when using it in awx.
When awx runs an inventory sync with a plugin, it creates an inventory object.
When awx then tries to run a playbook with that inventory, it will use the ansible.cfg settings to attempt to parse that text inventory as a script, which will generate obtuse syntax error messages.
The key seems to be having the inventory files all in a subfolder, separated from the playbook root.
More info can be found in the comments of [this](https://github.com/ansible/awx/issues/3365) github issue.

## Environment variables

Connection information is to be set in environment variables, rather than passed in the config file.
This is to be compatible with awx custom credential type options.
To run via the command line you must set environment variables first:

```bash
export neo4j_user='neo4j'
export neo4j_password='neo5j'
export neo4j_host='localhost'
export neo4j_bolt_port='7687'
```

To test the inventory file:

```bash
ansible-inventory -i neo4j_inventory.yml --playbook-dir ./ --list
```

To use it in a playbook:

```bash
ansible-playbook test.yml -i neo4j_inventory.yml
```

neo4j_inventory.yml query parameters:

the query parameters are designed to map certain node types to an ansible host, and other node types to an ansible group. Relationships between the two would be used to specify the group membership.

for example: the "hostname" node type could map to the ansible host, and the "HW_Manufacturer" node type could map to the ansible group.  with relationships defined in neo4j, some hosts are related to certain manufacturers.  This would be defined like this:

```yaml
  group_node: HW_Manufacturer
  group_label: Name
  host_node: Hostname
  host_label: Name
  relation: "*"
  max_length: 2
```

Note that in this case there are multiple 'hops' to get from the host node to the group node, so the relation is listed as "*".  If there is a specific, direct relationship to follow, this can be listed instead of the wildcard.  In the case of the wildcard, a max_length value is recommended, as the query could take a significant amount of time (and crash your laptop) if left wide open.

# Python SQL Driver

https://docs.microsoft.com/en-us/sql/connect/python/pyodbc/python-sql-driver-pyodbc?view=sql-server-ver15

## Install commands

https://docs.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server
### Ubuntu 18.04


```bash
 sudo apt-get install unixodbc-dev
 sudo pip install pyodbc

  sudo su
  curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
  curl https://packages.microsoft.com/config/ubuntu/18.04/prod.list > /etc/apt/sources.list.d/mssql-release.list
  exit
  sudo apt-get update
  sudo ACCEPT_EULA=Y apt-get install msodbcsql17
  # optional: for bcp and sqlcmd
  sudo ACCEPT_EULA=Y apt-get install mssql-tools
  echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bash_profile
  echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc
  source ~/.bashrc
  # optional: for unixODBC development headers
  sudo apt-get install unixodbc-dev
  ```

### RHEL, OEL, CentOS

```bash
  
sudo su

#Download appropriate package for the OS version
#Choose only ONE of the following, corresponding to your OS version

#RedHat Enterprise Server 7
curl https://packages.microsoft.com/config/rhel/7/prod.repo > /etc/yum.repos.d/mssql-release.repo

exit
sudo yum remove unixODBC-utf16 unixODBC-utf16-devel #to avoid conflicts
sudo ACCEPT_EULA=Y yum install msodbcsql17
# optional: for bcp and sqlcmd
sudo ACCEPT_EULA=Y yum install mssql-tools
echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bash_profile
echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc
source ~/.bashrc
# optional: for unixODBC development headers
sudo yum install unixODBC-devel


sudo yum install gcc-c++
sudo -H pip install pyodbc
```