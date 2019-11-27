'''
Manage remote state
'''

import urllib.parse

import re
import json
import fastly


class Remote():
    '''
    Manage remote state
    '''

    def __init__(self, env):
        '''
        Connect & auth to the Fastly API
        '''
        try:
            self.api = fastly.API(timeout=15)
            self.api.authenticate_by_key(env.apikey)
        except BaseException:
            exit('Error: could not connect & auth to Fastly API')

    def get_remote_config_service(self, env, sid):
        '''
        Get all the fastly-blocklist config from a live service
        All live config is put into env.from_remote dict
        '''

        print(f'\tGetting live config.')

        env.from_remote = {
            'service_id': sid
        }

        try:
            version = self.api.service(
                id=sid
            ).get_active_version_number()
            env.from_remote['version'] = version
        except BaseException:
            exit(f'Error: could not get active version for service: {sid}')

        # get snippet
        env.from_remote['snippet'] = {}
        self._get_snippet(env)

        # get acls
        env.from_remote['acls'] = []
        acls = self.api.conn.request('GET',
                                     f'/service/{sid}'
                                     f'/version/{version}'
                                     f'/acl'
                                     )[1]
        for acl in acls:
            if re.match('^fastlyblocklist_', acl['name']):
                # get the acl's contents
                self._get_acl(env, acl['name'], acl['id'])
        print('\t\tGot fastly-blocklist acls.')

        # get dictionaries
        env.from_remote['dicts'] = []
        dicts = self.api.conn.request('GET',
                                      f'/service/{sid}'
                                      f'/version/{version}'
                                      f'/dictionary'
                                      )[1]
        for remote_dict in dicts:
            if re.match('^fastlyblocklist_', remote_dict['name']):
                # get the acl's contents
                self._get_dict(env, remote_dict['name'], remote_dict['id'])
        print('\t\tGot fastly-blocklist dictionaries.')

    def deploy_list_updates(self, env):
        '''
        Deploy remote list updates to a live service
        All live config is taken from env.to_remote dict
        '''

        print('\t\tDeploying list updates to service.')

        env.flag_new_version = False

        # create/update acls
        to_acls = [to_acl['name'] for to_acl in env.to_remote['acls']]
        from_acls = [from_acl['name'] for from_acl in env.from_remote['acls']]

        for name in to_acls:
            if name in from_acls:
                self._update_acl(env, name)
            else:
                if not env.flag_new_version:
                    env.flag_new_version = True
                    self._new_version(env)
                self._new_acl(env, name)

        # create/update dicts
        to_dicts = [to_dict['name'] for to_dict in env.to_remote['dicts']]
        from_dicts = [from_dict['name']
                      for from_dict in env.from_remote['dicts']]

        for name in to_dicts:
            if name in from_dicts:
                self._update_dict(env, name)
            else:
                if not env.flag_new_version:
                    env.flag_new_version = True
                    self._new_version(env)
                self._new_dict(env, name)

        if env.flag_new_version:
            self._deploy_version(env)
            env.flag_new_version = False

    def deploy_list_deletes(self, env):
        '''
        Delete remote list config from a live service
        All live config is taken from env.to_remote dict
        '''

        print('\t\tDeleting any orphaned lists from service.')

        # delete acls
        to_acls = [to_acl['name'] for to_acl in env.to_remote['acls']]
        from_acls = [from_acl['name'] for from_acl in env.from_remote['acls']]

        for name in from_acls:
            if name not in to_acls:
                if not env.flag_new_version:
                    env.flag_new_version = True
                    self._new_version(env)
                self._delete_acl(env, name)

        # delete dicts
        to_dicts = [to_dict['name'] for to_dict in env.to_remote['dicts']]
        from_dicts = [from_dict['name']
                      for from_dict in env.from_remote['dicts']]

        for name in from_dicts:
            if name not in to_dicts:
                if not env.flag_new_version:
                    env.flag_new_version = True
                    self._new_version(env)
                self._delete_dict(env, name)

    def update_snippet(self, env):
        '''
        Update/deploy remote snippet config to a live service
        All live config is taken from env.to_remote dict
        '''

        # determine if we need to create a new snippet
        if env.to_remote['snippet']['name'] \
                != env.from_remote['snippet']['name'] \
                or env.to_remote['snippet']['type'] \
                != env.from_remote['snippet']['type'] \
                or env.to_remote['snippet']['priority'] \
                != env.from_remote['snippet']['priority']:

            env.flag_new_version = True
            self._new_version(env)
            self._new_snippet(env)

        # determine if we need to update existing snippet
        elif env.to_remote['snippet']['content'] \
                != env.from_remote['snippet']['content']:

            self._update_snippet(env)

        # no snippet changes required
        else:
            print('\t\tNo changes to fastly-blocklist snippet.')

    def deploy_snippet_updates(self, env):
        '''
        Delete remote snippet & list deletes to a live service
        '''

        # cleanup any loose fastly-blocklist snippets
        name_from_remote = env.from_remote['snippet']['name']
        if env.to_remote['snippet']['name'] != name_from_remote:
            self._delete_snippet(env, name_from_remote)

        if env.flag_new_version:
            self._deploy_version(env)

    def _new_version(self, env):
        '''
        Clone the active service version and create a new one
        '''

        sid = env.to_remote['service_id']

        try:
            version = self.api.service(
                id=sid
            ).get_active_version_number()
            env.to_remote['version'] = version
            version_old = version
        except BaseException:
            exit(f'Error: could not get active version for service: {sid}')

        try:
            response = self.api.version(
                service_id=sid,
                version=version
            ).clone()
            version_new = response['number']
            env.to_remote['version'] = version_new
        except BaseException:
            exit(f'Error: could not clone active version: {version_old} '
                 f'for service: {sid}'
                 f'Response: {response}'
                 )

        print(f'\t\tCreated new version: {version_new} from active version: '
              f'{version_old} for service: {sid}'
              )

    def _deploy_version(self, env):
        '''
        Make the service version active
        '''

        sid = env.to_remote['service_id']
        version = env.to_remote['version']

        try:
            response = self.api.version(
                service_id=sid,
                version=version
            ).activate()
        except BaseException:
            exit(f'Error: could not activate version: {version} for '
                 f'service: {sid}.'
                 f'Response: {response}'
                 )

        print(f'\tDeployed version: {version} for service: {sid}')

    def _new_snippet(self, env):
        '''
        Create a new VCL snippet in this service + version
        '''

        sid = env.to_remote['service_id']
        version = env.to_remote['version']
        snippet = env.to_remote['snippet']
        snippet_name = snippet['name']

        self._delete_snippet(env, snippet_name)

        body = urllib.parse.urlencode(snippet)
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        try:
            self.api.conn.request('POST',
                                  f'/service/{sid}'
                                  f'/version/{version}'
                                  f'/snippet',
                                  body=body,
                                  headers=headers
                                 )

            print(f'\t\tAdded new snippet name: {snippet_name}')

        except BaseException:
            exit(f'Error: could not add snippet name: {snippet_name} to '
                 f'service: {sid} version: {version}'
                 )

    def _get_snippet(self, env):
        '''
        Get an existing VCL snippet
        '''

        re_snippet_name = '^fastlyblocklist_'

        sid = env.from_remote['service_id']
        version = env.from_remote['version']

        snippet_id = None
        env.from_remote['snippet']['content'] = ''
        env.from_remote['snippet']['name'] = ''
        env.from_remote['snippet']['id'] = ''
        env.from_remote['snippet']['priority'] = '1'

        try:
            snippets = self.api.conn.request('GET',
                                             f'/service/{sid}'
                                             f'/version/{version}'
                                             f'/snippet'
                                             )[1]

            for snippet in snippets:
                if re.match(re_snippet_name, snippet['name']) \
                        and snippet['dynamic'] == '1':
                    snippet_id = snippet['id']
                    snippet_name = snippet['name']
                    env.from_remote['snippet'] = snippet

            if not snippet_id:
                print(f'\t\tCouldn\'t find dynamic vcl snippet matching '
                      f'/{re_snippet_name}/'
                      )
                raise

            # get the snippet's contents and put in env.from_remote
            snippet_content = self.api.conn.request('GET',
                                                    f'/service/{sid}'
                                                    f'/snippet/{snippet_id}'
                                                    )[1]

            env.from_remote['snippet']['content'] = snippet_content['content']

            if env.verbose:
                print(f'\t\tGot fastly-blocklist vcl snippet name: {snippet_name}')

        except BaseException:
            print(f'\t\tWarning: Couldn\'t get fastly-blocklist snippet for service: '
                  f'{sid} snippet id: {snippet_id}'
                  )

    def _update_snippet(self, env):
        '''
        Update the VCL snippet in existing service + version
        '''

        sid = env.to_remote['service_id']
        snippet_id = env.from_remote['snippet']['id']
        snippet = env.to_remote['snippet']
        snippet_name = snippet['name']

        body = urllib.parse.urlencode(snippet)
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        try:
            self.api.conn.request('PUT',
                                  f'/service/{sid}'
                                  f'/snippet/{snippet_id}',
                                  body=body,
                                  headers=headers
                                  )

            print(f'\t\tUpdated snippet name: {snippet_name}')

        except BaseException:
            exit(f'Error: could not update snippet name: {snippet_name} in '
                 f'service: {sid}'
                 )

    def _delete_snippet(self, env, name):
        '''
        Delete an existing VCL snippet
        '''

        sid = env.to_remote['service_id']
        version = env.to_remote['version']

        try:
            self.api.conn.request('DELETE',
                                  f'/service/{sid}'
                                  f'/version/{version}'
                                  f'/snippet/{name}'
                                  )[1]

            print(f'\t\tDeleted fastly-blocklist vcl snippet name: {name}')

        except BaseException:
            print(f'\t\tWarning: Couldn\'t delete snippet for service: '
                  f'{sid} snippet name: {name}'
                  )

    def _new_acl(self, env, name):
        '''
        Create a new ACL in this service + version
        '''

        sid = env.to_remote['service_id']
        version = env.to_remote['version']

        self._delete_acl(env, name)

        body = f'name={name}'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        try:
            response = self.api.conn.request('POST',
                                             f'/service/{sid}'
                                             f'/version/{version}'
                                             f'/acl',
                                             body=body,
                                             headers=headers
                                             )
        except BaseException:
            exit(f'Error: could not add acl name: {name} to '
                 f'service: {sid} version: {version}.'
                 f'Response : {response}'
                 )

        print(f'\t\tAdded new acl: {name}')

        self._update_acl(env, name)

    def _get_acl(self, env, name, acl_id):
        '''
        Get existing ACL
        '''

        sid = env.from_remote['service_id']

        try:
            acl_remote = self.api.conn.request('GET',
                                               f'/service/{sid}'
                                               f'/acl/{acl_id}'
                                               f'/entries'
                                               )[1]
            env.from_remote['acls'].append(
                {
                    'name': name,
                    'items': acl_remote
                }
            )

        except BaseException:
            exit(f'Error: Couldn\'t get acl for service: '
                 f'{sid} acl name: {name}'
                 )

        if env.verbose:
            print(f'\t\tGot fastly-blocklist acl name: {name}')

    def _update_acl(self, env, name):
        '''
        Update an existing ACL
        '''

        sid = env.to_remote['service_id']
        version = env.to_remote['version']
        to_acl = []
        from_acl = []
        entries = []


        # get items for comparison
        for acl in env.from_remote['acls']:
            if acl['name'] == name:
                from_acl = acl['items']
        for acl in env.to_remote['acls']:
            if acl['name'] == name:
                to_acl = acl['items']

        # find items to remove
        for from_item in from_acl:
            flag_found = False
            for to_item in to_acl:
                if from_item['ip'] == to_item['ip'] \
                        and from_item['negated'] == to_item['negated'] \
                        and from_item['subnet'] == to_item['subnet']:
                    flag_found = True

            if not flag_found:
                entries.append({
                    'op': 'delete',
                    'id': from_item['id']
                })

        # find items to create
        for to_item in to_acl:
            flag_found = False
            for from_item in from_acl:
                if from_item['ip'] == to_item['ip'] \
                        and from_item['negated'] == to_item['negated'] \
                        and from_item['subnet'] == to_item['subnet']:
                    flag_found = True

            if not flag_found:
                entries.append({
                    'op': 'create',
                    'ip': to_item['ip'],
                    'negated': to_item['negated'],
                    'subnet': to_item['subnet']
                })

        if not entries:
            if env.verbose:
                print(f'\t\tNo items to update in acl name: {name}')
            return

        print(f'\t\tUpdating acl name: {name}')

        try:
            for chunk in self._chunk_list(entries):
                response = self.api.conn.request('GET',
                                                 f'/service/{sid}'
                                                 f'/version/{version}'
                                                 f'/acl/{name}'
                                                 )[1]

                acl_id = response['id']
                body = json.dumps({'entries': chunk})
                headers = {
                    'Content-Type': 'application/json'
                }

                response = self.api.conn.request('PATCH',
                                                 f'/service/{sid}'
                                                 f'/acl/{acl_id}'
                                                 f'/entries',
                                                 body=body,
                                                 headers=headers
                                                 )[1]
        except BaseException:
            exit(f'Error: Couldn\'t update acl for service: '
                 f'{sid} acl name: {name} '
                 f'Response: {response}'
                 )

        print(f'\t\tUpdated acl name: {name}')

    def _delete_acl(self, env, name):
        '''
        Delete an existing ACL
        '''

        sid = env.to_remote['service_id']
        version = env.to_remote['version']

        try:
            self.api.conn.request('DELETE',
                                  f'/service/{sid}'
                                  f'/version/{version}'
                                  f'/acl/{name}'
                                  )[1]

            print(f'\t\tDeleted fastly-blocklist acl name: {name}')

        except BaseException:
            print(f'\t\tWarning: Couldn\'t delete acl for service: '
                  f'{sid} acl name: {name}'
                  )

    def _new_dict(self, env, name):
        '''
        Create a new Edge Dictionary in this service + version
        '''

        sid = env.to_remote['service_id']
        version = env.to_remote['version']

        self._delete_dict(env, name)

        body = f'name={name}'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        try:
            response = self.api.conn.request('POST',
                                             f'/service/{sid}'
                                             f'/version/{version}'
                                             f'/dictionary',
                                             body=body,
                                             headers=headers
                                             )[1]
        except BaseException:
            exit(f'Error: could not add dict name: {name} to '
                 f'service: {sid} version: {version}. '
                 f'Response : {response}'
                 )

        print(f'\t\tAdded new dict: {name}')

        self._update_dict(env, name)

    def _get_dict(self, env, name, dict_id):
        '''
        Get existing Edge Dictionary
        '''

        sid = env.from_remote['service_id']

        try:
            dict_remote = self.api.conn.request('GET',
                                                f'/service/{sid}'
                                                f'/dictionary/{dict_id}'
                                                f'/items'
                                                )[1]
            env.from_remote['dicts'].append(
                {
                    'name': name,
                    'items': dict_remote
                }
            )

        except BaseException:
            exit(f'Error: Couldn\'t get dict for service: '
                 f'{sid} dict name: {name}'
                 )

        if env.verbose:
            print(f'\t\tGot fastly-blocklist dict name: {name}')

    def _update_dict(self, env, name):
        '''
        Update an existing Edge Dictionary
        '''

        sid = env.to_remote['service_id']
        version = env.to_remote['version']
        to_dict = []
        from_dict = []
        entries = []

        # get items for comparison
        for remote_dict in env.from_remote['dicts']:
            if remote_dict['name'] == name:
                from_dict = remote_dict['items']
        for local_dict in env.to_remote['dicts']:
            if local_dict['name'] == name:
                to_dict = local_dict['items']

        # find items to remove
        for from_item in from_dict:
            flag_found = False
            for to_item in to_dict:
                if from_item['item_key'] == to_item['item_key'] \
                        and from_item['item_value'] == to_item['item_value']:
                    flag_found = True

            if not flag_found:
                entries.append({
                    'op': 'delete',
                    'item_key': from_item['item_key']
                })

        # find items to create
        for to_item in to_dict:
            flag_found = False
            for from_item in from_dict:
                if from_item['item_key'] == to_item['item_key'] \
                        and from_item['item_value'] == to_item['item_value']:
                    flag_found = True

            if not flag_found:
                entries.append({
                    'op': 'create',
                    'item_key': to_item['item_key'],
                    'item_value': to_item['item_value']
                })

        if not entries:
            if env.verbose:
                print(f'\t\tNo items to update in dict name: {name}')
            return

        print(f'\t\tUpdating dict name: {name}')

        try:
            for chunk in self._chunk_list(entries):
                response = self.api.conn.request('GET',
                                                 f'/service/{sid}'
                                                 f'/version/{version}'
                                                 f'/dictionary/{name}'
                                                 )[1]

                dict_id = response['id']
                body = json.dumps({'items': chunk})
                headers = {
                    'Content-Type': 'application/json'
                }

                response = self.api.conn.request('PATCH',
                                                 f'/service/{sid}'
                                                 f'/dictionary/{dict_id}'
                                                 f'/items',
                                                 body=body,
                                                 headers=headers
                                                 )[1]
        except BaseException:
            exit(f'Error: Couldn\'t update dict for service: '
                 f'{sid} dict name: {name} '
                 f'Response: {response}'
                 )

        print(f'\t\tUpdated dict name: {name}')

    def _delete_dict(self, env, name):
        '''
        Delete an existing Edge Dictionary
        '''

        sid = env.to_remote['service_id']
        version = env.to_remote['version']

        try:
            self.api.conn.request('DELETE',
                                  f'/service/{sid}'
                                  f'/version/{version}'
                                  f'/dictionary/{name}'
                                  )[1]

            print(f'\t\tDeleted fastly-blocklist dict name: {name}')

        except BaseException:
            print(f'\t\tWarning: Couldn\'t delete dict for service: '
                  f'{sid} dict name: {name}'
                  )

    def _chunk_list(self, full_list):
        '''
        Chunk list before sending update
        '''

        chunk_size = 250

        for item in range(0, len(full_list), chunk_size):
            yield full_list[item:item + chunk_size]
