
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
    name: neo4j_inventory
    plugin_type: inventory
    short_description: Returns ansible inventory from neo4j
    description: Returns Ansible inventory from neo4j
    options:
      plugin:
          description: Name of the plugin
          required: true
          choices: ['neo4j_inventory']
      query:
        description: details of the objects to find
        required: true
'''

import os
from ansible.plugins.inventory import BaseInventoryPlugin
from ansible.errors import AnsibleError, AnsibleParserError

from neo4j import GraphDatabase

class InventoryModule(BaseInventoryPlugin):
    NAME = 'neo4j_inventory'


    def _get_neo4j_data(self):
        neo4j_uri = 'bolt://{}:{}'.format(self.neo4j_host,self.neo4j_port)

        driver = GraphDatabase.driver(neo4j_uri, auth=(self.neo4j_user, self.neo4j_pass))

        def get_hosts_in_groups(tx, host_node, relation, group_node, host_label, group_label, max_length=1):
            if relation == "*":
                cypher_string = "MATCH (a:{})-[* 1..{}]-(b:{}) WHERE EXISTS (a.{}) AND EXISTS (b.{}) RETURN a.{}, b.{}".format(host_node, max_length, group_node, host_label, group_label, host_label, group_label)
            else:
                cypher_string = "MATCH (a:{})-[:{}]-(b:{}) WHERE EXISTS (a.{}) AND EXISTS (b.{}) RETURN a.{}, b.{}".format(host_node, relation, group_node, host_label, group_label, host_label, group_label)
            inventory_data = {}
            for record in tx.run(cypher_string):
                if record["a.{}".format(host_label)]:
                    hostname = record["a.{}".format(host_label)]
                    inventory_data[hostname] = record["b.{}".format(group_label)]
            return inventory_data
        with driver.session() as session:
            data = session.read_transaction(get_hosts_in_groups, **self.neo4j_query)
        driver.close()
        return data


    def _populate(self):
        '''Return the hosts and groups'''
        self.myinventory = self._get_neo4j_data()
        for hostname,data in self.myinventory.items():
            gname = self.inventory.add_group(data)
            self.inventory.add_host(host=hostname.upper(), group=gname.upper())

    def parse(self, inventory, loader, path, cache):
        '''Return dynamic inventory from source '''
        super(InventoryModule, self).parse(inventory, loader, path, cache)
        self._read_config_data(path)
        try:
            #Store the options from the YAML file
            self.neo4j_user = os.environ['neo4j_user']
            self.neo4j_pass = os.environ['neo4j_password']
            self.neo4j_host = os.environ['neo4j_host']
            self.neo4j_port = os.environ['neo4j_bolt_port']
            self.neo4j_query = self.get_option('query')
        except Exception as e:
            raise AnsibleParserError(
                'All correct options required: {}'.format(e))        
        self._populate()
        