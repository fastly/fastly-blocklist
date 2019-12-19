'''
Manage blockly local and remote state
'''

import re
import json

import urllib.parse

from jinja2 import Environment, FileSystemLoader


class State():
    '''
    Manage blockly local and remote state
    '''

    def __init__(self):
        '''
        do nothing
        '''

    def sync(self, env, remote):
        '''
        Sync live service to the running config
        '''

        sync_sid = env.config['services'][0]['id']
        if len(env.config['services']) > 1:
            print(f'\tWarning: more then one service is configured. Syncing '
                  f'from first service available.'
                  )
        print(f'\tSyncing with service: {sync_sid}')

        remote.get_remote_config_service(env, sync_sid)
        self._convert_remote_to_local(env)

        print(f'\tService: {sync_sid} synced to running config.')

    def commit(self, env, remote):
        '''
        Deploy running configuration to the live service(s)
        '''

        commit_sids = [service['id'] for service in env.config['services']]
        print(f'\tConfig will be deployed to service(s): {commit_sids}')

        for service in env.config['services']:
            commit_sid = service['id']
            print(f'\tDeploying config to service: {commit_sid}')

            self._convert_local_to_remote(env, commit_sid)
            remote.get_remote_config_service(env, commit_sid)

            env.to_remote['version'] = env.from_remote['version']

            print('\tDeploying config to service.')
            remote.deploy_list_updates(env)
            remote.update_snippet(env)
            remote.deploy_list_deletes(env)
            remote.deploy_snippet_updates(env)

        print(f'\tDeployed config to services.')

    def save(self, env):
        '''
        Save running configuration to a blockly config file
        '''

        env.save_config()

    def _convert_remote_to_local(self, env):
        '''
        convert & copy env.from_remote to env.config
        '''

        print(f'\tConverting remote config to local.')

        # clear out our running config
        env.config['log'] = None
        env.config['services'] = []
        env.config['lists'] = []

        # convert service
        service = {
            'id': env.from_remote['service_id'],
            'snippet_name': env.from_remote['snippet']['name'],
            'type': env.from_remote['snippet']['type'],
            'priority': str(env.from_remote['snippet']['priority']),
            'options': {
                'edge_only': True,
                'var_ip': 'client.ip'
            }
        }
        env.config['services'].append(service)

        # convert snippet
        for blockly_raw in env.from_remote['snippet']['content'].splitlines():

            # parse out #fastlyblocklist_log line
            snippet_log = re.match(
                '^#fastlyblocklist_log (.*)',
                blockly_raw
            )
            if snippet_log:
                env.config['log'] = snippet_log.group(1)
                if env.verbose:
                    print(f'\t\tAdded log line from vcl snippet.')

            # parse out #fastlyblocklist_block line
            snippet_log = re.match(
                '^#fastlyblocklist_block (.*)',
                blockly_raw
            )
            if snippet_log:
                env.config['block'] = snippet_log.group(1)
                if env.verbose:
                    print(f'\t\tAdded block line from vcl snippet.')

            # parse out #fastlyblocklist_list lines
            snippet_list = None
            list_json = re.match(
                '^#fastlyblocklist_list (.*)',
                blockly_raw
            )
            if list_json:
                try:
                    snippet_list = json.loads(list_json.group(1))
                except BaseException:
                    print(f'\t\tWarning: could not load fastlyblocklist_list from '
                          f'snippet: {list_json}. Skipping list.'
                          )
            if snippet_list:
                env.config['lists'].append(snippet_list)
                list_name = snippet_list['name']
                if env.verbose:
                    print(f'\t\tAdded list "{list_name}" from vcl snippet.')

        lists = [blockly_list['name'] for blockly_list in env.config['lists']]

        # convert acls
        for remote_acl in env.from_remote['acls']:

            remote_name = remote_acl['name']
            match_name = re.match(
                '^fastlyblocklist_(.+)',
                remote_name
            )

            if match_name:
                list_name = match_name.group(1)
            else:
                print(f'\t\tWarning: ACL "{remote_name}" does not contain '
                      f'a valid name. Skipping list.'
                      )
                continue

            if list_name not in lists:
                print(f'\t\tWarning: ACL "{remote_name}" is not present in '
                      f'vcl snippet. Skipping list.'
                      )
                continue

            for blockly_list in env.config['lists']:
                if blockly_list['name'] == list_name:
                    for item in remote_acl['items']:
                        blockly_item = item['ip']

                        if item['negated'] == '1':
                            blockly_item = '!{}'.format(blockly_item)
                        if item['subnet']:
                            blockly_item = '{}/{}'.format(
                                blockly_item,
                                item['subnet']
                            )
                        else:
                            blockly_item = '{}/{}'.format(
                                blockly_item,
                                '32'
                            )

                        blockly_list['items'].append(blockly_item)

                    if env.verbose:
                        print(f'\t\tAdded items to list "{list_name}" from '
                              f'remote acl name: {remote_name}'
                              )

        # convert dictionaries
        for remote_dict in env.from_remote['dicts']:

            remote_name = remote_dict['name']
            match_name = re.match(
                '^fastlyblocklist_(.+)',
                remote_name
            )

            if match_name:
                list_name = match_name.group(1)
            else:
                print(f'\t\tWarning: dictionary "{remote_name}" does not '
                      f'contain a valid name. Skipping list.'
                      )
                continue

            if list_name not in lists:
                print(f'\t\tWarning: dictionary "{remote_name}" is not '
                      f'present in vcl snippet. Skipping list.'
                      )
                continue

            for blockly_list in env.config['lists']:
                if blockly_list['name'] == list_name:
                    for item in remote_dict['items']:
                        blockly_item = {
                            str(item['item_key']): str(item['item_value'])
                        }

                        blockly_list['items'].append(blockly_item)

                    if env.verbose:
                        print(f'\t\tAdded items to list "{list_name}" from '
                              f'remote dict name: {remote_name}'
                              )

    def _convert_local_to_remote(self, env, sid):
        '''
        convert & copy env.config to env.to_remote
        '''

        print(f'\tConverting local config to remote.')

        list_prefix = 'fastlyblocklist_'

        log_line = env.config['log']
        block_line = env.config['block']

        env.to_remote = {
            'service_id': sid,
            'acls': [],
            'dicts': [],
            'snippet': {
                'dynamic': '1'
            },
            'options': {}
        }

        # convert acls
        for blockly_list in env.config['lists']:
            if blockly_list['type'] in ['allow', 'block']:

                list_name = blockly_list['name']
                acl_name = f'{list_prefix}{list_name}'

                remote_acl = {
                    'items': [],
                    'name': acl_name
                }

                for item in blockly_list['items']:

                    remote_item = {}
                    remote_match = re.match(r'(!)?([0-9\.]+)/?([0-9]*)', item)

                    remote_item['ip'] = remote_match.group(2)

                    if remote_match.group(1):
                        remote_item['negated'] = '1'
                    else:
                        remote_item['negated'] = '0'
                    if remote_match.group(3):
                        remote_item['subnet'] = int(remote_match.group(3))

                    remote_acl['items'].append(remote_item)

                env.to_remote['acls'].append(remote_acl)

                if env.verbose:
                    print(f'\t\tAdded items to acl "{acl_name}" from local '
                          f'list name: {list_name}'
                          )

        # convert dicts
        for blockly_list in env.config['lists']:
            if blockly_list['type'] in ['geo', 'temp'] \
                or (blockly_list['type'] == 'var'
                        and blockly_list['match'] == 'exact'
                   ):

                list_name = blockly_list['name']
                dict_name = f'{list_prefix}{list_name}'

                remote_dict = {
                    'items': [],
                    'name': dict_name
                }

                for item in blockly_list['items']:
                    for key, value in item.items():
                        remote_item = {
                            'item_key': str(key),
                            'item_value': str(value)
                        }
                        remote_dict['items'].append(remote_item)

                env.to_remote['dicts'].append(remote_dict)

                if env.verbose:
                    print(f'\t\tAdded items to dict "{dict_name}" from local '
                          f'list name: {list_name}'
                          )

        # generate vcl
        for service in env.config['services']:
            if service['id'] == sid:
                env.to_remote['snippet']['name'] = service['snippet_name']
                env.to_remote['snippet']['type'] = service['type']
                env.to_remote['snippet']['priority'] = str(service['priority'])
                edge_only = service['options']['edge_only']
                var_ip = service['options']['var_ip']

        # add vars for 'var' lists
        custom_vars = []
        for blockly_list in env.config['lists']:
            if blockly_list['type'] == 'var':
                custom_vars.append({
                    'name': blockly_list['name'],
                    'value': urllib.parse.quote(
                        blockly_list['variable'], safe=''
                    )
                })

        # generate blockly content from lists
        lists = {
            'config_block': [],
            'allow': [],
            'geo': [],
            'block': [],
            'temp': [],
            'var_exact': [],
            'combo': [],
            'var_regexp': []
        }
        for blockly_list in env.config['lists']:

            if blockly_list['type'] in ['allow', 'block', 'geo', 'temp'] \
                    or (blockly_list['type'] == 'var'
                            and blockly_list['match'] == 'exact'
                       ):
                blockly_list['items'] = []

            list_json = json.dumps(blockly_list)
            lists['config_block'].append(list_json)

            # add 'allow' list(s)
            name = blockly_list['name']
            if blockly_list['type'] == 'allow':
                lists['allow'].append({
                    'name': f'{list_prefix}{name}'
                })

            # add 'block' list(s)
            if blockly_list['type'] == 'block':
                lists['block'].append({
                    'name': f'{list_prefix}{name}',
                    'log': blockly_list['action_log'],
                    'block': blockly_list['action_block'],
                    'none': blockly_list['action_none']
                })

            # add 'geo' list(s)
            if blockly_list['type'] == 'geo':
                lists['geo'].append({
                    'name': f'{list_prefix}{name}',
                    'log': blockly_list['action_log'],
                    'block': blockly_list['action_block'],
                    'none': blockly_list['action_none']
                })

            # add 'temp' list(s)
            if blockly_list['type'] == 'temp':
                lists['temp'].append({
                    'name': f'{list_prefix}{name}',
                    'log': blockly_list['action_log'],
                    'block': blockly_list['action_block'],
                    'none': blockly_list['action_none']
                })

            # add exact 'var' list(s)
            if blockly_list['type'] == 'var' \
                    and blockly_list['match'] == 'exact':
                lists['var_exact'].append({
                    'name': f'{list_prefix}{name}',
                    'variable': f'var.custom_{name}',
                    'log': blockly_list['action_log'],
                    'block': blockly_list['action_block'],
                    'none': blockly_list['action_none']
                })

            # add 'combo' list(s)
            combo_list = {
                'children': []
            }
            if blockly_list['type'] == 'combo':
                for item in blockly_list['items']:
                    for child_list in env.config['lists']:
                        child_name = child_list['name']
                        if item == child_name:
                            combo_list['children'].append({
                                'name': f'{list_prefix}{child_name}',
                                'name_short': f'{child_name}',
                                'type': child_list['type'],
                                'match': child_list['match'],
                                'variable': f'var.custom_{child_name}',
                                'strings': child_list['items']
                            })
                combo_list['name'] = name
                combo_list['log'] = blockly_list['action_log']
                combo_list['block'] = blockly_list['action_block']
                combo_list['none'] = blockly_list['action_none']
                lists['combo'].append(combo_list)

            # add regexp 'var' list(s)
            if blockly_list['type'] == 'var' \
                    and blockly_list['match'] == 'regexp':
                lists['var_regexp'].append({
                    'name': f'{name}',
                    'strings': blockly_list['items'],
                    'log': blockly_list['action_log'],
                    'block': blockly_list['action_block'],
                    'none': blockly_list['action_none']
                })

        jinja_env = Environment(
            loader=FileSystemLoader('lib/templates/'),
            extensions=['jinja2.ext.do'],
            trim_blocks=True,
            lstrip_blocks=True
        )

        vcl = jinja_env.get_template('fastly-blocklist_vcl.jinja')

        env.to_remote['snippet']['content'] = vcl.render(
            name=env.to_remote['snippet']['name'],
            log_line=env.config['log'],
            block_line=env.config['block'],
            lists=lists,
            custom_vars=custom_vars,
            edge_only=edge_only,
            var_ip=var_ip
        )
