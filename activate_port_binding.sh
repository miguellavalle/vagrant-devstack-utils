curl -s -X PUT http://localhost:9696/v2.0/ports/$PORT_ID/bindings/$HOST/activate \
    -H "Content-type: application/json" \
    -H "X-Auth-Token: $TOKEN" | jq
