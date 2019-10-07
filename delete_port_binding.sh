curl -s -X DELETE http://localhost:9696/v2.0/ports/$PORT_ID/bindings/$HOST \
    -H "Content-type: application/json" \
    -H "X-Auth-Token: $TOKEN" | jq
