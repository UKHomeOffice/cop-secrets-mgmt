import logging
from libs import git_handler


class Tree(dict):
    def __getattr__(self, attr):
        return self[attr]

    def __setattr__(self, attr, val):
        self[attr] = val

    def __missing__(self, key):
        value = self[key] = type(self)()
        return value


def summary_status(success_list, error_list, dry_run):
    print('\n')
    if dry_run:
        print('\n**** No changes have been made, dry-run only ****\n')
    print('Successful secrets')
    print('------------------')
    for success_item in success_list:
        print(success_item)

    print('\n\nUnsuccessful secrets')
    print('--------------------')
    for error_item in error_list:
        print(error_item)


def git_process(repo_data=None):
    repo = git_handler.Git_Process(clone_path=repo_data['path'],
                                   remote_repo=repo_data['url'])
    clone_status = repo.git_clone()
    if not clone_status:
        current_branch = str(repo.git_show_branch()).strip()
        if current_branch == repo_data['branch']:
            try:
                repo.git_pull_prune()
            except ValueError as err:
                logging.info(f"Unable to update Repo: {repo_data['path']} :: "
                             f"branch: {repo_data['branch']} :: "
                             f"Error: {err} :: skipping")
        else:
            logging.warning(f"repo: {repo_data['path']}, "
                            f"current branch: {current_branch},"
                            f"expected_branch: {repo_data['branch']}, branch mismatch skipping update")
    else:
        try:
            repo.git_checkout(branch=repo_data['branch'])
        except ValueError as err:
            logging.info(f"Unable to checkout Repo: {repo_data['path']} :: "
                         f"branch: {repo_data['branch']} :: "
                         f"Error: {err} :: skipping")
        try:
            repo.git_pull_prune()
        except ValueError as err:
            logging.info(f"Unable to update Repo: {repo_data['path']} :: "
                         f"branch: {repo_data['branch']} :: "
                         f"Error: {err} :: skipping")


def flatten_dict(current, key, result):
    if isinstance(current, dict):
        for k in current:
            new_key = "{0}_{1}".format(key, k) if len(key) > 0 else k
            flatten_dict(current[k], new_key, result)
    else:
        result[key] = current

    return result


def flatten_seed(data):
    seed_list = []
    for key in data['keys']:
        if isinstance(key, dict):
            seed_result = flatten_dict(key, '', {})
            for key_name, key_values in seed_result.items():
                for key_value in key_values.split():
                    seed_list.append(key_name + '_' + key_value)
        else:
            seed_list.append(key)

    return seed_list


class Sorter(object, ):
    def __init__(self, data=None, io_handle=None):
        self.data = data
        self.io_handle = io_handle
        self.env_exclusions = self.data['exclusion_lists']['env']
        self.global_exclusions = self.data['exclusion_lists']['global']
        self.env = self.data['env']
        self.new_env = self.data['new_env']
        self.value_list = []
        self.key_list = []
        self.old_secrets_list = []
        self.sorted_data = Tree()

    def flatten_sort(self, env_data, key):
        if isinstance(env_data, dict):
            for k in env_data:
                new_key = k
                if key:
                    new_key = f"{key}_{k}"
                self.flatten_sort(env_data[k], new_key)
        else:
            data_list = env_data.split()
            data_list = self.io_handle.clean_values(data_list)
            self.sorted_data[key] = data_list

        return self.sorted_data

    def create_old_secrets(self):
        for key, values in self.sorted_data.items():
            for value in values:
                secret = f'{key}_{value}'
                if secret not in self.global_exclusions:
                    secret = f'{self.env}_{secret}'
                self.old_secrets_list.append(secret)
        return self.old_secrets_list

    def sort_env_data(self, env_data, key_list=[]):
        if isinstance(env_data, dict):
            for key in env_data:
                # self.key_list.append(key)
                key_list.append(key)
                self.sort_env_data(env_data[key], key_list)
        else:
            data_list = env_data.split()
            data_list = self.io_handle.clean_values(data_list)
            self.value_list.append(data_list)
            new_env_data = self.new_env_data(keys=key_list, values=data_list)
            self.sorted_data.update(new_env_data)
        return self.sorted_data

    def new_env_data(self, keys=None, values=None):
        data = Tree()
        for idx, key in enumerate(keys):
            if idx == len(keys) - 1:
                data[key] = values
            data = data[key]
        print(f"data currently: {data}")
        return data
