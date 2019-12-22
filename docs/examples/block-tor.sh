#!/usr/bin/env bash

# TOR exit node IPs are published. Get a list with connectivity to Fastly
fsly_ip=$(dig +short global.ssl.fastly.net | head -1)
tor_ips="https://check.torproject.org/cgi-bin/TorBulkExitList.py?ip=${fsly_ip}"

# Create a temp file to store ips
tempfile=$(mktemp)

# Get the IPs and store in file
curl -s "${tor_ips}" | grep -v "^#" > $tempfile

# Add a new block list "tor_ips"
# This will fail harmlessly if the list is already defined
python fastly-blocklist.py \
    --list tor_ips \
    --new \
    --type block \
    --action block \
    --save

# Add the IPs to the blocklist
python fastly-blocklist.py \
    --list tor_ips \
    --removeall \
    --add \
    --file $tempfile \
    --save

# Deploy the config
python fastly-blocklist.py \
    --commit

# Remove our temp file
rm $tempfile
