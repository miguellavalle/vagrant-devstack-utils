import ipaddress
import os
import time

from keystoneauth1 import identity
from keystoneauth1 import session
from neutronclient.v2_0 import client as neutron_client
from novaclient import client as nova_client


NOVA_API_VERSION = '2'
NETWORK_NAME = 'multinet'
HOSTS_CIDRS_MAP = {'allinone': ipaddress.ip_network('10.1.0.0/24'),
                   'compute1': ipaddress.ip_network('10.1.0.0/24'),
                   'compute2': ipaddress.ip_network('10.1.1.0/24'),
                   'compute3': ipaddress.ip_network('10.1.1.0/24')}


def get_login_data():
    login_data = {}
    login_data['username'] = os.environ['OS_USERNAME']
    login_data['password'] = os.environ['OS_PASSWORD']
    login_data['project_name'] = os.environ['OS_PROJECT_NAME']
    login_data['project_domain_id'] = os.environ['OS_PROJECT_DOMAIN_ID']
    login_data['user_domain_id'] = os.environ['OS_USER_DOMAIN_ID']
    login_data['auth_url'] = os.environ['OS_AUTH_URL']
    return login_data


def get_cirros_image(client):
    for image in client.glance.list():
        if 'cirros' in image.name:
            return image
    raise Exception('Cirros image not found')


def get_nics_dictionary(client):
    return([{'net-id':
             neutron.list_networks(name=NETWORK_NAME)['networks'][0]['id']}])


def get_tiny_flavor(client):
    for flavor in client.flavors.list():
        if flavor.name == 'm1.tiny':
            return flavor
    raise Exception('Tiny flavor not found')


def get_active_server(nova, neutron, host):
    image = get_cirros_image(nova)
    nics = get_nics_dictionary(neutron)
    flavor = get_tiny_flavor(nova)
    server = nova.servers.create('test-vm', image, flavor, nics=nics,
                                 availability_zone='nova:%s' % host)
    start_time = int(time.time())
    while True:
        time.sleep(5)
        server = nova.servers.get(server)
        if server.status == 'ACTIVE':
            return server
        elif server.status == 'ERROR':
            nova.servers.delete(server)
            raise Exception('VM went into ERROR state')
        elif int(time.time()) - start_time > 180:
            nova.servers.delete(server)
            raise Exception('VM timed out reaching ACTIVE state')


def get_ipv4_address(server):
    for net in server.addresses[NETWORK_NAME]:
        if net['version'] == 4:
            return net['addr']
    raise Exception("Couldn't find IPv4 address in server")


login_data = get_login_data()
auth = identity.Password(**login_data)
sess = session.Session(auth=auth)
neutron = neutron_client.Client(session=sess)
nova = nova_client.Client(NOVA_API_VERSION, session=sess)

for i in range(100):
    for host in HOSTS_CIDRS_MAP.keys():
        server = get_active_server(nova, neutron, host)
        server_ipv4 = get_ipv4_address(server)
        if ipaddress.ip_address(server_ipv4) not in HOSTS_CIDRS_MAP[host]:
            raise Exception('Server ipv4 address not in the correct segment')
        nova.servers.delete(server)
