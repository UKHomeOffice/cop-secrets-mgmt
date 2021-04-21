#  git_handler - This handles basic git operations

import os
import sh
import logging


class Git_Process(object):
    def __init__(self, clone_path='', remote_repo=''):
        self.path = clone_path
        self.repo = remote_repo
        self.git = sh.git.bake(_cwd=self.path)

    def git_clone(self):
        if os.path.isdir(self.path):
            logging.info(f"Repo: {self.repo} at path: {self.path} already exists, "
                         f"pulling latest updates only")
            return None
        else:
            try:
                sh.git.clone(self.repo, self.path)
            except sh.ErrorReturnCode_128 as err:
                logging.error(f"Cannot Clone, on macosx make sure to add passphrases "
                              f"before hand running ssh-add ~/.ssh/<rest_of_path_to_ssh_key>")
                exit(1)
            return "done"

    def git_checkout(self, branch=None):
        if branch:
            try:
                print(self.git.checkout(branch))
            except sh.ErrorReturnCode_1 as err:
                logging.warning(f"Cannot checkout branch, Skipping Git Branch Step :: Error: {err}")
                raise ValueError(f"Error Message: {err}")

    def git_branch(self, branch=None):
        if branch:
            try:
                print(self.git.checkout("-b", branch))
            except sh.ErrorReturnCode_1 as err:
                logging.warning(f"Cannot checkout branch, Skipping Git Branch Step :: Error: {err}")
                raise ValueError(f"Error Message: {err}")

    def git_show_branch(self):
        try:
            current_branch = self.git.branch("--show-current")
            return current_branch
        except sh.ErrorReturnCode_1 as err:
            logging.warning(f"Cannot show current branch, Skipping :: Error: {err}")
            return None

    def git_branch_track(self, branch=None):
        if branch:
            try:
                print(self.git.branch("-u", "origin/" + branch, branch))
            except sh.ErrorReturnCode_1 as err:
                logging.info("Cannot track remote branch, Skipping Git Branch Track Step")
                raise ValueError(f"Error:: {err}")

    def git_pull(self):
        try:
            print(self.git.pull('--rebase'))
        except sh.ErrorReturnCode_1 as err:
            logging.info(f"Cannot pull remote branch may not exist or changes may need to be committed, "
                         f"Skipping Git Pull Step")
            raise ValueError(f"Error Message: {err}")

    def git_pull_prune(self):
        try:
            print(self.git.pull('--prune'))
        except sh.ErrorReturnCode_1 as err:
            logging.info(f"Cannot pull remote branch may not exist or changes may need to be committed, "
                         f" Skipping Git Pull Step")
            raise ValueError(f"Error Message: {err}")

    def git_status(self):
        try:
            print(self.git.status)
        except sh.ErrorReturnCode_1 as err:
            logging.warning(f"Cant get status, Error Message :: {err}")
            return "fail"

    def git_show(self):
        try:
            print(self.git.show)
        except sh.ErrorReturnCode_1 as err:
            logging.warning(f"Cant show, Error Message :: {err}")
            return "fail"

    def git_log(self, commits='2'):
        try:
            print(self.git.log("--decorate=short", "--sparse", "-n", commits))
        except sh.ErrorReturnCode_1 as err:
            logging.warning(f"Cant show logs, Error Message :: {err}")
            return "fail"

    def __del__(self):
        if os.path.isdir(self.path):
            logging.info(f"Leaving repo: {self.repo} in Path: {self.path}, for developers to work on")
