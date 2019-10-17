import openstack

CLOUD = 'devstack-stable-admin'
NETWORK_NAME = 'openstacksdk-routed-network'
SEGMENT_ID = 2040


def find_network_segment(conn, network):
    for segment in conn.network.segments():
        if segment.network_id == network.id:
            return segment


def main():
    conn = openstack.connect(cloud=CLOUD)
    routed_network = conn.network.create_network(
        name=NETWORK_NAME, shared=True,
        provider_physical_network='physnet1', provider_network_type='vlan',
        provider_segmentation_id=SEGMENT_ID)
    segment_1 = find_network_segment(conn, routed_network)
    conn.network.update_segment(segment_1.id, name=('%s-%s' % (NETWORK_NAME,
                                                               'segment-1')))
    segment_2 = conn.network.create_segment(network_id=routed_network.id,
                                            name=('%s-%s' % (NETWORK_NAME,
                                                             'segment-2')),
                                            physical_network='physnet2',
                                            network_type='vlan',
                                            segmentation_id=SEGMENT_ID)
    subnet_1 = conn.network.create_subnet(name=('%s-%s' %
                                                (NETWORK_NAME,
                                                 'subnet-segment-1')),
                                          network_id=routed_network.id,
                                          ip_version=4, cidr='10.2.0.0/24',
                                          segment_id=segment_1.id)
    subnet_1_ipv6 = conn.network.create_subnet(
        name=('%s-%s' % (NETWORK_NAME, 'subnet-segment-1-ipv6')),
        network_id=routed_network.id, ip_version=6,
        cidr='fd2a:d02c:d36b:9a::/64', segment_id=segment_1.id)
    subnet_2 = conn.network.create_subnet(name=('%s-%s' %
                                                (NETWORK_NAME,
                                                 'subnet-segment-2')),
                                          network_id=routed_network.id,
                                          ip_version=4, cidr='10.2.1.0/24',
                                          segment_id=segment_2.id)
    subnet_2_ipv6 = conn.network.create_subnet(
        name=('%s-%s' % (NETWORK_NAME, 'subnet-segment-2-ipv6')),
        network_id=routed_network.id, ip_version=6,
        cidr='fd2a:d02c:d36b:9b::/64', segment_id=segment_2.id)
    print(conn.network.find_network(routed_network.name))
    for subnet in [subnet_1, subnet_1_ipv6, subnet_2, subnet_2_ipv6]:
        conn.network.delete_subnet(subnet)
    conn.network.delete_network(routed_network)


if __name__ == "__main__":
    main()
