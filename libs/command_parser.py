#  command_parser
#    This manages command line arguments

import argparse
import os


class Commands(object):
    def __init__(self, name='', version='0.0.1', message=''):
        self.name = name
        self.version = version
        self.message = message
        self.parser = argparse.ArgumentParser(prog=self.name,
                                              usage='\n'.join([
                                                  self.name + ' [options]',
                                                  'Version: ' + self.version,
                                              ]))
        self.parser.add_argument('--version', action='version', version=self.version)
        self.env_choices = ['local', 'dev', 'sit', 'staging', 'production']

    def add_config(self):
        libs_path = os.path.dirname(os.path.realpath(__file__))
        base_path, libs_dir = libs_path.split('libs')
        config_file = os.path.join(base_path, 'configs', 'config.yml')
        self.parser.add_argument('-c', '--config', action='store', default=config_file,
                                 help=f'specify the location of the config file, '
                                      f'defaults to  \'{config_file}\'')

    def add_env(self):
        self.parser.add_argument('-e', '--env', dest='env', required=False, default=None,
                                 choices=self.env_choices,
                                 help=f'Specify the environment, valid choices are: '
                                      f'{" ".join(self.env_choices)}')

    def add_new_env(self):
        self.parser.add_argument('-N', '--new-env', dest='new_env', required=True, default=None,
                                 choices=self.env_choices,
                                 help=f'Specify the environment the secret is being copied to, '
                                      f'valid choices are: {" ".join(self.env_choices)} This must be provided')

    def add_user_auth(self):
        self.parser.add_argument('-l', '--auth', dest='authenticate', required=False, action='store_true',
                                 help='Authentication required, default False')
        self.parser.add_argument('-m', '--mfa', dest='mfa', help='MFA device id')
        self.parser.add_argument('-a', '--primary-account', dest='primary_account', help='HO primary account')
        self.parser.add_argument('-s', '--switch-account', dest='switch_account',
                                 help='AWS Secondary Account number to switch into')
        self.parser.add_argument('-r', '--role-name', dest='role_name', help='AWS role name')

    def add_project(self):
        self.parser.add_argument('-p', '--project', dest='project', help='Project to gather secrets from')

    def add_dry_run(self):
        self.parser.add_argument('-d', '--dry-run', dest='dryrun', required=False, action='store_true',
                                 help='Only show secrets that would be updated in Drone, default False')

    def set_options(self):
        options = self.parser.parse_args()
        return options, self.parser
