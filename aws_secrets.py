#!/usr/bin/env python

import argparse
import os
import yaml
from common import *
from credentials import *
from secrets import *

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


def processEnvSecrets(client, src_file, dry_run):
    with open(src_file, 'r') as seed_stream:
        seed_data = yaml.safe_load(seed_stream)
        seed_list = flatten_seed(seed_data)

    error_list = []
    success_list = []

    secret_env = os.environ.get('DEPLOY_ENV')
    if secret_env is None:
        secret_env = os.environ.get('DRONE_DEPLOY_TO')
        if secret_env is None:
            secret_env = 'dev'

    drone_server_url = os.environ.get('DRONE_SERVER')
    if drone_server_url is None:
        print('Drone server environment variable not set')
        exit(1)

    drone_user_token = os.environ.get('DRONE_TOKEN')
    if drone_user_token is None:
        print('Drone authorization token not set, trying AWS')

        if "gitlab" in drone_server_url:
            drone_token = 'drone_private_token'
        else:
            drone_token = 'drone_public_token'

        try:
            print('Getting ' + drone_token + ' from AWS')
            drone_user_token = processAWSSecret(client, drone_token, 'list')
        except ClientError as e:
            print('Drone authorization token not found in AWS')
            exit(1)

    repo = os.environ.get('DRONE_REPO')
    if repo is None:
        print('DRONE_REPO is not set')
        exit(1)

    drone_secrets_url = drone_server_url + '/api/repos/' + repo + '/secrets'

    for secret in seed_list:
        if secret in global_exclusion_list:
            secret_key_name = secret
        else:
            secret_key_name = secret_env + '_' + secret
        
        try:
            secret_value = processAWSSecret(client, secret_key_name, 'list')
            if dry_run == 'N':
                updateDroneSecret(drone_secrets_url, drone_user_token, secret_key_name, secret_value)
            success_list.append(secret_key_name)
        except ClientError as e:
            error_list.append(secret_key_name + ' ' + e.response['Error']['Message'])

    print ('\n')

    if dry_run != 'N':
        print('\n**** No changes have been made, dry-run only ****\n')

    summaryStatus(success_list, error_list)
    if len(error_list) > 0:
        exit(1)

    exit(0)


if __name__ == "__main__":
    secrets_list_file = os.environ.get('DRONE_WORKSPACE') + '/env.yaml'

    parser = argparse.ArgumentParser(description='Secrets management')

    parser.add_argument('-l', '--auth', dest='authenticate', default='N', choices=['Y', 'N'], help='Authentication required Y/N, default N')
    parser.add_argument('-m', '--mfa', dest='mfa', help='MFA device id')
    parser.add_argument('-p', '--primaryaccount', dest='primaryaccount', help='HO primary account')
    parser.add_argument('-a', '--account', dest='account', help='AWS Account number')
    parser.add_argument('-n', '--rolename', dest='rolename', help='AWS role name')
    parser.add_argument('-d', '--dry-run', dest='dryrun', default='N', help='Only show secrets that would be updated in Drone, default N')

    args = parser.parse_args()

    # Validate yaml file
    if not validateFile(secrets_list_file):
        exit(1)

    # Get credentials
    if args.authenticate == "Y":
        role_arn = 'arn:aws:iam::' + args.account + ':' + args.rolename
        mfa_arn  = 'arn:aws:iam::' + args.primaryaccount + ':mfa/' + args.mfa
        client = getAssumeRoleCreds(role_arn, mfa_arn)
    else:
        client = getAWSSecretsManagerCreds('eu-west-2')

    processEnvSecrets(client, secrets_list_file, args.dryrun)
