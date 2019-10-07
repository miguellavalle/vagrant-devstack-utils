import os
import random

from keystoneauth1 import identity
from keystoneauth1 import session
from neutronclient.v2_0 import client as neutron_client
from keystoneclient.v3 import client as keystone_client


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
keystone = keystone_client.Client(session=sess)

secgroups_ids = []
projects_ids = []
secgroups_in_project = 0
created_secgroups_count = 0
created_projects = 0
try:
    while created_secgroups_count < 6000:
        if secgroups_in_project <= 0:
            project = keystone.projects.create(
                name='test-project-%s' % created_projects,
                domain=login_data['user_domain_id'])
            secgroups_in_project = random.randint(1, 7)
            projects_ids.append(project.id)
            new_project = True
            created_projects += 1
        body = {'security_group': {
                    'name': 'test-secgroup-%s' % created_secgroups_count,
                    'description': ('Test security group %s' %
                                    created_secgroups_count),
                    'project_id': project.id}}
        secgroup = neutron.create_security_group(body=body)
        secgroups_in_project -= 1
        secgroups_ids.append(secgroup['security_group']['id'])
        created_secgroups_count += 1
        if new_project:
            new_project = False
            default_secgroup = neutron.list_security_groups(
                name='default', project_id=project.id)['security_groups'][0]
            secgroups_ids.append(default_secgroup['id'])
            created_secgroups_count += 1
        print(created_secgroups_count)
    import pdb
    pdb.set_trace()
finally:
    for secgroup_id in secgroups_ids:
        neutron.delete_security_group(secgroup_id)
    for project_id in projects_ids:
        keystone.projects.delete(project_id)
