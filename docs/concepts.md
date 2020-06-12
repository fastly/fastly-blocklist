# fastly-blocklist/docs/concepts

## Lists

fastly-blocklist config and behavior is mostly defined by the lists you create. Each type of list matches against different characteristics of a client HTTP request. When a list matches we execute its corresponding `action` (usually `log` or `block`).

1. allow

    IP addresses added to an `allow` list are permitted access regardless of the other logic applied by fastly-blocklist. This is essentially a "global allowlist" you'd apply for trusted IP addresses which should _never_ get blocked. List items are IPv4 or v6 addresses and can include negation and CIDR notation e.g. `!10.0.0.0/8`.

1. geo

    `geo` lists use Fastly [geolocation](https://docs.fastly.com/vcl/geolocation/) to identify the country from which a request originated. These can be used to limit traffic countries you don't want or expect to visit your service. List items must be a [two letter country code](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2).

1. block

    IPs in `block` lists are permanently denied access to the service (assuming list `action` is also set to block). This is the most traditional type of [ACL](https://docs.fastly.com/en/guides/about-acls) or "blocklist" we use. List items are IPv4 or v6 addresses and can include negation and CIDR notation e.g. `172.16.0.0/12`.

1. temp

    `temp` lists are used to temporarily block access from a set of IPs. These entries are no longer enforced after the list's `block_length` has elapsed and are best used as a dynamic reputation list or to reduce the impact of blocking a public IP address. List items are IPv4 or v6 addresses only and _cannot_ include negation or CIDR.

1. var

    Variable, or `var` lists inspect any [VCL variable](https://docs.fastly.com/vcl/variables/) associated with a request (set by `--variable`). This list type can be used to identify traffic matching many different attributes, but is commonly used to inspect things like "User-Agent" (`req.http.User-Agent`), or request URL (`req.url`)). List items can be any string, and are compared as either an exact match (`--match exact`) or as a regular expression (`--match regexp`).

1. combo

    `combo` lists combine any 2+ existing lists, and will match traffic when _all included lists_ are matched. These can be used to evaluate more complex conditions than other types. For example, we can block form submissions from the US to a service by combining `geo` and `var` lists: "request geolocation == US AND `req.method` IN ['POST', 'PUT', 'PATCH']". List items _must_ match the names of other, existing, lists.

## Actions

The action is the VCL applied when a list is matched.

1. none

    No action is applied. This is the default action for a new list and enables creating lists which _only_ take an action when used later on in a `combo` list.

1. log

    Log the offending request to the logging endpoint and [format](https://docs.fastly.com/en/guides/custom-log-formats) specified. This action is empty by default.

1. block

    Log AND block the offending request. We return a basic block page by default: `error 403 "Forbidden";`.


The VCL which runs for log and block actions is defined in your configuration with `--log 'xxx'` and `--block 'xxx'`.

## State

fastly-blocklist has three locations for state -- local (a configuration file on disk), running (the information read from a config file, with your changes made in memory), and remote (the VCL, ACLs, and Dictionaries deployed to a service). When you use fastly-blocklist, you sync/save/make changes/deploy between all of these.

1. sync

    Fetch the existing fastly-blocklist configuration from a live service. This can be used to get remote state when you don't have access to a local config file.

1. save

    Save the running configuration to a local config file. You'll often use this in _every_ command, but it can be omitted when testing or to make temporary changes to the live service.

1. commit

    Deploy the running configuration to the live service(s). Your config will take effect on the service immediately.


When fastly-blocklist starts, it will _always_ try to read from your local configuration first. Changes are _only_ made to local or live config when specified with `--save` (local), or `--commit` (live/deployed configuration).

## Next Steps
Now that we've covered the basics, let's create a blocklist config. Go on to the [next tutorial here](create-a-blocklist-config.md).

