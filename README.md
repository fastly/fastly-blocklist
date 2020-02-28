![](https://github.com/fastly/fastly-blocklist/workflows/prerelease/badge.svg)
![](https://github.com/fastly/fastly-blocklist/workflows/master/badge.svg)

# fastly-blocklist

**Configure request blocking for a Fastly service.**

`fastly-blocklist` is a utility to help you manage request blocking policies for a Fastly service. It works by handling the maintenance of a number of Fastly components on your behalf, like ACLs, Dictionaries, and VCL snippets. The lists and actions you define locally are converted to blocking code when deployed to your service.

Things you can do with `fastly-blocklist`:
* Block access to your service for a list of IP addresses
* Block requests from a specific geolocation / country code
* Restrict access to your admin URLs by IP address
* Prevent certain HTTP methods (like POST) from a list of suspicious IPs (or User-Agents, or ...)
* And several more!

Get started with [**installation/setup here**](#installationsetup), then go on to the [**included tutorial and examples**](docs/).

> **Note:** This application is currently in development.

---

## Installation/Setup

First clone or download this repository, then use one of the installation methods below:
```
git clone https://github.com/fastly/fastly-blocklist/ && cd fastly-blocklist
```

1. [Running in Docker](#running-in-docker)
1. [Local installation - virtual environment (pipenv)](#local-installation---virtual-environment-pipenv)
1. [Local installation with pip](#local-installation-with-pip)

### Running in Docker

You can use the included [`Dockerfile`](Dockerfile) to build and run `fastly-blocklist` in a container. This method can simplify python version & dependency management in many cases and is our recommended "installation" method if you have Docker available. 

Build the `fastly-blocklist` container:
```
docker build . -t fastly-blocklist:latest
```

Run container:
```
$ docker run --rm \
    -v "${HOME}/.fastlyctl_token:/root/.fastlyctl_token:ro" \
    -v "${PWD}/config.blocklist:/fastly-blocklist/config.blocklist" \
    fastly-blocklist:latest --help
```

> **Note:** You'll need to run the `docker build` step again if/when the _script_ in this repository is updated. _Config_ file changes don't require a new docker build.


### Local installation - virtual environment (pipenv)

Install pipenv for your operating system of choice with the [instructions here](https://docs.pipenv.org/en/latest/install/#installing-pipenv).

Create a virtual environment & install dependencies:
```
pipenv install
```

You can then activate the virtual environment & run `fastly-blocklist` like so:
```
$ pipenv shell

(fastly-blocklist) ~$ python fastly-blocklist.py --help
```

### Local installation with pip

`fastly-blocklist` requires python >= 3.6. You can install dependencies with pip & run with your system python 3 like so:

```
pip3 install --user -r requirements.txt
python3 fastly-blocklist --help
```

> **Note:** The command to invoke python3/pip3 may differ slightly on your system.

---

## fastly-blocklist.py

```
$ python fastly-blocklist.py --help

# fastly-blocklist #
Configure request blocking for a Fastly service.

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Enable verbose mode.

ENVIRONMENT:
  Manage blocklist environment

  --init                Create a new fastly-blocklist config.
  --force               Force config initialization, overwriting existing local config file.
  --apikey APIKEY       Location of a file containing Fastly API key/token.
                            Default: Read from ~/.fastlyctl_token
  --config CONFIG       Location of a fastly-blocklist config file.
                            Default: ./config.blocklist
  --service SERVICE     Service(s) to target.
                            This is required on config --init.
                            Default: Read from the selected config file.
                            Example: --service ABCDEF,DEFABC
  --log LOG             VCL to execute when a request is logged/blocked.
                            Default: none
  --block BLOCK         VCL to execute when a request is blocked.
                            Default: error 403 "Forbidden"

STATE:
  Modify live service and local config state

  --sync                Sync live service configuration to the running config.
  --commit              Deploy running config to the live service(s).
  --save                Save running configuration to a fastly-blocklist config file.

LISTS:
  Manage blocklist lists

  -n, --new             Create a new list.
  -d, --delete          Delete an existing list.
  -l LIST, --list LIST  List name(s) to create/update/delete.
                            This is required for all operations on lists & list items.
                            Example: my-block-list
  -t {allow,geo,block,temp,var,combo}, --type {allow,geo,block,temp,var,combo}
                        List type.
                            This is required when creating a new list.
                            allow   - Allow IP addresses. Disables processing for all other lists.
                            geo     - Block geolocations (ISO alpha-2).
                            block   - Block IP addresses permanently.
                            temp    - Block IP addresses temporarily.
                            var     - Block whenever a VCL variable matches an item.
                            combo   - Block whenever any 2+ lists are matched.
  --action {none,log,block}
                        Action to take when the list is matched.
                            none    - No action is taken.
                            log     - Log that a match occurred.
                            block   - Block the request and log that a match occurred.
                            Default: none
  --match {exact,regexp}
                        Match type for var lists.
                            This is required when creating a new var list.
                            exact   - Match only if variable value == list item.
                            regexp  - Match if variable value ~ list item.
                            Default: exact
  --variable VARIABLE, --var VARIABLE
                        VCL variable name to match against for var lists.
                            This is required when creating a new var list.
                            Example: req.http.User-Agent
  --block_length BLOCK_LENGTH, --len BLOCK_LENGTH
                        Block length in seconds for temp lists.
                            Items will be added with expiration time (now + len).
                            Default: 600

ITEMS:
  Manage list items

  -a, --add             Add an item or items to a list.
  -r, --remove          Remove an item or items from a list.
  -i ITEM, --item ITEM  List item(s) to add/remove.
                            --item or --file are required when operating on list items.
                            Example: 1.2.3.4,4.3.2.1
  -f FILE, --file FILE  File containing list items to add/remove.
                            --item or --file are required when operating on list items.
  --clean               Clean up expired entries from temp list(s) in the running config.
  --removeall           Remove all items from a list or all lists in the running config.

```

## Contributing
We welcome pull requests for issues and new functionality. Please see [Contributing](CONTRIBUTING.md) for more details.
