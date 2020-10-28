#!/usr/bin/env python

from common import *
from secrets import *


def check_version():
    version = os.environ.get('DRONE_VERSION')
    print("Checking Drone Version: {}".format(version))
    try:
        version = version.split('v')[-1]
        version = int(version.split('.')[0])
    except ValueError:
        print("Error: Drone version: {}, is not a recognised version, defaulting to Drone v0 payload".format(version))
        return "v0"
    if version >= 1:
        print("Drone version: {}, Using Drone v1 Payload".format(version))
        return "v1"
    print("Drone version: {}, Using Drone v0 payload  (Original Method)".format(version))
    return "v0"

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

    drone_version = check_version()

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
            if dry_run != 'N':
                success_list.append('Dry run ' + secret_key_name)
            else:
                updateDroneSecret(drone_secrets_url, drone_user_token, drone_version, secret_key_name, secret_value)
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
    parser = getUserParser()
    parser.add_argument('-d', '--dry-run', dest='dryrun', default='N', help='Only show secrets that would be updated in Drone, default N')
    args = parser.parse_args()

    secrets_list_file = os.environ.get('DRONE_WORKSPACE') + '/env.yaml'

    # Validate yaml file
    if not validateFile(secrets_list_file):
        exit(1)

    # Get credentials
    client = getCredentials(args)

    processEnvSecrets(client, secrets_list_file, args.dryrun)
