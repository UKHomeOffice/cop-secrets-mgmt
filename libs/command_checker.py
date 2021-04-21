#  command_checker
#    This verifies command line arguments and handles
#    initialisation and injection of configuration data.

import os
import logging


class CommandCheck(object):
    def __init__(self, options=None, parser=None, config_data=None, io_handler=None):
        self.options = options
        self.parser = parser
        self.data = config_data
        self.io_handle = io_handler

    def login(self):
        if 'aws' not in self.data:
            self.data['aws'] = {}
        self.data['aws']['authenticate'] = False
        self.data['aws']['role_arn'] = None
        self.data['aws']['mfa_arn'] = None
        if self.options.authenticate:
            if not self.options.switch_account:
                self.parser.print_help()
                self.parser.error('An AWS Secondary Account number must be provided, to switch into')
            if not self.options.primary_account:
                self.parser.print_help()
                self.parser.error('A Primary Account Number must be provided')
            if not self.options.role_name:
                self.parser.print_help()
                self.parser.error('An AWS Role Name must be provided')
            if not self.options.mfa:
                self.parser.print_help()
                self.parser.error('An MFA Device ID Must be provided (Usually your HO Email)')
            self.data['aws']['authenticate'] = True
            self.data['aws']['role_arn'] = f'arn:aws:iam::{self.options.switch_account}:role/{self.options.role_name}'
            self.data['aws']['mfa_arn'] = f'arn:aws:iam::{self.options.primary_account}:mfa/{self.options.mfa}'

    def get_project(self):
        if 'projects_file' not in self.data:
            raise KeyError('A projects_file configuration stanza must be provided in the config file')
        projects_file = self.data['projects_file']

        libs_path = os.path.dirname(os.path.realpath(__file__))
        base_path, libs_dir = libs_path.split('libs')
        base_projects_file = os.path.join(base_path, projects_file)
        config_project_file = os.path.join(base_path, "configs", projects_file)
        projects_project_file = os.path.join(base_path, "projects", projects_file)

        if self.io_handle.file_exists(projects_file):
            logging.info(f'Found projects file in {projects_file}')
        elif self.io_handle.file_exists(base_projects_file):
            logging.warning(f'Unable to read projects file from {projects_file}, found in {base_projects_file}')
            projects_file = base_projects_file
        elif self.io_handle.file_exists(config_project_file):
            logging.warning(f'Unable to read projects file from {projects_file}, found in {config_project_file}')
            projects_file = config_project_file
        elif self.io_handle.file_exists(projects_project_file):
            logging.warning(f'Unable to read projects file from {projects_file}, found in {projects_project_file}')
            projects_file = projects_project_file
        else:
            raise ValueError(f'Unable to read projects file from the given path: {projects_file}, '
                             f'Tried {base_projects_file}, {config_project_file} and {projects_project_file}, '
                             f'no matches, please provide either a valid path or valid relative path to this file')

        project_repos = self.io_handle.read_file(config_file=projects_file, file_type='yaml')
        self.data.update(project_repos)

        if self.options.project:
            self.data['project'] = self.options.project

        if 'project' not in self.data:
            self.parser.print_help()
            self.parser.error('A Project must be provided to retrieve secrets from')

        project_name = self.data['project']

        if project_name not in self.data['projects']:
            raise ValueError(f'Unable to find {project_name} in the provided projects')

    def get_env(self):
        env = self.options.env
        if not env:
            env = os.environ.get('DEPLOY_ENV')
            if not env:
                env = os.environ.get('DRONE_DEPLOY_TO')
                if not env:
                    self.parser.print_help()
                    self.parser.error(f'An Environment must be provided either as an '
                                      f'environment variable (DEPLOY_ENV) or by command line flag (-e)')
        if self.options.new_env:
            self.data['new_env'] = self.options.new_env
        self.data['env'] = env

    def get_drone_settings(self):
        repo_secrets_file = f"{os.environ.get('DRONE_WORKSPACE')}/env.yaml"
        drone_server = os.environ.get('DRONE_SERVER')
        drone_user_token = os.environ.get('DRONE_TOKEN')
        drone_repo = os.environ.get('DRONE_REPO')
        drone_version = os.environ.get('DRONE_VERSION')
        drone_alt_version = "v0"

        if not 'drone' in self.data:
            self.data['drone'] = {}

        if not 'secrets' in self.data:
            self.data['secrets'] = {}

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
            logging.warning(f'Error: Drone version: {drone_version}, '
                            f'is not a recognised version, '
                            f'defaulting to Drone v0 payload')

        if version >= 1:
            logging.debug(f'Drone version: {drone_version}, Using Drone v1 Payload')
            drone_alt_version = "v1"

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
