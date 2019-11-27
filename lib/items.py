'''
Manage list items
'''

import urllib.parse

import re
import time
import ipaddress

class Items():
    '''
    Manage list items
    '''

    def __init__(self, args, env):
        '''
        Manage list items
        '''

        self.list = args.list

        if args.removeall:
            print('Removing all item(s) from list(s)')
            self.update = 'remove'
            self._removeall(env)
        if args.clean:
            print('Cleaning temp list(s)')
            self.update = 'remove'
            self._clean(env)
        if args.add:
            print('Adding item(s) to list(s)')
            self.update = 'add'
            self.item = args.item
            self.file = args.file
            self._add(env)
            print('Added item(s) to list(s)')
        if args.remove:
            print('Removing item(s) from list(s)')
            self.update = 'remove'
            self.item = args.item
            self.file = args.file
            self._remove(env)
            print('Removed item(s) from list(s)')

    def _clean(self, env):
        '''
        Clean up expired entries from temp list(s) in the running config
        '''

        current_time = int(time.time())

        # try to cleanup provided list names
        if self.list:
            for name in self.list:
                for config_list in env.config['lists']:

                    # only try to cleanup if this is a temp list.
                    if config_list['name'] == name \
                            and config_list['type'] == 'temp':

                        for item in config_list['items']:
                            for key, value in item.items():
                                # remove items where timestamp < now
                                if value < current_time:
                                    self._update_list(env, {key: value})

                        print(f'\tCleaning temp list: {name}')

        # try to cleanup all lists
        else:
            for config_list in env.config['lists']:

                # only try to cleanup if this is a temp list.
                if config_list['type'] == 'temp':
                    for item in config_list['items']:
                        for key, value in item.items():
                            # remove items where timestamp < now
                            if value < current_time:
                                self.list = [config_list['name']]
                                self._update_list(env, {key: value})

                    print('\tCleaned temp list: {}'.format(
                        config_list['name']))

    def _removeall(self, env):
        '''
        Remove all items from a list or lists
        '''

        # try to remove all items from provided list name
        if self.list:
            for name in self.list:
                for config_list in env.config['lists']:
                    if config_list['name'] == name:
                        config_list['items'] = []
                        print(f'\tRemoved all items from list: {name}')

        # try to remove all items from all lists
        else:
            for config_list in env.config['lists']:
                config_list['items'] = []
                print('\tRemoved all items from list: {}'.format(
                    config_list['name']))

    def _add(self, env):
        '''
        Add an item or items to a list or lists
        '''

        if not self.list:
            exit('Error: no list name(s) defined. Use --list <name>,<name>')

        if not self.item and not self.file:
            exit('Error: --add requires list items. Use --item or --file')

        # try to add item(s) from --item argument
        if self.item:
            for item in self.item:
                self._update_list(env, item)

        # try to add item(s) from --file provided
        if self.file:
            try:
                if env.verbose:
                    print(f'\tReading list items from file: {self.file}')
                with open(self.file) as file_items:
                    items = file_items.read().splitlines()
                if env.verbose:
                    print(f'\tRead items from file.')
            except BaseException:
                exit(f'Error: could not read items from file: {self.file}')

            for item in items:
                self._update_list(env, item)

    def _remove(self, env):
        '''
        Remove an item or items from a list or lists
        '''

        if not self.list:
            exit('Error: no list name(s) defined. Use --list <name>,<name>')

        if not self.item and not self.file:
            exit('Error: --remove requires list items. Use --item or --file')

        # try to add item(s) from --item argument
        if self.item:
            for item in self.item:
                self._update_list(env, item)

        # try to add item(s) from --file provided
        if self.file:
            try:
                if env.verbose:
                    print(f'\tReading list items from file: {self.file}')
                with open(self.file) as file_items:
                    items = file_items.read().splitlines()
                if env.verbose:
                    print(f'\tRead items from file.')
            except BaseException:
                exit(f'Error: could not read items from file: {self.file}')

            for item in items:
                self._update_list(env, item)

    def _update_list(self, env, item):

        lists = [blockly_list['name'] for blockly_list in env.config['lists']]
        for name in self.list:
            # check the the list indicated actually exists
            if name not in lists:
                exit(f'Error: List does not exist. Cannot update: {name}')
            else:
                for blockly_list in env.config['lists']:
                    if blockly_list['name'] == name:

                        # add item to the list
                        if self.update == 'add':

                            # _validate_item validates the item string and
                            # creates the object to be inserted into list
                            valid_item, error = self._validate_item(
                                env, item, name
                            )
                            if error:
                                continue

                            # don't insert duplicates
                            if valid_item in blockly_list['items']:
                                if env.verbose:
                                    print(f'\tWarning: item: {item} already '
                                          f'exists in list: {name}. '
                                          f'Skipping item.'
                                          )
                                continue

                            # finally, add the item to the list
                            try:
                                blockly_list['items'].append(valid_item)
                                if env.verbose:
                                    print(f'\tAdded item: {item} to list: '
                                          f'{name}'
                                          )
                            except BaseException:
                                pass

                        # remove item from the list
                        if self.update == 'remove':

                            # validate item for dictionary type lists
                            if blockly_list['type'] in ['geo', 'temp'] \
                                or (blockly_list['type'] == 'var'
                                        and blockly_list['match'] == 'exact'):

                                # _get_dict_item looks up a dict item by key
                                valid_item, error = self._get_dict_item(
                                    blockly_list, item
                                )
                                if error:
                                    continue

                            # validate item for list type lists
                            else:

                                # _validate_item validates the item string
                                valid_item, error = self._validate_item(
                                    env, item, name
                                )
                                if error:
                                    continue

                            # skip removal if the item doesn't exist
                            if valid_item not in blockly_list['items']:
                                if env.verbose:
                                    print(f'\tWarning: item: {item} does not '
                                          f'exist in list: {name}. Skipping '
                                          f'item.'
                                          )
                                continue

                            # finally, remove the item from the list
                            try:
                                blockly_list['items'].remove(valid_item)
                                if env.verbose:
                                    print(f'\tRemoved item: {item} from '
                                          f'list: {name}'
                                          )
                            except BaseException:
                                pass

    def _validate_item(self, env, item, name):
        '''
        Make sure this item can be inserted into this list
        '''

        # get attributes of the list we're trying to modify
        lists = [blockly_list['name'] for blockly_list in env.config['lists']]
        for blockly_list in env.config['lists']:
            if blockly_list['name'] == name:
                list_name = blockly_list['name']
                list_type = blockly_list['type']
                list_match = blockly_list['match']
                block_length = blockly_list['block_length']

        valid_item = None
        error = False

        try:
            # geo lists require a capitalized ISO-2 country code
            if list_type == 'geo':
                if re.match('^[A-Z]{2}$', item):
                    valid_item = {item: 'fastly-blocklist'}
                else:
                    raise

            # allow and block lists can take a IP or CIDR + ! for negation
            if list_type in ['allow', 'block']:
                if item[:1] == '!':
                    valid_item = '!{}'.format(
                        str(ipaddress.ip_network(item[1:]))
                    )
                else:
                    valid_item = str(ipaddress.ip_network(item))

            # temp lists can take an IP address only
            if list_type == 'temp':
                valid_item = str(ipaddress.ip_address(item))
                # set temp list expiration time: now + block_length
                expiration_time = int(time.time()) + block_length
                valid_item = {valid_item: expiration_time}

            # exact var lists take any string, it will be urlencoded
            if list_type == 'var' and list_match == 'exact':
                encoded_item = urllib.parse.quote(item, safe='')
                valid_item = {encoded_item: 'fastly-blocklist'}

            # regexp var lists can take any string, it will be urlencoded
            if list_type == 'var' and list_match == 'regexp':
                encoded_item = urllib.parse.quote(item, safe='')
                valid_item = encoded_item

            # combo lists can use any list names
            if list_type == 'combo':
                if item in lists and not item == list_name:
                    valid_item = item
                else:
                    raise

        except BaseException:
            if env.verbose:
                print(f'\tWarning: item: {item} is not a valid entry for '
                      f'list: {list_name}. Skipping item.'
                      )
            error = True

        return valid_item, error

    def _get_dict_item(self, config_list, search_key):
        '''
        Get corresponding item for dict type blockly lists
        '''

        error = False

        # return search_key if it is already a dict
        if isinstance(search_key, dict):
            return search_key, error

        # get dict where key matches search_key
        for item in config_list['items']:
            for key, value in item.items():
                if key == search_key:
                    return {key: value}, error

        error = True

        return None, error
