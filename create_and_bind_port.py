import os
from keystoneauth1 import identity
from keystoneauth1 import session
from neutronclient.v2_0 import client as neutron_client


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
neutron = neutron_client.Client(session=sess)

try:
    network_id = os.environ['TEST_NETWORK_ID']
    body = {'port': {
                'network_id': network_id}}
    port = neutron.create_port(body=body)
    port_id = port['port']['id']
    body = {'port': {
                'binding:host_id': 'allinone'}}
    port = neutron.update_port(port_id, body)
finally:
    import pdb
    pdb.set_trace()
    neutron.delete_port(port_id)
