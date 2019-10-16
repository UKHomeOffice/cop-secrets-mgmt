#!/usr/bin/env python

from common import *
from secrets import *


def listRepoSecrets(client, src_file):
    with open(src_file, 'r') as seed_stream:
        seed_data = yaml.safe_load(seed_stream)
        seed_list = flatten_seed(seed_data)

    error_list = []
    secret_list = []

    secret_env = os.environ.get('DEPLOY_ENV')
    if secret_env is None:
        secret_env = os.environ.get('DRONE_DEPLOY_TO')
        if secret_env is None:
            secret_env = 'dev'

    for secret in seed_list:
        if secret in global_exclusion_list:
            secret_key_name = secret
        else:
            secret_key_name = secret_env + '_' + secret
        
        try:
            secret_value = processAWSSecret(client, secret_key_name, 'list')
            secret_list.append(secret_key_name + '=' + secret_value)
         
        except ClientError as e:
            error_list.append(secret_key_name + ' ' + e.response['Error']['Message'])

    print ('\n')

    summaryStatus(secret_list, error_list)
    exit(0)


if __name__ == "__main__":
    secrets_list_file = os.environ.get('DRONE_WORKSPACE') + '/env.yaml'

    parser = getUserParser()
    args = parser.parse_args()

    # Validate yaml file
    if not validateFile(secrets_list_file):
        exit(1)

    # Get credentials
    client = getCredentials(args)

    listRepoSecrets(client, secrets_list_file)
