source ~/demo-openrc
date -u
start_time="$(date -u +%s)"
openstack security group list
end_time="$(date -u +%s)"
elapsed="$(($end_time-$start_time))"
date -u
echo "Total of $elapsed seconds elapsed for process"
