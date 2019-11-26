'''
Test managing list items with lib.Items()
'''

import unittest

import os
import argparse
import time

import lib


class ItemTests(unittest.TestCase):
    '''
    Test managing list items with lib.Items()
    '''

    def setUp(self):
        with open('tests.apikey', 'w') as file_apikey:
            file_apikey.write('fastly_token: APIKEY')

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
            os.remove('tests.items')
        except BaseException:
            pass

    def test_add_item_bad(self):
        '''
        try to add an item where no args.item or args.file provided
        '''

        self.args.new = True
        self.args.delete = False
        self.args.list = ['a_new_list']
        self.args.type = 'var'
        self.args.action = 'block'
        self.args.match = 'exact'
        self.args.variable = 'var.whatever'
        self.args.block_length = None

        self.args.add = True
        self.args.remove = False
        self.args.clean = False
        self.args.removeall = False
        self.args.item = []
        self.args.file = None

        # create a new config file
        env = lib.Environment(self.args)
        lib.Lists(self.args, env)

        with self.assertRaisesRegex(
                SystemExit,
                "add requires list items"
            ):
            lib.Items(self.args, env)

    def test_add_geo(self):
        '''
        try to add a valid new item to geo list
        '''

        self.args.new = True
        self.args.delete = False
        self.args.list = ['a_new_list']
        self.args.type = 'geo'
        self.args.action = 'block'
        self.args.match = 'exact'
        self.args.variable = None
        self.args.block_length = None

        self.args.add = True
        self.args.remove = False
        self.args.clean = False
        self.args.removeall = False
        self.args.item = ['US']
        self.args.file = None

        # create a new config file
        env = lib.Environment(self.args)
        lib.Lists(self.args, env)
        lib.Items(self.args, env)

        self.assertEqual(
            env.config['lists'][0]['items'][0]['US'],
            'fastly-blocklist'
        )

    def test_add_geo_file(self):
        '''
        try to add a valid new item to geo list from args.file
        '''

        with open('tests.items', 'w') as file_items:
            file_items.writelines(['US', '\n', 'RU'])

        self.args.new = True
        self.args.delete = False
        self.args.list = ['a_new_list']
        self.args.type = 'geo'
        self.args.action = 'block'
        self.args.match = 'exact'
        self.args.variable = None
        self.args.block_length = None

        self.args.add = True
        self.args.remove = False
        self.args.clean = False
        self.args.removeall = False
        self.args.item = []
        self.args.file = 'tests.items'

        # create a new config file
        env = lib.Environment(self.args)
        lib.Lists(self.args, env)
        lib.Items(self.args, env)

        self.assertEqual(
            len(env.config['lists'][0]['items']),
            2
        )

    def test_add_geo_bad(self):
        '''
        try to add an invalid new item to geo list
        '''

        self.args.new = True
        self.args.delete = False
        self.args.list = ['a_new_list']
        self.args.type = 'geo'
        self.args.action = 'block'
        self.args.match = 'exact'
        self.args.variable = None
        self.args.block_length = None

        self.args.add = True
        self.args.remove = False
        self.args.clean = False
        self.args.removeall = False
        self.args.item = ['United States of America']
        self.args.file = None

        # create a new config file
        env = lib.Environment(self.args)
        lib.Lists(self.args, env)
        lib.Items(self.args, env)

        self.assertFalse(env.config['lists'][0]['items'])

    def test_add_geo_file_bad(self):
        '''
        try to add itemss to geo list from args.file that doesn't exist
        '''

        self.args.new = True
        self.args.delete = False
        self.args.list = ['a_new_list']
        self.args.type = 'geo'
        self.args.action = 'block'
        self.args.match = 'exact'
        self.args.variable = None
        self.args.block_length = None

        self.args.add = True
        self.args.remove = False
        self.args.clean = False
        self.args.removeall = False
        self.args.item = []
        self.args.file = 'tests.items'

        # create new environment
        env = lib.Environment(self.args)
        lib.Lists(self.args, env)

        with self.assertRaisesRegex(
                SystemExit,
                "could not read items from file"
            ):
            lib.Items(self.args, env)

    def test_add_geo_duplicate(self):
        '''
        try to add a duplicate item to geo list
        '''

        self.args.new = True
        self.args.delete = False
        self.args.list = ['a_new_list']
        self.args.type = 'geo'
        self.args.action = 'block'
        self.args.match = 'exact'
        self.args.variable = None
        self.args.block_length = None

        self.args.add = True
        self.args.remove = False
        self.args.clean = False
        self.args.removeall = False
        self.args.item = ['US']
        self.args.file = None

        # create a new environment
        env = lib.Environment(self.args)
        lib.Lists(self.args, env)
        lib.Items(self.args, env)

        self.args.init = False
        self.args.new = False
        lib.Items(self.args, env)

        self.assertEqual(
            len(env.config['lists'][0]['items']),
            1
        )

    def test_add_block(self):
        '''
        try to add a valid new item to block list
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

        # create a new environment
        env = lib.Environment(self.args)
        lib.Lists(self.args, env)
        lib.Items(self.args, env)

        self.assertEqual(
            env.config['lists'][0]['items'][0],
            '!10.0.0.0/8'
        )

    def test_add_block_bad(self):
        '''
        try to add an invalid new item to block list
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
        self.args.item = ['867-5309']
        self.args.file = None

        # create a new environment
        env = lib.Environment(self.args)
        lib.Lists(self.args, env)
        lib.Items(self.args, env)

        self.assertFalse(env.config['lists'][0]['items'])

    def test_add_block_duplicate(self):
        '''
        try to add a duplicate item to block list
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

        # create a new environment
        env = lib.Environment(self.args)
        lib.Lists(self.args, env)
        lib.Items(self.args, env)

        self.args.init = False
        self.args.new = False
        lib.Items(self.args, env)

        self.assertEqual(
            len(env.config['lists'][0]['items']),
            1
        )

    def test_add_temp(self):
        '''
        try to add a valid new item to temp list
        '''

        self.args.new = True
        self.args.delete = False
        self.args.list = ['a_new_list']
        self.args.type = 'temp'
        self.args.action = 'block'
        self.args.match = 'exact'
        self.args.variable = None
        self.args.block_length = 600

        self.args.add = True
        self.args.remove = False
        self.args.clean = False
        self.args.removeall = False
        self.args.item = ['10.0.0.1']
        self.args.file = None

        # create a new environment
        env = lib.Environment(self.args)
        lib.Lists(self.args, env)
        lib.Items(self.args, env)

        expiration_time = int(time.time()) + self.args.block_length
        lib.Items(self.args, env)

        self.assertTrue(env.config['lists'][0]['items'][0]['10.0.0.1'])
        self.assertEqual(
            env.config['lists'][0]['items'][0]['10.0.0.1'],
            expiration_time
        )

    def test_add_temp_bad(self):
        '''
        try to add an invalid new item to temp list
        '''

        self.args.new = True
        self.args.delete = False
        self.args.list = ['a_new_list']
        self.args.type = 'temp'
        self.args.action = 'block'
        self.args.match = 'exact'
        self.args.variable = None
        self.args.block_length = 600

        self.args.add = True
        self.args.remove = False
        self.args.clean = False
        self.args.removeall = False
        self.args.item = ['867-5309']
        self.args.file = None

        # create a new environment
        env = lib.Environment(self.args)
        lib.Lists(self.args, env)
        lib.Items(self.args, env)

        self.assertFalse(env.config['lists'][0]['items'])

    def test_add_var(self):
        '''
        try to add a valid new item to var list
        '''

        self.args.new = True
        self.args.delete = False
        self.args.list = ['a_new_list']
        self.args.type = 'var'
        self.args.action = 'block'
        self.args.match = 'exact'
        self.args.variable = 'var.whatever'
        self.args.block_length = 600

        self.args.add = True
        self.args.remove = False
        self.args.clean = False
        self.args.removeall = False
        self.args.item = ['ABC']
        self.args.file = None

        # create a new environment
        env = lib.Environment(self.args)
        lib.Lists(self.args, env)
        lib.Items(self.args, env)

        self.assertEqual(
            env.config['lists'][0]['items'][0]['ABC'],
            'fastly-blocklist'
        )

    def test_add_combo(self):
        '''
        try to add a valid new combo list
        '''

        self.args.new = True
        self.args.delete = False
        self.args.list = ['LIST1', 'LIST2']
        self.args.type = 'block'
        self.args.action = 'block'
        self.args.match = None
        self.args.variable = None
        self.args.block_length = 600

        self.args.add = True
        self.args.remove = False
        self.args.clean = False
        self.args.removeall = False
        self.args.item = ['!10.0.0.0/8']
        self.args.file = None

        # create a new environment
        env = lib.Environment(self.args)
        lib.Lists(self.args, env)
        lib.Items(self.args, env)

        self.args.list = ['COMBO']
        self.args.type = 'combo'
        self.args.item = ['LIST1', 'LIST2']
        lib.Lists(self.args, env)
        lib.Items(self.args, env)

        self.assertEqual(
            len(env.config['lists'][2]['items']),
            2
        )

    def test_add_combo_bad(self):
        '''
        try to add an invalid new combo list
        '''

        self.args.new = True
        self.args.delete = False
        self.args.list = ['LIST1', 'LIST2']
        self.args.type = 'block'
        self.args.action = 'block'
        self.args.match = None
        self.args.variable = None
        self.args.block_length = 600

        self.args.add = True
        self.args.remove = False
        self.args.clean = False
        self.args.removeall = False
        self.args.item = ['!10.0.0.0/8']
        self.args.file = None

        # create a new environment
        env = lib.Environment(self.args)
        lib.Lists(self.args, env)
        lib.Items(self.args, env)

        self.args.list = ['COMBO']
        self.args.type = 'combo'
        self.args.item = ['CALM', 'DOWN']
        lib.Lists(self.args, env)
        lib.Items(self.args, env)

        self.assertFalse(env.config['lists'][2]['items'])

    def test_remove_item_bad(self):
        '''
        try to remove item when no args.item or args.file provided
        '''

        self.args.new = True
        self.args.delete = False
        self.args.list = ['a_new_list']
        self.args.type = 'block'
        self.args.action = 'block'
        self.args.match = 'exact'
        self.args.variable = None
        self.args.block_length = None

        self.args.add = False
        self.args.remove = True
        self.args.clean = False
        self.args.removeall = False
        self.args.item = []
        self.args.file = None

        # create a new environment
        env = lib.Environment(self.args)
        lib.Lists(self.args, env)

        with self.assertRaisesRegex(
                SystemExit,
                "remove requires list items"
            ):
            lib.Items(self.args, env)

    def test_remove_geo(self):
        '''
        try to remove item from geo list
        '''

        self.args.new = True
        self.args.delete = False
        self.args.list = ['a_new_list']
        self.args.type = 'geo'
        self.args.action = 'block'
        self.args.match = 'exact'
        self.args.variable = None
        self.args.block_length = None

        self.args.add = True
        self.args.remove = False
        self.args.clean = False
        self.args.removeall = False
        self.args.item = ['US']
        self.args.file = None

        # create a new config file
        env = lib.Environment(self.args)
        lib.Lists(self.args, env)
        lib.Items(self.args, env)

        self.args.add = False
        self.args.remove = True
        lib.Items(self.args, env)

        self.assertFalse(env.config['lists'][0]['items'])

    def test_remove_geo_bad(self):
        '''
        try to remove item that doesn't exist from geo list
        '''

        self.args.new = True
        self.args.delete = False
        self.args.list = ['a_new_list']
        self.args.type = 'geo'
        self.args.action = 'block'
        self.args.match = 'exact'
        self.args.variable = None
        self.args.block_length = None

        self.args.add = True
        self.args.remove = False
        self.args.clean = False
        self.args.removeall = False
        self.args.item = ['US']
        self.args.file = None

        # create a new config file
        env = lib.Environment(self.args)
        lib.Lists(self.args, env)
        lib.Items(self.args, env)

        self.args.add = False
        self.args.remove = True
        self.args.item = ['United States of America']
        lib.Items(self.args, env)

        self.assertTrue(env.config['lists'][0]['items'])

    def test_remove_block(self):
        '''
        try to remove item from block list
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

        # create a new environment
        env = lib.Environment(self.args)
        lib.Lists(self.args, env)
        lib.Items(self.args, env)

        self.args.add = False
        self.args.remove = True
        lib.Items(self.args, env)

        self.assertFalse(env.config['lists'][0]['items'])

    def test_remove_block_bad(self):
        '''
        try to remove item that doesn't exist from block list
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

        # create a new environment
        env = lib.Environment(self.args)
        lib.Lists(self.args, env)
        lib.Items(self.args, env)

        self.args.add = False
        self.args.remove = True
        self.args.item = ['127.0.0.1']
        lib.Items(self.args, env)

        self.assertTrue(env.config['lists'][0]['items'])

    def test_clean(self):
        '''
        try to clean expired items from all temp lists
        '''

        self.args.new = True
        self.args.delete = False
        self.args.list = ['a_new_list']
        self.args.type = 'temp'
        self.args.action = 'block'
        self.args.match = 'exact'
        self.args.variable = None
        self.args.block_length = 600

        self.args.add = True
        self.args.remove = False
        self.args.clean = False
        self.args.removeall = False
        self.args.item = ['10.0.0.1']
        self.args.file = None

        # create a new environment
        env = lib.Environment(self.args)
        lib.Lists(self.args, env)
        lib.Items(self.args, env)

        force_expiration_time = int(time.time()) - self.args.block_length
        env.config['lists'][0]['items'][0]['10.0.0.1'] = force_expiration_time

        self.args.add = False
        self.args.list = []
        self.args.clean = True
        lib.Items(self.args, env)

        self.assertFalse(env.config['lists'][0]['items'])

    def test_clean_list(self):
        '''
        try to clean expired items from a specific temp list
        '''

        self.args.new = True
        self.args.delete = False
        self.args.list = ['a_new_list']
        self.args.type = 'temp'
        self.args.action = 'block'
        self.args.match = 'exact'
        self.args.variable = None
        self.args.block_length = 600

        self.args.add = True
        self.args.remove = False
        self.args.clean = False
        self.args.removeall = False
        self.args.item = ['10.0.0.1']
        self.args.file = None

        # create a new environment
        env = lib.Environment(self.args)
        lib.Lists(self.args, env)
        lib.Items(self.args, env)

        force_expiration_time = int(time.time()) - self.args.block_length
        env.config['lists'][0]['items'][0]['10.0.0.1'] = force_expiration_time

        self.args.add = False
        self.args.clean = True
        lib.Items(self.args, env)

        self.assertFalse(env.config['lists'][0]['items'])

    def test_removeall(self):
        '''
        try to remove all items from all lists
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
        self.args.item = ['!10.0.0.1/8']
        self.args.file = None

        # create a new environment
        env = lib.Environment(self.args)
        lib.Lists(self.args, env)
        lib.Items(self.args, env)

        self.args.add = False
        self.args.list = []
        self.args.removeall = True
        lib.Items(self.args, env)

        self.assertFalse(env.config['lists'][0]['items'])

    def test_removeall_list(self):
        '''
        try to remove all items from a specific list
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
        self.args.item = ['!10.0.0.1/8']
        self.args.file = None

        # create a new environment
        env = lib.Environment(self.args)
        lib.Lists(self.args, env)
        lib.Items(self.args, env)

        self.args.add = False
        self.args.removeall = True
        lib.Items(self.args, env)

        self.assertFalse(env.config['lists'][0]['items'])


if __name__ == '__main__':
    unittest.main()
