
from __future__ import (absolute_import, division, print_function)
from subprocess import Popen, PIPE
import pyodbc
from ansible.errors import AnsibleError, AnsibleParserError
from ansible.plugins.inventory import BaseInventoryPlugin
import os
__metaclass__ = type

DOCUMENTATION = r'''
    name: mssql_inventory
    plugin_type: inventory
    short_description: Returns ansible inventory from mssql
    description: Returns Ansible inventory from mssql
    options:
      plugin:
          description: Name of the plugin
          required: true
          choices: ['mssql_inventory']
      query_string:
        description: details of the objects to find
        required: true
'''


class InventoryModule(BaseInventoryPlugin):
    NAME = 'mssql_inventory'

    def _get_mssql_data(self):
        """Run a SQL query."""
        cnxn = pyodbc.connect(driver='{ODBC Driver 17 for SQL Server}',
            server=self.mssql_host,
            database=self.mssql_db,
            uid=self.mssql_user,
            trusted_connection='yes'
        )
        cursor = cnxn.cursor()
        inventory_data = {}
        cursor.execute(self.mssql_query)
        row = cursor.fetchone() 
        while row: 
            hostname=row.hosts
            inventory_data[hostname]=row.groups
            row = cursor.fetchone()
        return inventory_data
        cnxn.close()


    def _kinit(self):
        kinit = '/usr/bin/kinit'
        # Get Fresh Kerberos Ticket
        kinit_args = [ kinit, self.mssql_user ]
        kinit = Popen(kinit_args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        kinit.stdin.write('%s\n' % self.mssql_pass)
        kinit.wait()

    def _populate(self):
        '''Retrieve kerberos token'''
        self._kinit()
        '''Connect to MSSQL database'''

        '''Return the hosts and groups'''
        self.myinventory = self._get_mssql_data()
        for hostname,data in self.myinventory.items():
            gname = self.inventory.add_group(data)
            self.inventory.add_host(host=hostname, group=gname)

    def parse(self, inventory, loader, path, cache):
        '''Return dynamic inventory from source '''
        super(InventoryModule, self).parse(inventory, loader, path, cache)
        self._read_config_data(path)
        try:
            self.mssql_user = os.environ['MSSQL_USER']
            self.mssql_pass = os.environ['MSSQL_PASSWORD']
            self.mssql_host = os.environ['MSSQL_HOST']
            self.mssql_port = os.environ['MSSQL_PORT']
            self.mssql_db = os.environ['MSSQL_DB']
            self.mssql_query = self.get_option('query_string')
        except Exception as e:
            raise AnsibleParserError(
                'All correct options required: {}'.format(e))
        self._populate()
