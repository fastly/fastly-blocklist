'''
Test modifying state with lib State()
'''

import unittest

import os
import argparse

from lib import Environment, State, Lists, Items


class StateTests(unittest.TestCase):
    '''
    Test modifying state with State()
    '''

    def setUp(self):
        with open('tests.apikey', 'w') as file_apikey:
            file_apikey.write('fastly_token: APIKEY')

        # set up argparse
        self.args = argparse.Namespace(
            init=True,
            apikey='tests.apikey',
            config='tests.blocklist',
            service=['SERVICEID'],
            log='',
            block='',
            force=False,
            verbose=False
        )

    def tearDown(self):
        try:
            os.remove('tests.apikey')
            os.remove('tests.blocklist')
        except BaseException:
            pass

    def test_sync(self):
        '''
        test local portion of sync operations (env.from_remote to env.config)
        '''
        # create a new environment
        env = Environment(self.args)
        env.mock_remote = True
        # create an env.from_remote object
        env.from_remote = {
            'service_id': 'REMOTESERVICEID',
            'version': 1,
            'snippet': {
                'name': 'REMOTE_SNIPPET_NAME',
                'type': 'recv',
                'priority': 10,
                'content': '#fastlyblocklist_list {"name": "my_test_list", '
                           '"type": "block", "action_block": true, '
                           '"action_log": true, "action_none": false, '
                           '"match": "exact", "variable": null, '
                           '"block_length": 600, "items": []}\n'
            },
            'acls': [
                {
                    'name': 'fastlyblocklist_my_test_list',
                    'items': [
                        {
                            'comment': '',
                            'subnet': 32,
                            'service_id': 'REMOTESERVICEID',
                            'negated': '0',
                            'deleted_at': None,
                            'ip': '10.0.0.1'
                        }
                    ]
                }
            ],
            'dicts': []
        }

        # sync env.from_remote to local env.config
        State().sync(env, 'remote')

        # ensure remote made it into our local config
        self.assertEqual(
            env.config['services'][0]['id'],
            'REMOTESERVICEID'
        )
        self.assertEqual(
            env.config['services'][0]['snippet_name'],
            'REMOTE_SNIPPET_NAME'
        )
        self.assertEqual(
            env.config['lists'][0]['name'],
            'my_test_list'
        )
        self.assertEqual(
            env.config['lists'][0]['type'],
            'block'
        )
        self.assertTrue(
            env.config['lists'][0]['action_block']
        )
        self.assertEqual(
            env.config['lists'][0]['items'][0],
            '10.0.0.1/32'
        )

    def test_commit(self):
        '''
        test local portion of commit operations (create env.to_remote)
        '''

        self.args.new = True
        self.args.delete = False
        self.args.list = ['a_new_list']
        self.args.type = 'block'
        self.args.action = 'block'
        self.args.match = 'exact'
        self.args.variable = None
        self.args.block_length = None

        self.args.add = True
        self.args.remove = False
        self.args.clean = False
        self.args.removeall = False
        self.args.item = ['!10.0.0.0/8']
        self.args.file = None

        # create a new environment, populate it with our list and item
        env = Environment(self.args)
        env.mock_remote = True
        Lists(self.args, env)
        Items(self.args, env)

        # commit to 'remote' service
        State().commit(env, 'remote')

        # ensure SERVICEID is copied into env.to_remote
        self.assertEqual(
            env.to_remote['service_id'],
            'SERVICEID'
        )
        # ensure snippet contains config block and logic for our list
        self.assertRegex(
            env.to_remote['snippet']['content'],
            r'\n#fastlyblocklist_list {"name": "a_new_list".*"items": \[\]}\n'
        )
        self.assertRegex(
            env.to_remote['snippet']['content'],
            r'\n\s*if \(var\.ip ~ fastlyblocklist_a_new_list\) {\n'
        )
        # ensure our list is converted to ACL
        self.assertEqual(
            env.to_remote['acls'][0]['name'],
            'fastlyblocklist_a_new_list'
        )
        self.assertEqual(
            env.to_remote['acls'][0]['items'][0]['ip'],
            '10.0.0.0'
        )
        self.assertEqual(
            env.to_remote['acls'][0]['items'][0]['negated'],
            '1'
        )
        self.assertEqual(
            env.to_remote['acls'][0]['items'][0]['subnet'],
            8
        )

    def test_save(self):
        '''
        test create, save, and load of a config file
        '''

        # create a new config file
        Environment(self.args)

        # load existing config file, change something
        self.args.init = False
        self.args.save = True
        self.args.service = ['SERVICE1', 'SERVICE2']
        env = Environment(self.args)

        # save the changes using State().save()
        State().save(env)

        # load the modified config file
        self.args.service = []
        env = Environment(self.args)

        # ensure updated config is loaded
        self.assertEqual(
            len(env.config['services']),
            2
        )


if __name__ == '__main__':
    unittest.main()
