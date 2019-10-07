curl -s -X GET http://192.168.33.12:9696/v2.0/network-ip-availabilities?network_id=22e1b87a-e2d4-4c12-a8ab-ce7da005f3e0\&network_id=3e1a16c1-288b-47e5-8aab-666a08016588\&network_id=85d60f9a-40a2-44a6-b6f7-ca414864058f\&network_id=d4360548-cc7a-498f-bdba-dd4b63644797 \
    -H "Content-type: application/json" \
    -H "X-Auth-Token: $TOKEN" | jq
