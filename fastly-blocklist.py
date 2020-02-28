'''
# fastly-blocklist #

Configure request blocking on a Fastly service.
'''

from pathlib import Path
from argparse import ArgumentParser, RawTextHelpFormatter

import lib


def main(args):
    '''
    run fastly-blocklist
    '''

    # setup our environment
    env = lib.Environment(args)
    state = lib.State()

    # sync state with live service
    if args.sync:
        print('Syncing with live service.')
        remote = lib.Remote(env)
        state.sync(env, remote)

    # list operations
    lib.Lists(args, env)

    # item operations
    lib.Items(args, env)

    # deploy and/or save config state
    if args.commit:
        print('Deploying to live service(s).')
        remote = lib.Remote(env)
        state.commit(env, remote)
    if args.save:
        print(f'Saving running config to file: {env.config_file}')
        state.save(env)
    else:
        print(f'Warning: This change has NOT been saved. Use --save to store '
              f'in config file: {env.config_file}'
              )


if __name__ == '__main__':

    version = '0.1.0'

    PARSER = ArgumentParser(formatter_class=RawTextHelpFormatter, description=(
            f'\n# fastly-blocklist # version: {version}\n'
            f'Configure request blocking for a Fastly service.\n'
    ))
    # Enable verbose mode
    PARSER.add_argument('-v', '--verbose', required=False, action='store_true',
                        help=("Enable verbose mode.")
                        )
    # Manage blocklist environment
    ENVIRONMENT = PARSER.add_argument_group('ENVIRONMENT',
                                            'Manage blocklist environment'
                                            )
    ENVIRONMENT.add_argument('--init', required=False, action='store_true',
                             help=("Create a new fastly-blocklist config.")
                             )
    ENVIRONMENT.add_argument(
        '--force',
        required=False,
        action='store_true',
        help=(
            "Force config initialization, overwriting existing local config "
            "file."))
    ENVIRONMENT.add_argument(
        '--apikey', required=False, default='{}/.fastlyctl_token'.format(
            Path.home()), type=str, help=(
                "Location of a file containing Fastly API key/token.\n"
                "\tDefault: Read from ~/.fastlyctl_token"))
    ENVIRONMENT.add_argument('--config', required=False,
                             default='{}/config.blocklist'.format(Path.cwd()),
                             type=str,
                             help=("Location of a fastly-blocklist config file.\n"
                                   "\tDefault: ./config.blocklist"
                                   )
                             )
    ENVIRONMENT.add_argument(
        '--service',
        required=False,
        default=[],
        type=lambda s: [
            str(item) for item in s.split(',')],
        help=(
            "Service(s) to target.\n"
            "\tThis is required on config --init.\n"
            "\tDefault: Read from the selected config file.\n"
            "\tExample: --service ABCDEF,DEFABC"))
    ENVIRONMENT.add_argument(
        '--log',
        required=False,
        default='',
        type=str,
        help=(
            "VCL to execute when a request is logged/blocked.\n"
            "\tDefault: none"))
    ENVIRONMENT.add_argument(
        '--block',
        required=False,
        default='error 403 "Forbidden";',
        type=str,
        help=(
            "VCL to execute when a request is blocked.\n"
            "\tDefault: error 403 \"Forbidden\""))
    # Manage configuration state
    STATE = PARSER.add_argument_group(
        'STATE', 'Modify live service and local config state')
    STATE.add_argument(
        '--sync',
        required=False,
        action='store_true',
        help=("Sync live service configuration to the running config."))
    STATE.add_argument('--commit', required=False, action='store_true',
                       help=("Deploy running config to the live service(s).")
                       )
    STATE.add_argument(
        '--save',
        required=False,
        action='store_true',
        help=("Save running configuration to a fastly-blocklist config file."))
    # Manage lists
    LISTS = PARSER.add_argument_group('LISTS',
                                      'Manage blocklist lists'
                                      )
    LISTS.add_argument('-n', '--new', required=False, action='store_true',
                       help=("Create a new list.")
                       )
    LISTS.add_argument('-d', '--delete', required=False, action='store_true',
                       help=("Delete an existing list.")
                       )
    LISTS.add_argument(
        '-l',
        '--list',
        required=False,
        default=[],
        type=lambda s: [
            str(item) for item in s.split(',')],
        help=(
            "List name(s) to create/update/delete.\n"
            "\tThis is required for all operations on lists & list items.\n"
            "\tExample: my-block-list"))
    LISTS.add_argument(
        '-t',
        '--type',
        required=False,
        choices=[
            'allow',
            'geo',
            'block',
            'temp',
            'var',
            'combo'],
        help=(
            "List type.\n"
            "\tThis is required when creating a new list.\n"
            "\tallow\t- Allow IP addresses. Disables processing for all "
            "other lists.\n"
            "\tgeo \t- Block geolocations (ISO alpha-2).\n"
            "\tblock\t- Block IP addresses permanently.\n"
            "\ttemp\t- Block IP addresses temporarily.\n"
            "\tvar\t- Block whenever a VCL variable matches an item.\n"
            "\tcombo\t- Block whenever any 2+ lists are matched."))
    LISTS.add_argument(
        '--action',
        required=False,
        default='none',
        choices=[
            'none',
            'log',
            'block'],
        help=(
            "Action to take when the list is matched.\n"
            "\tnone\t- No action is taken.\n"
            "\tlog\t- Log that a match occurred.\n"
            "\tblock\t- Block the request and log that a match occurred.\n"
            "\tDefault: none"))
    LISTS.add_argument(
        '--match',
        required=False,
        default='exact',
        choices=[
            'exact',
            'regexp'],
        help=(
            "Match type for var lists.\n"
            "\tThis is required when creating a new var list.\n"
            "\texact\t- Match only if variable value == list item.\n"
            "\tregexp\t- Match if variable value ~ list item.\n"
            "\tDefault: exact"))
    LISTS.add_argument(
        '--variable',
        '--var',
        required=False,
        type=str,
        help=(
            "VCL variable name to match against for var lists.\n"
            "\tThis is required when creating a new var list.\n"
            "\tExample: req.http.User-Agent"))
    LISTS.add_argument(
        '--block_length',
        '--len',
        required=False,
        default=600,
        type=int,
        help=(
            "Block length in seconds for temp lists.\n"
            "\tItems will be added with expiration time (now + len).\n"
            "\tDefault: 600"))
    # Manage list items
    ITEMS = PARSER.add_argument_group('ITEMS',
                                      'Manage list items'
                                      )
    ITEMS.add_argument('-a', '--add', required=False, action='store_true',
                       help=("Add an item or items to a list.")
                       )
    ITEMS.add_argument('-r', '--remove', required=False, action='store_true',
                       help=("Remove an item or items from a list.")
                       )
    ITEMS.add_argument(
        '-i',
        '--item',
        required=False,
        default=[],
        type=lambda s: [
            str(item) for item in s.split(',')],
        help=(
            "List item(s) to add/remove.\n"
            "\t--item or --file are required when operating on list items.\n"
            "\tExample: 1.2.3.4,4.3.2.1"))
    ITEMS.add_argument(
        '-f',
        '--file',
        required=False,
        type=str,
        help=(
            "File containing list items to add/remove.\n"
            "\t--item or --file are required when operating on list items."))
    ITEMS.add_argument(
        '--clean',
        required=False,
        action='store_true',
        help=(
            "Clean up expired entries from temp list(s) in the running "
            "config."))
    ITEMS.add_argument(
        '--removeall',
        required=False,
        action='store_true',
        help=(
            "Remove all items from a list or all lists in the running "
            "config."))

    # print the fastly-blocklist header
    print(PARSER.description)

    main(PARSER.parse_args())
