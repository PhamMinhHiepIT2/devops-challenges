#!/bin/bash

# Extract all order_id which has symbol=TSLA and side=sell and parse those values to curl command param
jq -r 'select(.symbol == "TSLA" and .side == "sell") | .order_id' ./transaction-log.txt | xargs -I {} curl -s "https://example.com/api/{}" >> ./output.txt

