'''
Manage blockly lists
'''

import re


class Lists():
    '''
    Manage blockly lists
    '''

    def __init__(self, args, env):
        '''
        Manage blockly lists
        '''

        if args.new:
            print('Creating new list.')
            self._new(args, env)
        if args.delete:
            print('Deleting existing list.')
            self._delete(args, env)

    def _new(self, args, env):
        '''
        Create new list(s)
        '''

        # ensure we have all the information we need to create the lsit
        if not args.list:
            exit('Error: no list name(s) defined. Use --list <name>,<name>')
        if not args.type:
            exit('Error: no list type defined. Use --type')
        if not args.action:
            exit('Error: no list action defined. Use --action')
        if args.type == "var":
            if not args.match:
                exit('Error: no list match defined. Use --match')
            if not args.variable:
                exit('Error: no list variable defined. Use --variable')
        if args.type == "temp":
            if not args.block_length:
                exit('Error: no list block_length defined. Use --block_length')

        lists = [blockly_list['name'] for blockly_list in env.config['lists']]
        for name in args.list:

            # validate list name
            if not re.match('^[a-z][a-z0-9_ ]*$', name, re.I):
                exit(f'Error: invalid list name: {name}. '
                     f'Name must start with alphabetical and contain only '
                     f'alphanumeric, underscore, and whitespace'
                     )

            # don't create duplicate lists
            if name in lists:
                exit(f'Error: List already exists. Cannot create: {name}')

            print(f'\tCreating list: {name}')
            blockly_list = {
                'name': f'{name}',
                'type': f'{args.type}',
                'action_block': True if args.action in ['block'] else False,
                'action_log': True if args.action in [
                    'block',
                    'log'] else False,
                'action_none': False if args.action in [
                    'block',
                    'log'] else True,
                'match': args.match,
                'variable': args.variable,
                'block_length': args.block_length,
                'items': []}

            env.config['lists'].append(blockly_list)
            print(f'\tCreated list.')

    def _delete(self, args, env):
        '''
        Delete existing list(s)
        '''

        if not args.list:
            exit('Error: no list name(s) defined. Use --list <name>,<name>')

        print(f'\tDeleting list(s): {args.list}')

        # create a new 'lists' list in config, without the deleted lists. list.
        lists_new = []
        for list_config in env.config['lists']:
            if list_config['name'] in args.list:
                print('\tDeleted list: {}'.format(list_config['name']))
            else:
                lists_new.append(list_config)

        env.config['lists'] = lists_new
