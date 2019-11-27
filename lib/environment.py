'''
Manage fastly-blocklist configuration environment
'''

from pathlib import Path

import random
import string
import json
import yaml

class Environment():
    '''
    Manage fastly-blocklist configuration environment
    '''

    def __init__(self, args):
        '''
        Try to initialize our environment, depending on arguments provided.
        '''

        # Set verbosity.
        self.verbose = args.verbose

        # Create a new config file.
        if args.init:
            print(f'Creating a new config file: {args.config}')
            self._init_config(
                args.force,
                args.config,
                args.service,
                args.log,
                args.block)

        # Read Fastly API key from file.
        try:
            print(f'Reading API key from: {args.apikey}')
            with open(args.apikey) as file_apikey:
                self.apikey = (yaml.safe_load(file_apikey))['fastly_token']
            print(f'\tRead API key.')
        except BaseException:
            exit(f'Error: could not read API key from: {args.apikey}')

        # Read or create a fastly-blocklist config file.
        try:
            print(f'Loading config from file: {args.config}')
            self._load_config(args.config)
        except BaseException:
            print('\tWarning: could not read config file.')
            print('\tCreating a new config file.')
            self._init_config(
                args.force,
                args.config,
                args.service,
                args.log,
                args.block)

        # Override service(s) targeted
        if args.service:
            print(f'Targeting service(s): {args.service}')
            self._set_service(args.service)

    def _init_config(self, force, config_file, service, log, block):
        '''
        Create a new fastly-blocklist config file
        '''

        self.config_file = config_file

        self.config = {
            'log': f'{log}',
            'block': f'{block}',
            'services': [],
            'lists': []
        }

        # Set service(s) for this saved config
        if service:
            self._set_service(service)
        else:
            exit('Error: no service(s) targeted. Use --service <sid>,<sid> '
                 'to set.'
                 )

        # Write a new config file only if one doesn't exist, or if forced
        if not Path(self.config_file).exists():
            with open(self.config_file, 'w') as file_config:
                file_config.write(json.dumps(self.config, indent=4))
        else:
            if force:
                with open(self.config_file, 'w') as file_config:
                    file_config.write(json.dumps(self.config, indent=4))
            else:
                exit('Error: config file exists. Use --force to overwrite.')

        print(f'\tCreated a new config file: {self.config_file}')

    def _load_config(self, config_file):
        '''
        Load a fastly-blocklist configuration from file
        '''

        self.config_file = config_file

        try:
            with open(self.config_file) as file_config:
                config = json.load(file_config)

            self.config = config
        except BaseException:
            quit('Error: could not load config from file: {config_file}')

        print('\tLoaded config from file.')

    def _set_service(self, service):
        '''
        Set service(s) targeted by the config
        '''

        # Print a warning if existing SIDs in config file don't match SIDs
        # supplied
        sids = [service['id'] for service in self.config['services']]
        if sids and list(set(sids) - set(service)):
            print(f'\tWarning: overriding services in config file: '
                  f'{sids} with: {service}'
                  )

        self.config['services'] = []

        snippet_uid = ''.join(random.sample(string.ascii_lowercase, 12))

        for sid in service:
            service = {
                'id': f'{sid}',
                'type': 'recv',
                'snippet_name': f'fastlyblocklist_{snippet_uid}',
                'priority': '10',
                'options': {
                    'shield_only': False
                }
            }
            self.config['services'].append(service)

    def save_config(self):
        '''
        Save a fastly-blocklist configuration to file
        '''

        try:
            with open(self.config_file, 'w') as file_config:
                file_config.write(json.dumps(self.config, indent=4))
        except BaseException:
            exit(f'Error: could not write to file: {self.config_file}')

        print(f'\tSaved config to file: {self.config_file}')
