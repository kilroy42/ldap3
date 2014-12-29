# Created on 2013.05.23
#
# @author: Giovanni Cannata
#
# Copyright 2015 Giovanni Cannata
#
# This file is part of ldap3.
#
# ldap3 is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ldap3 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with ldap3 in the COPYING and COPYING.LESSER files.
# If not, see <http://www.gnu.org/licenses/>.

import unittest
from ldap3 import Server, Connection, ServerPool, STRATEGY_REUSABLE_THREADED
from ldap3.protocol.rfc4511 import LDAPDN, AddRequest, AttributeList, Attribute, AttributeDescription, \
    AttributeValue, ModifyRequest, ValsAtLeast1, Changes, Change, Operation, PartialAttribute, Vals
from test import test_server, test_port, test_user, test_password, test_authentication, test_strategy,\
    test_base, generate_dn, test_lazy_connection, test_get_info, test_server_mode, test_pooling_strategy, test_pooling_active, test_pooling_exhaust


class Test(unittest.TestCase):
    def setUp(self):
        if isinstance(test_server, (list, tuple)):
            server = ServerPool(pool_strategy=test_pooling_strategy, active=test_pooling_active, exhaust=test_pooling_exhaust)
            for host in test_server:
                server.add(Server(host=host, port=test_port, allowed_referral_hosts=('*', True), get_info=test_get_info, mode=test_server_mode))
        else:
            server = Server(test_server, test_port, allowed_referral_hosts=('*', True), get_info=test_get_info, mode=test_server_mode)
        self.connection = Connection(server, auto_bind=True, client_strategy=test_strategy, user=test_user, password=test_password, authentication=test_authentication, lazy=False, pool_name='pool1')

    def tearDown(self):
        self.connection.unbind()
        if self.connection.strategy_type == STRATEGY_REUSABLE_THREADED:
            self.connection.strategy.terminate()
        self.assertFalse(self.connection.bound)

    def test_modify(self):
        attribute1 = Attribute()
        vals1 = ValsAtLeast1()
        vals1[0] = AttributeValue('tost')
        attribute1['type'] = AttributeDescription('sn')
        attribute1['vals'] = vals1

        attribute2 = Attribute()
        vals2 = ValsAtLeast1()
        vals2[0] = AttributeValue('tust')
        attribute2['type'] = AttributeDescription('givenName')
        attribute2['vals'] = vals2

        attribute3 = Attribute()
        vals3 = ValsAtLeast1()
        vals3[0] = AttributeValue('inetOrgPerson')
        attribute3['type'] = AttributeDescription('objectClass')
        attribute3['vals'] = vals3

        attributes = AttributeList()
        attributes[0] = attribute1
        attributes[1] = attribute2
        attributes[2] = attribute3

        add_req = AddRequest()
        add_req['entry'] = LDAPDN(generate_dn(test_base, 'test-modify'))
        add_req['attributes'] = attributes

        result = self.connection.post_send_single_response(self.connection.send('addRequest', add_req))
        if isinstance(result, int):
            self.connection.get_response(result)
        vals_mod1 = Vals()
        vals_mod1[0] = 'test-modified'
        part_attr1 = PartialAttribute()
        part_attr1['type'] = AttributeDescription('sn')
        part_attr1['vals'] = vals_mod1
        change1 = Change()
        change1['operation'] = Operation('replace')
        change1['modification'] = part_attr1
        changes = Changes()
        changes[0] = change1
        modify_req = ModifyRequest()
        modify_req['object'] = LDAPDN(generate_dn(test_base, 'test-modify'))
        modify_req['changes'] = changes
        result = self.connection.post_send_single_response(self.connection.send('modifyRequest', modify_req))
        if isinstance(result, int):
            self.connection.get_response(result)
        self.assertTrue(True)