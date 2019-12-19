#!/usr/bin/env bash

# Create a geo list of embargoed countries
python fastly-blocklist.py \
    --list embargoed_geos \
    --new \
    --type geo \
    --action block \
    --save

# Add country codes to the geo list
python fastly-blocklist.py \
    --list embargoed_geos \
    --add \
    --item 'IR','KP','SY','SD','CU','VE' \
    --save

# Deploy the fastly-blocklist config
python fastly-blocklist.py \
    --commit
