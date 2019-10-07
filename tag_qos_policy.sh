APIIP=$1
POLICY_ID=$2
curl -s -X PUT http://$APIIP:9696/v2.0/policies/$POLICY_ID/tags \
    -H "Content-type: application/json" \
    -H "X-Auth-Token: $TOKEN" \
    -d '{
            "tags": [
                "red",
                "blue"
            ]
        }' | jq
