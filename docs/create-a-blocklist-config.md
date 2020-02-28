# fastly-blocklist/docs/create-a-blocklist-config

Objectives:
1. Create a new fastly-blocklist configuration 
1. Add a new list to your config

## Obtain a Fastly API token

You'll need an [API token](https://docs.fastly.com/en/guides/using-api-tokens) from a user with at least [`Engineer` permissions](https://docs.fastly.com/en/guides/configuring-user-roles-and-permissions) to your Fastly account.

1. Create a new token on the [API Token Management page](https://manage.fastly.com/account/personal/tokens)
1. Save the token on your local machine in the file: `~/.fastlyctl_token`
    1. The file should only contain one thing: your `YOURFASTLYAPITOKEN`.

## Determine which Fastly Service you'll be targeting

1. Browse to your [Fastly management console](https://manage.fastly.com/services/all) and select a service or create a new one.
1. Select a service, click 'Show service ID', and copy the service id.

## Create a new fastly-blocklist configuration

To begin, we'll initialize a new config file `config.blocklist` targeting your service id.

`python fastly-blocklist.py --init --service SERVICEID --save`

```
$ python fastly-blocklist.py --init --service SERVICEID --save

# fastly-blocklist #
Configure request blocking for a Fastly service.

Creating a new config file: /home/user/fastly-blocklist/config.blocklist
        Created a new config file: /home/user/fastly-blocklist/config.blocklist
Reading API key from: /home/user/.fastlyctl_token
        Read API key.
Loading config from file: /home/user/fastly-blocklist/config.blocklist
        Loaded config from file.
Targeting service(s): ['SERVICEID']
Saving running config to file: /home/user/fastly-blocklist/config.blocklist
        Saved config to file: /home/user/fastly-blocklist/config.blocklist
```

You can change the default filename and location with `--config path/to/your-config.blocklist`.

Take a look in the `config.blocklist` file generated. You should see your service ID and some additional boilerplate config.

```
$ cat config.blocklist
{
    "log": "",
    "block": "error 403 \"Forbidden\";",
    "services": [
        {
            "id": "SERVICEID",
            "type": "recv",
            "snippet_name": "fastlyblocklist_RANDOMSTRING",
            "priority": "10",
            "options": {
                "edge_only": true,
                "var_ip": "client.ip"
            }
        }
    ],
    "lists": []
}
```

## Create a new list

Next, create a new list container. For this tutorial we're creating a `block` list with action `block`.

`python fastly-blocklist.py --new --list my_block_list --type block --action block --save`

```
$ python fastly-blocklist.py --new --list my_block_list --type block --action block --save

# fastly-blocklist #
Configure request blocking for a Fastly service.

Reading API key from: /home/user/.fastlyctl_token
        Read API key.
Loading config from file: /home/user/fastly-blocklist/config.blocklist
        Loaded config from file.
Creating new list.
        Creating list: my_block_list
        Created list.
Saving running config to file: /home/user/fastly-blocklist/config.blocklist
        Saved config to file: /home/user/fastly-blocklist/config.blocklist
```

## Add an IP address to the block list

First, determine which IP address you're going to block from accessing your service. I'm using my current public IP address: https://www.google.com/search?q=my+ip+address

Then, add the IP address to the list `my_block_list` you just created.

`python fastly-blocklist.py --add --list my_block_list --item MYPUBLICIP --save --verbose`

```
$ python fastly-blocklist.py --add --list my_block_list --item MYPUBLICIP --save --verbose

# fastly-blocklist #
Configure request blocking for a Fastly service.

Reading API key from: /home/user/.fastlyctl_token
        Read API key.
Loading config from file: /home/user/fastly-blocklist/config.blocklist
        Loaded config from file.
Adding item(s) to list(s)
        Added item: MYPUBLICIP to list: my_block_list
Added item(s) to list(s)
Saving running config to file: /home/user/fastly-blocklist/config.blocklist
        Saved config to file: /home/user/fastly-blocklist/config.blocklist
```

## Next Steps
You now have a fastly-blocklist configuration file ready to be deployed. Go on to the [next tutorial here](deploy-blocklist-to-service.md).
