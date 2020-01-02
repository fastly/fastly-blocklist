'''
Test environment creation with lib Environment()
'''

import unittest

import os
import argparse

from lib import Environment


class EnvironmentTests(unittest.TestCase):
    '''
    Test environment creation with Environment()
    '''

    def setUp(self):
        with open('tests.apikey', 'w') as file_apikey:
            file_apikey.write('MYTESTAPIKEY')

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

    def test_init(self):
        '''
        test init of a new config file
        '''

        # create a new environment
        env = Environment(self.args)

        # ensure apikey and config are populated
        self.assertEqual(env.apikey, 'MYTESTAPIKEY')
        self.assertTrue(env.config['services'])
        self.assertFalse(env.config['lists'])
        self.assertEqual(env.config['log'], '')

    def test_init_service_defaults(self):
        '''
        ensure service config defaults are set during init
        '''

        # create a new environment
        env = Environment(self.args)

        # ensure service defaults
        self.assertEqual(env.config['services'][0]['type'], 'recv')
        self.assertEqual(env.config['services'][0]['priority'], '10')
        self.assertEqual(env.config['services'][0]['options']['edge_only'], True)
        self.assertEqual(env.config['services'][0]['options']['var_ip'], 'client.ip')

    def test_init_config_exists(self):
        '''
        test init of a new config file where another exists
        '''

        # create a 'valid' config file
        with open('tests.blocklist', 'w') as file_apikey:
            file_apikey.write('{}')

        # try to create a new config over existing
        self.args.force = False

        with self.assertRaisesRegex(
                SystemExit,
                "config file exists"
                ):
            Environment(self.args)

    def test_init_config_exists_force(self):
        '''
        test init of a new config file where another exists
        and args.force is provided
        '''

        # create a 'valid' config file
        with open('tests.blocklist', 'w') as file_apikey:
            file_apikey.write('{}')

        # force create a new config over existing
        self.args.force = True
        env = Environment(self.args)

        # ensure apikey and config are populated
        self.assertEqual(env.apikey, 'MYTESTAPIKEY')
        self.assertTrue(env.config['services'])
        self.assertFalse(env.config['lists'])
        self.assertEqual(env.config['log'], '')

    def test_load_config(self):
        '''
        test init and load of a config file
        '''

        # create a new config file
        Environment(self.args)

        # load an existing config file
        self.args.init = False
        env = Environment(self.args)

        # ensure apikey and config are populated
        self.assertEqual(env.apikey, 'MYTESTAPIKEY')
        self.assertTrue(env.config['services'])
        self.assertFalse(env.config['lists'])
        self.assertEqual(env.config['log'], '')

    def test_load_config_auto_generate(self):
        '''
        test init of a new config file where args.init is not provided
        '''

        # auto init a config file when one doesn't exist
        self.args.init = False
        env = Environment(self.args)

        # ensure apikey and config are populated
        self.assertEqual(env.apikey, 'MYTESTAPIKEY')
        self.assertTrue(env.config['services'])
        self.assertFalse(env.config['lists'])
        self.assertEqual(env.config['log'], '')

    def test_load_config_override_services(self):
        '''
        test runtime override of args.services
        '''

        # create a new config file
        Environment(self.args)

        # load an existing config file and replace services in running config
        self.args.init = False
        self.args.service = ['SERVICE1', 'SERVICE2']
        env = Environment(self.args)

        # ensure override services are targeted
        self.assertEqual(
            len(env.config['services']),
            2
        )

    def test_save_config(self):
        '''
        test saving a config file
        '''

        # create a new config file
        Environment(self.args)

        # load existing config file, change something, and save
        self.args.init = False
        self.args.service = ['SERVICE1', 'SERVICE2']
        Environment(self.args).save_config()

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
