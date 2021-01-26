#  command_parser
#    This manages command line arguments, verifies them and handles
#    initialisation and injection of configuration data.

import argparse
import os
import sys
import logging

try:
    from ruamel import yaml
except:
    import yaml


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

    def add_config(self):
        base_path = os.path.expanduser('~')
        config_file = os.path.join(base_path, "cop-auto-deploy", "config.yaml")
        self.parser.add_argument('-c', '--config', action='store', default=config_file,
                                 help=' '.join(['specify the location of the config file,',
                                                'defaults to  \'~/cop-auto-deploy/config.yaml\'']))

    def add_user_auth(self):
        self.parser.add_argument('-l', '--auth', dest='authenticate', required=False, action='store_true',
                                 help='Authentication required, default False')
        self.parser.add_argument('-m', '--mfa', dest='mfa', help='MFA device id')
        self.parser.add_argument('-p', '--primaryaccount', dest='primaryaccount', help='HO primary account')
        self.parser.add_argument('-a', '--account', dest='account', help='AWS Account number')
        self.parser.add_argument('-n', '--rolename', dest='rolename', help='AWS role name')

    def add_dry_run(self):
        self.parser.add_argument('-d', '--dry-run', dest='dryrun', required=False, action='store_true',
                                 help='Only show secrets that would be updated in Drone, default False')

    def set_options(self):
        options = self.parser.parse_args()
        return options, self.parser


class CommandCheck(object):
    def __init__(self, options=None, parser=None, config_data=None):
        self.options = options
        self.parser = parser
        self.data = config_data

    def login(self):
        if not 'aws' in self.data:
            self.data['aws'] = {}
        self.data['aws']['authenticate'] = False
        self.data['aws']['role_arn'] = None
        self.data['aws']['mfa_arn'] = None
        if self.options.authenticate:
            if not self.options.account:
                self.parser.print_help()
                self.parser.error('An AWS Account number must be provided')
            if not self.options.primaryaccount:
                self.parser.print_help()
                self.parser.error('A HO Primary Account must be provided')
            if not self.options.rolename:
                self.parser.print_help()
                self.parser.error('An AWS Role Name must be provided')
            if not self.options.mfa:
                self.parser.print_help()
                self.parser.error('An MFA Device ID Must be provided (Usually your HO Email)')
            self.data['aws']['authenticate'] = True
            self.data['aws']['role_arn'] = (f'arn:aws:iam::{self.options.account}:{self.options.rolename}')
            self.data['aws']['mfa_arn'] = (f'arn:aws:iam:{self.options.primaryaccount}:mfa/{self.options.mfa}')

    def get_envs(self):
        secret_env = os.environ.get('DEPLOY_ENV')
        repo_secrets_file = os.environ.get('DRONE_WORKSPACE') + '/env.yaml
        drone_server = os.environ.get('DRONE_SERVER')
        drone_user_token = os.environ.get('DRONE_TOKEN')
        drone_repo = os.environ.get('DRONE_REPO')
        drone_version = os.environ.get('DRONE_VERSION')
        drone_alt_version = "v0"

        if not 'drone' in self.data:
            self.data['drone'] = {}

        if not 'secrets' in self.data:
            self.data['secrets'] = {}

        if not secret_env:
            secret_env = os.environ.get('DRONE_DEPLOY_TO')
            if not secret_env:
                secret_env = 'dev'

        if not drone_server:
            logging.error('Drone Server Url Environment variable not set: Exiting')
            exit(1)

        if not drone_repo:
            logging.error('Drone Repo Environment variable not set: Exiting')
            exit(1)

        if "gitlab" in drone_server:
            drone_token_name = 'drone_private_token'
        else:
            drone_token_name = 'drone_public_token'

        try:
            version = drone_version.split('v')[-1]
            version = int(version.split('.')[0])
        except (AttributeError, ValueError):
            logging.warning(f'Error: Drone version: {version}, '
                            f'is not a recognised version, '
                            f'defaulting to Drone v0 payload')

        if version >= 1:
            logging.debug(f'Drone version: {drone_version}, Using Drone v1 Payload')
            drone_alt_version = "v1"


        self.data['deploy_env'] = secret_env
        self.data['secrets_file'] = repo_secrets_file
        self.data['drone']['repo'] = drone_repo
        self.data['drone']['url'] = f'{drone_server}/api/repos/{drone_repo}/secrets'
        self.data['drone']['server'] = drone_server
        self.data['drone']['token'] = drone_user_token
        self.data['drone']['token_name'] = drone_token_name
        self.data['drone']['version'] = drone_version
        self.data['drone']['alt_version'] = drone_alt_version

    def return_data(self):
        return self.data
