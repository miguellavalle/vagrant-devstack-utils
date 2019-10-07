curl -s -X POST http://localhost:9696/v2.0/ports/$PORT_ID/bindings \
    -H "Content-type: application/json" \
    -H "X-Auth-Token: $TOKEN" \
    -d '{
            "binding": {
                "host": "$HOST"
            }
        }' | jq
