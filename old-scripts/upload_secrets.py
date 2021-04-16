#!/usr/bin/env python3

from common import *
from secrets import *


def uploadSecrets(client, src_file, repo_name, dry_run):
  error_list = []
  success_list = []

  data = open(src_file, 'r').readlines()
  for keypair in data:
    secret = keypair.rstrip('\n').split('=',1)

    check_exclusion = secret[0].split('_',1)
    if check_exclusion[1].lower() in global_exclusion_list:
        secret[0] = check_exclusion[1]
        description_repo_name = 'Global'
    elif check_exclusion[1].lower() in env_exclusion_list:
        description_repo_name = check_exclusion[0] + ' Environment'
    else:
        description_repo_name = repo_name

    try:
        if dry_run == 'N':
            response = processAWSSecret(client, secret, 'update', description_repo_name)
        else:
            response = ''

    except ClientError as e:
        error_list.append(secret[0]+ ' ' + e.response['Error']['Message'])
    except Exception as general_e:
        error_list.append(secret[0]+ ' ' + str(general_e))
    else:
        success_list.append(secret[0]+ ' ' + response)

  if dry_run != 'N':
     print('\n**** No changes have been made, dry-run only ****\n')

  summaryStatus(success_list, error_list)


if __name__ == "__main__":
    parser = getUserParser()
    
    parser.add_argument('-f', '--file', dest='src_file', required=True, help='Yaml file with secret key value pairs')
    parser.add_argument('-r', '--repo', dest='repo_name', required=True, help='Name of the repo to which the secrets belong')
    parser.add_argument('-d', '--dry-run', dest='dryrun', default='N', help='Only show secrets that would be updated in AWS , default N')
    
    args = parser.parse_args()

    # Get credentials
    client = getCredentials(args)

    uploadSecrets(client, args.src_file, args.repo_name, args.dryrun)
