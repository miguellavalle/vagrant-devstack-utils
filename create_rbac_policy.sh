PROJECT_ID=$1
SECGROUP_ID=$2
REQUEST_HEAD='
    {
        "rbac_policy": {
            "action": "access_as_shared",
            "object_type": "security_group",
            "target_tenant": '
REQUEST_MIDDLE='
            "object_id": '
REQUEST_TAIL='
        }
   }'
REQUEST="$REQUEST_HEAD \"$PROJECT_ID\", $REQUEST_MIDDLE \"$SECGROUP_ID\" $REQUEST_TAIL"
curl -s -X POST http://$APIIP:9696/v2.0/rbac-policies \
    -H "Content-type: application/json" \
    -H "X-Auth-Token: $TOKEN" \
    -d "$REQUEST" | jq
