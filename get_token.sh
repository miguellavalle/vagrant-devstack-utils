APIIP=$1
curl -s -X POST http://$APIIP/identity/v3/auth/tokens \
    -H "Content-type: application/json" \
    -d '{
            "auth": {
                "identity": {
                    "methods": [
                        "password"
                    ],
                    "password": {
                        "user": {
                            "domain": {
                                "name": "Default"
                            },
                            "name": "admin",
                            "password": "devstack"
                        }
                    }
                },
                "scope": {
                    "project": {
                        "domain": {
                            "name": "Default"
                        },
                        "name": "demo"
                    }
                }
            }
        }' | jq
