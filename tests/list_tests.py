'''
Test list management in lib.Lists()
'''

import unittest

import os
import argparse

import lib


class ListTests(unittest.TestCase):
    '''
    Test list management in lib.Lists()
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
        except BaseException:
            pass

    def test_new_list(self):
        '''
        try to create a valid new list with action block
        '''

        self.args.new = True
        self.args.delete = False
        self.args.list = ['a_new_list']
        self.args.type = 'block'
        self.args.action = 'block'
        self.args.match = None
        self.args.variable = None
        self.args.block_length = None

        # create a new environment
        env = lib.Environment(self.args)

        # create a new list
        lib.Lists(self.args, env)

        self.assertEqual(
            len(env.config['lists']),
            1
        )
        self.assertEqual(
            env.config['lists'][0]['name'],
            'a_new_list'
        )
        self.assertEqual(
            env.config['lists'][0]['type'],
            'block'
        )
        print(env.config['lists'][0])
        self.assertEqual(
            env.config['lists'][0]['action_none'],
            False
        )
        self.assertEqual(
            env.config['lists'][0]['action_log'],
            True
        )
        self.assertEqual(
            env.config['lists'][0]['action_block'],
            True
        )

    def test_new_list_log(self):
        '''
        try to create a valid new list with action log
        '''

        self.args.new = True
        self.args.delete = False
        self.args.list = ['a_new_list']
        self.args.type = 'block'
        self.args.action = 'log'
        self.args.match = None
        self.args.variable = None
        self.args.block_length = None

        # create a new environment
        env = lib.Environment(self.args)

        # create a new list
        lib.Lists(self.args, env)

        self.assertEqual(
            len(env.config['lists']),
            1
        )
        self.assertEqual(
            env.config['lists'][0]['name'],
            'a_new_list'
        )
        self.assertEqual(
            env.config['lists'][0]['type'],
            'block'
        )
        self.assertEqual(
            env.config['lists'][0]['action_none'],
            False
        )
        self.assertEqual(
            env.config['lists'][0]['action_log'],
            True
        )
        self.assertEqual(
            env.config['lists'][0]['action_block'],
            False
        )

    def test_new_list_none(self):
        '''
        try to create a valid new list with action none
        '''

        self.args.new = True
        self.args.delete = False
        self.args.list = ['a_new_list']
        self.args.type = 'block'
        self.args.action = 'none'
        self.args.match = None
        self.args.variable = None
        self.args.block_length = None

        # create a new environment
        env = lib.Environment(self.args)

        # create a new list
        lib.Lists(self.args, env)

        self.assertEqual(
            len(env.config['lists']),
            1
        )
        self.assertEqual(
            env.config['lists'][0]['name'],
            'a_new_list'
        )
        self.assertEqual(
            env.config['lists'][0]['type'],
            'block'
        )
        self.assertEqual(
            env.config['lists'][0]['action_none'],
            True
        )
        self.assertEqual(
            env.config['lists'][0]['action_block'],
            False
        )

    def test_new_list_bad(self):
        '''
        try to create a list where no args.list provided
        '''

        self.args.new = True
        self.args.delete = False
        self.args.list = []
        self.args.type = 'block'
        self.args.action = 'block'
        self.args.match = None
        self.args.variable = None
        self.args.block_length = None

        # create a new environment
        env = lib.Environment(self.args)

        with self.assertRaisesRegex(
                SystemExit,
                r"no list name\(s\) defined"
        ):
            lib.Lists(self.args, env)

    def test_new_list_var(self):
        '''
        try to create a valid new var list
        '''

        self.args.new = True
        self.args.delete = False
        self.args.list = ['a_new_list']
        self.args.type = 'var'
        self.args.action = 'block'
        self.args.match = 'exact'
        self.args.variable = 'req.whatever'
        self.args.block_length = None

        # create a new environment
        env = lib.Environment(self.args)
        lib.Lists(self.args, env)

        self.assertEqual(
            len(env.config['lists']),
            1
        )
        self.assertEqual(
            env.config['lists'][0]['type'],
            'var'
        )
        self.assertEqual(
            env.config['lists'][0]['match'],
            'exact'
        )
        self.assertEqual(
            env.config['lists'][0]['variable'],
            'req.whatever'
        )

    def test_new_list_var_bad(self):
        '''
        try to create a new var list where no args.variable provided
        '''

        self.args.new = True
        self.args.delete = False
        self.args.list = ['a_new_list']
        self.args.type = 'var'
        self.args.action = 'block'
        self.args.match = 'exact'
        self.args.variable = None
        self.args.block_length = None

        # create a new environment
        env = lib.Environment(self.args)

        with self.assertRaisesRegex(
                SystemExit,
                "no list variable defined"
        ):
            lib.Lists(self.args, env)

    def test_new_list_temp(self):
        '''
        try to create a valid new temp list
        '''

        self.args.new = True
        self.args.delete = False
        self.args.list = ['a_new_list']
        self.args.type = 'temp'
        self.args.action = 'block'
        self.args.match = None
        self.args.variable = None
        self.args.block_length = 600

        # create a new environment
        env = lib.Environment(self.args)
        lib.Lists(self.args, env)

        self.assertEqual(
            len(env.config['lists']),
            1
        )
        self.assertEqual(
            env.config['lists'][0]['type'],
            'temp'
        )
        self.assertEqual(
            env.config['lists'][0]['block_length'],
            600
        )

    def test_new_list_temp_bad(self):
        '''
        try to create a new temp list where no args.block_length provided
        '''

        self.args.new = True
        self.args.delete = False
        self.args.list = ['a_new_list']
        self.args.type = 'temp'
        self.args.action = 'block'
        self.args.match = None
        self.args.variable = None
        self.args.block_length = None

        # create a new environment
        env = lib.Environment(self.args)

        with self.assertRaisesRegex(
                SystemExit,
                "no list block_length defined"
        ):
            lib.Lists(self.args, env)

    def test_delete_list(self):
        '''
        try to create and delete a valid list
        '''

        self.args.new = True
        self.args.delete = False
        self.args.list = ['a_new_list']
        self.args.type = 'var'
        self.args.action = 'block'
        self.args.match = 'exact'
        self.args.variable = 'req.whatever'
        self.args.block_length = None

        # create a new environment
        env = lib.Environment(self.args)
        lib.Lists(self.args, env)

        self.args.new = False
        self.args.delete = True

        lib.Lists(self.args, env)

        self.assertFalse(env.config['lists'])

    def test_delete_list_bad(self):
        '''
        try to delete a list where no args.list provided
        '''

        self.args.new = True
        self.args.delete = False
        self.args.list = ['a_new_list']
        self.args.type = 'var'
        self.args.action = 'block'
        self.args.match = 'exact'
        self.args.variable = 'req.whatever'
        self.args.block_length = None

        # create a new environment
        env = lib.Environment(self.args)
        lib.Lists(self.args, env)

        self.args.new = False
        self.args.delete = True
        self.args.list = []

        with self.assertRaisesRegex(
                SystemExit,
                r"no list name\(s\) defined"
        ):
            lib.Lists(self.args, env)


if __name__ == '__main__':
    unittest.main()
