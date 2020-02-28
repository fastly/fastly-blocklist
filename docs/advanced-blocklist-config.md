# fastly-blocklist/docs/advanced-config-blocklist

This document covers advanced settings available and direct manipulation of a fastly-blocklist [configuration file](../example-config).

When first using `fastly-blocklist`, the application will automatically create a new configuration file (`config.blocklist` in your current working directory by default). This is a JSON file containing persistent local configuration and will be updated each time you issue a `--save` command. You'll generally manipulate this file through the application and may never need to edit it directly, however this may be necessary for more advanced use cases like:

* Setting a log line/format to be executed when one of your blocklists is matched
* Changing the default `block` page or behavior
* Using `fastly-blocklist` from within your custom VCL logic
* Changing the nodes on which blocklist logic is run (for services with shielding in place)

## Global Configuration

```
{
    "log": "",
    "block": "error 403 \"Forbidden\";"
}
```

* `log` - A line of VCL invoked whenever a request matches a list with action `log` or `block`. This should be a JSON escaped string containing your log target name and vcl variables to be logged. It might look something like this:
    ```
    "log": "log {\"syslog \"\"} req.service_id {\"\" YOUR_LOG_TARGET :: \"} {\"{\"type\":\"req\",\"service_id\":\"\"} req.service_id {\"\",\"start_time\":\"\"} time.start.sec {\"\",\"fastly_info\":\"\"} fastly_info.state {\"\",\"datacenter\":\"\"} server.datacenter {\"\",\"client_ip\":\"\"} client.ip {\"\",\"req_method\":\"\"} req.request {\"\",\"req_uri\":\"\"} cstr_escape(req.url)};"
    ```
* `block` - A line of VCL invoked whenever a request hits a list with action `block`. You may wish to change from the default `"error 403 \"Forbidden\";` in order to [serve a custom synthetic response](https://docs.fastly.com/en/guides/creating-error-pages-with-custom-responses#create-a-vcl-snippet-for-a-synthetic-response) back to the client when a request is blocked.

## Services

```
{
    "services": [
        {
            "id": "SERVICEID",
            "snippet_name": "fastlyblocklist_RANDOMSTRING",
            "type": "recv",
            "priority": "10",
            "options": {
                "edge_only": true,
                "var_ip": "client.ip"
            }
        }
    ]
}
```

* `services` - An array of configurations for Fastly services to target. When multiple services are defined, a given `--commit` will apply your locally defined blocklists to _each_ service.
* `id` - The Fastly service ID to target.
* `snippet_name` - Any custom name for your blocklist VCL snippet. This should _always_ start with `fastlyblocklist_` to ensure the application can find an existing snippet.
* `type` - The VCL function/"sub" in which to place your snippet. This will typically be `recv` (the snippet logic runs in `vcl_recv` before any other processing is done), but can be changed to any valid function. You may use type `none` if you want to explicitly call the snippet [from within your Custom VCL](https://docs.fastly.com/vcl/vcl-snippets/using-dynamic-vcl-snippets/#including-dynamic-snippets-in-custom-vcl).
* `priority` - Determines where the blocklist VCL is placed in your function relative to other snippets. You may need to change this from the default if your have _other_ snippets you'd like to execute before your blocklist.
* `options.edge_only` - When a service a service is using [shielding](https://docs.fastly.com/en/guides/shielding), the blocklist will only run on edge nodes (where the request is first received) by default. You can change this behavior by setting to `false`.
* `options.var_ip` - The variable `client.ip` used to determine client IP address matches `edge_only = True` by default. If you're running [IP blocklist logic on a shield node](https://docs.fastly.com/en/guides/adding-or-modifying-headers-on-http-requests-and-responses#common-sources-of-new-content) (or use another custom VCL variable to store true client IP), you can change this field to match your needs.


## Lists

```
{
    "lists": [
        {
            "name": "my_block_list",
            "type": "block",
            "action_block": true,
            "action_log": true,
            "action_none": false,
            "match": "exact",
            "variable": null,
            "block_length": 600,
            "items": [
                "10.0.0.0/32"
            ]
        }
    ]
}
```

* `lists` - An array of list objects which make up the bulk of your `fastly-blocklist` configuration.
* `name` - The name you use to refer to the list locally.
* `type` - The type of list this object is. The current options are: `allow`, `geo`, `block`, `temp`, `var`, `combo` and each implements different behavior. See [concepts#lists](concepts.md#lists) for the details of each list type.
* `action_block` - Whether or not the `block` VCL should be called when a request matches this list criteria.
* `action_log` - `Whether or not the `log` VCL should be called when a request matches this list criteria.
* `action_none` - Whether or not matches for this list should product _no action_. This should be set to `true` for lists where you want no action taken (because they're used in a `combo` list later or otherwise).
* `match` - `exact` or `regexp`. This setting is only used for `var` type lists.
* `variable`- The vcl variable you want to compare to items in this list. This setting is only used for `var` type lists.
* `block_length` - Length in seconds for an item in a `temp` type list to persist. This setting is only used for `temp` lists and is implementing by setting an absolute expiration time for the item with `int(time.time()) + block_length`.
* `items` - The array of items which make up the list. The format differs depending on the list type.
