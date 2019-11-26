# fastly-blocklist/docs

## Tutorial

1. [Concepts](concepts.md)
1. [Create a new blocklist config](create-a-blocklist-config.md)
1. [Deploy blocklist to a service](deploy-blocklist-to-service.md)

## Examples

1. Block TOR IPs

    fastly-blocklist can be integrated with any threat intelligence or 'bad IP' list to block requests from these sources. See [examples/block-tor.sh](examples/block-tor.sh) for an example wrapper to block access for [TOR](https://www.torproject.org/) users.

1. Block US embargoed countries

    `geo` lists can be used to block requests from a list of country codes. See [examples/block-us-embargoed-countries.sh](examples/block-us-embargoed-countries.sh) to block all access from [OFAC sanctioned countries](https://en.wikipedia.org/wiki/United_States_sanctions).

1. Block POSTs from a list of geolocations

    You can use a `combo` list to combine match conditions from multiple constituent lists. This example at [examples/block-posts-from-geolocation.sh](examples/block-posts-from-geolocation.sh) blocks POST, PUT, and PATCH requests from a list of geolocations.
