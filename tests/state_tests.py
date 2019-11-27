'''
Test modifying state with lib State()
'''

import unittest

import os
import argparse

from lib import Environment, State


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

    @unittest.SkipTest
    def test_sync(self):
        '''
        test local portion of sync operations
        '''

    @unittest.SkipTest
    def test_commit(self):
        '''
        test lost portion of commit operations
        '''

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
