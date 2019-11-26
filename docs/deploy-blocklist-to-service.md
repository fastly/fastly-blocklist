# fastly-blocklist/docs/deploy-blocklist-to-service

Objectives:
1. Deploy your configuration to a live service

## Deploy fastly-blocklist to your service

Deploying fastly-blocklist is as simple as issuing a `--commit`. The local configuration file you created earlier is read, your service checked, then config deployed to the live service.

> Since this is your first deploy, we'll need to create a new version of to service. This process is handled automatically by fastly-blocklist.

`python fastly-blocklist.py --commit --save`

```
$ python fastly-blocklist.py --commit --save

# fastly-blocklist #
Configure request blocking for a Fastly service.

Reading API key from: /home/user/.fastly
        Read API key.
Loading config from file: /home/user/fastly-blocklist/config.blocklist
        Loaded config from file.
Deploying to live service(s).
        Config will be deployed to service(s): ['SERVICEID']
        Deploying config to service: SERVICEID
        Converting local config to remote.
                Added items to acl "fastlyblocklist_my_block_list" from local list name: my_block_list
        Getting live config.
                Couldn't find dynamic vcl snippet matching /^fastly-blocklist_/
                Warning: Couldn't get fastly-blocklist snippet for service: SERVICEID snippet id: None
                Got fastly-blocklist acls.
                Got fastly-blocklist dictionaries.
        Deploying snippet config to service.
        Deploying config to service: SERVICEID
                Created new version: 2 from active version: 1 for service: SERVICEID
                Warning: Couldn't delete snippet for service: SERVICEID snippet name: fastlyblocklist_SERVICEID
                Added new snippet name: fastlyblocklist_SERVICEID
        Deploying list config to service.
                Warning: Couldn't delete acl for service: ACLID acl name: fastlyblocklist_my_block_list
                Added new acl: fastlyblocklist_my_block_list
        Deployed version: 2 for service: SERVICEID
        Deployed config to services.
Saving running config to file: /home/user/fastly-blocklist/config.blocklist
        Saved config to file: /home/user/fastly-blocklist/config.blocklist
```

## Test your service

1. Try sending a request for your service from the IP address you blocked. You should recieve a HTTP 403 block.
1. You can also check the new service version we activated. You should see a new "VCL snippet" and "Access control list" added to enforce the block.

## Next Steps
This is the end of the basic fastly-blocklist tutorial. Try adding more list types to your service, or take a look at some of the [examples here](README.md#Examples).
