import os

import netaddr

from keystoneauth1 import identity
from keystoneauth1 import session
from neutronclient.v2_0 import client


def get_login_data():
    login_data = {}
    login_data['username'] = os.environ['OS_USERNAME']
    login_data['password'] = os.environ['OS_PASSWORD']
    login_data['project_name'] = os.environ['OS_PROJECT_NAME']
    login_data['project_domain_id'] = os.environ['OS_PROJECT_DOMAIN_ID']
    login_data['user_domain_id'] = os.environ['OS_USER_DOMAIN_ID']
    login_data['auth_url'] = os.environ['OS_AUTH_URL']
    return login_data


login_data = get_login_data()
auth = identity.Password(**login_data)
sess = session.Session(auth=auth)
neutron = client.Client(session=sess)

network_ids = []
cidr = netaddr.IPNetwork('10.100.0.0/28')

try:
    for i in range(3):
        body = {'network': {'name': 'sample_network_%s' % i,
                'admin_state_up': True}}

        network = neutron.create_network(body=body)
        network_id = network['network']['id']
        network_ids.append(network_id)
        body = {'subnets': [{'cidr': str(cidr),
                'ip_version': 4, 'network_id': network_id}]}
        subnet = neutron.create_subnet(body=body)
        cidr = cidr.next()

    availability = (
        neutron.list_network_ip_availabilities(network_id=network_ids))
finally:
    for network_id in network_ids:
        neutron.delete_network(network_id)
