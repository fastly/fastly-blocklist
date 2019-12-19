#!/usr/bin/env bash

# Create a geo list of countries which will not
# be permitted to send POST/PUT/PATCH requests
python fastly-blocklist.py \
    --list no_post_geos \
    --new \
    --type geo \
    --action none \
    --save

# Add country codes to the geo list
python fastly-blocklist.py \
    --list no_post_geos \
    --add \
    --item 'IR','KP','SY','SD','CU','VE' \
    --save

# Create a var list of banned HTTP methods
python fastly-blocklist.py \
    --list geo_banned_methods \
    --new \
    --type var \
    --action none \
    --variable 'req.method' \
    --save

# Add banned methods to the var list
python fastly-blocklist.py \
    --list geo_banned_methods \
    --add \
    --item 'POST','PUT','PATCH' \
    --save

# Create a combo list to block banned methods from
# selected geolocations
python fastly-blocklist.py \
    --list block_posts_from_geolocation \
    --new \
    --type combo \
    --action block \
    --save

# Add the constituent lists to combo list
python fastly-blocklist.py \
    --list block_posts_from_geolocation \
    --add \
    --item 'no_post_geos','geo_banned_methods' \
    --save

# Deploy the the fastly-blocklist config
python fastly-blocklist.py \
    --commit
