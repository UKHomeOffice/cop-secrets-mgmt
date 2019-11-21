# cop-secrets

This is being developed by the UK Home Office and is used to store the configuration and scripts required to securely store secrets in AWS Secret Manager and sync Drone with the required secrets per repository during builds and deployments.

# Requirements

* AWS credentials, aws cli
* Drone credentials
* Python3, virtualenv

# Usage

To use cop-secrets, first clone this repo

```
git@github.com:UKHomeOffice/cop-secrets.git
```

# Drone secrets

Name|Example value
---|---
docker_password|xxx (Global for all repositories and environments)
docker_username|docker (Global for all repositories and environments)

## Secret Management

### Tools

Install brew on Mac

```
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```

Use brew to install aws cli
```
brew install awscli
```

Install virtual environment

```
pip install virtualenv
```

### Existing application repositories

We will add a new `TEST_APP_NEWITEM` variable and update the existing `TEST_APP_ITEM` secret for purposes of detailing the steps required.

1. Update your repository `env.yaml` with any new environment variables, in alphabetical order.

```
  - test:
      app:
        item
        newitem
```

2. Update your `.drone.yaml` with any new environment variables, in alphabetical order. Repeat similarly for staging and production, where applicable.

```
  deploy_to_dev:
    ...
    secrets:
      - source: DEV_TEST_APP_ITEM
        target: TEST_APP_ITEM
      - source: DEV_TEST_APP_NEWITEM
        target: TEST_APP_NEWITEM
```

3. Change into your cop-secrets repo directory and create/use your virtualenv. See [Create a virtual environment](#cop-secrets-repo). Make sure you unset all AWS credentials.

4. Create a `dev.yml` file which we will use to upload to AWS Secrets Manager with the changes to the secrets to the non prod AWS account.

```
dev_test_app_item=fireworks
dev_test_app_newitem=sparklers
```

5. Create a `prod.yml` file which we will use to upload to AWS Secrets Manager with the changes to the secrets to the prod AWS account.

```
staging_test_app_item=candles
staging_test_app_newitem=yankee
production_test_app_item=chocolate
production_test_app_newitem=snickers
```

6. Upload secrets to the dev AWS account.

You may also need to export your AWS_PROFILE name if you do not have a `default` stanza. See [AWS](https://doc.dev.cop.homeoffice.gov.uk/technical.html#aws) for help on setting up your credentials file. Remove the dry run option `-d Y` to update AWS.

```
export AWS_PROFILE=<your profile name>
./upload_secrets.py -f dev.yml -r <repo_name> -l Y -m <digital_email> -p <primary AWS account> -a <assume role account> -n <role/role_name> -d Y
```

7. Upload secrets to the prod account, remove the dry run option `-d Y` to update AWS.

```
./upload_secrets.py -f prod.yml -r <repo_name> -l Y -m <digital_email> -p <primary AWS account> -a <assume role account> -n <role/role_name> -d Y
```

8. Deactivate your cop-secrets virtualenv.

```
deactivate
```

9. Update drone variables

Export the `DRONE_SERVER` and `DRONE_TOKEN` environment variables from `https://drone-gitlab.acp.homeoffice.gov.uk/account/token` for gitlab repositories, and `https://drone.acp.homeoffice.gov.uk/account/token` for github repositories. Find the last master build number for your repository in Drone

```
drone deploy <repo-name> <build-number> secrets
```

10. Update local environment setup

In order to maintain a working local environment, change into the manifest repository and add the new environment variables to the `docker-compose.yml` and `local.yml` even if you do not use docker-compose. This is to ensure those who do, have all the correct settings for running the application locally.

#### Viewing secrets

##### AWS CLI

Various aws cli commands for viewing secrets quickly.

```
aws secretsmanager list-secrets --query 'SecretList[?Description==`Global`].Name'
aws secretsmanager list-secrets --query 'SecretList[?Description==`DEV Environment`].Name'
aws secretsmanager list-secrets --query 'SecretList[?Description==`UKHomeOffice/ref-data-api`].Name'

aws secretsmanager get-secret-value --secret-id=xxx

for mysecret in $(aws secretsmanager list-secrets  --query 'SecretList[?Description==`Global`].[Name]' --output text); do aws secretsmanager get-secret-value --secret-id=$mysecret --query '[Name,SecretString]' --output text; done
```

##### Python

Export the environment and path to the repo containing the env.file for which we are going to query AWS and then display the list of secrets and values
```
export DRONE_WORKSPACE=path_to_env_file
export DEPLOY_ENV=dev|staging|production

./repo_secrets.py -l Y/N -m email@digital.homeoffice.gov.uk -p <primary AWS account> -a <assume role account> -n <role/role_name>
e.g. ./repo_secrets.py -l YN -m john.doe@digital.homeoffice.gov.uk -p 123456 -a 789012 -n role/myrole
```

### Setting up new application repositories

1. List of variables

Your repository must contain an `env.yaml` file otherwise this will cause your build to fail.

Add all the variables your application needs to `env.yaml`, see the manifest repository `local.yml` for structure and an example.
Additionally you will need these variables. Use the private token when using gitlab repos, the public token when using github projects.
```
keys:
  - drone:
      aws_access_key_id
      aws_secret_access_key
      public_token  or   private_token
  - slack:
      webhook
```

2. Configure synch steps in Drone

In the `.drone.yml` file, add this snippet to the beginning of the pipeline, changing the private or public url for gitlab/github and PRIVATE/PUBLIC token depending on whether it builds on drone private/public.
```
  synch_dev_secrets:
    image: quay.io/ukhomeofficedigital/cop-secrets
    environment:
      - DRONE_SERVER=https://drone-gitlab.acp.homeoffice.gov.uk
      - DEPLOY_ENV=dev
    secrets:
      - source: DEV_DRONE_AWS_ACCESS_KEY_ID
        target: AWS_ACCESS_KEY_ID
      - source: DEV_DRONE_AWS_SECRET_ACCESS_KEY
        target: AWS_SECRET_ACCESS_KEY
      - source: DRONE_PRIVATE_TOKEN
        target: DRONE_TOKEN
    when:
      environment: secrets
      event: deployment

  synch_staging_secrets:
    image: quay.io/ukhomeofficedigital/cop-secrets
    environment:
      - DRONE_SERVER=https://drone-gitlab.acp.homeoffice.gov.uk
      - DEPLOY_ENV=staging
    secrets:
      - source: STAGING_DRONE_AWS_ACCESS_KEY_ID
        target: AWS_ACCESS_KEY_ID
      - source: STAGING_DRONE_AWS_SECRET_ACCESS_KEY
        target: AWS_SECRET_ACCESS_KEY
      - source: DRONE_PRIVATE_TOKEN
        target: DRONE_TOKEN
    when:
      environment: secrets
      event: deployment

  synch_production_secrets:
    image: quay.io/ukhomeofficedigital/cop-secrets
    environment:
      - DRONE_SERVER=https://drone-gitlab.acp.homeoffice.gov.uk
      - DEPLOY_ENV=production
    secrets:
      - source: PRODUCTION_DRONE_AWS_ACCESS_KEY_ID
        target: AWS_ACCESS_KEY_ID
      - source: PRODUCTION_DRONE_AWS_SECRET_ACCESS_KEY
        target: AWS_SECRET_ACCESS_KEY
      - source: DRONE_PRIVATE_TOKEN
        target: DRONE_TOKEN
    when:
      environment: secrets
      event: deployment
```

3. Manifest repo

Add the new environment variables to the `docker-compose.yml` and `local.yml`

Create a virtual environment
```
virtualenv manifest_venv
source manifest_venv/bin/activate
pip install -r requirements.txt
```

Run a test to see what will get populated for your repo
```
./bin/env.py -f local.yml -s <your_repo_path>/env.yaml -d -p dev
```

This will create a `drone_vars.envfile` with local dummy values.

Run with dev secrets
```
./bin/env.py -f <dev_secrets.yml> -s <your_repo_path>/env.yaml -d -p dev -o dev_seed_drone.envfile
```

Remove all the variables apart from the following, and also remove the *DEV_* prefix from the drone token and slack variable names, for example:
```
drone_public_token=thisismysecretvalue   or drone_private_token=thisismysecretvalue
slack_webhook=https://wowwheredoesthisgo
dev_drone_aws_access_key_id=myawsaccesskeyid
dev_drone_aws_secret_access_key=myawssecretaccesskey
```

In order to sync secrets the Drone and AWS, credentials need to be in Drone, which you will write to from your laptop using your credentials. Ensure your `DRONE_SERVER` and `DRONE_TOKEN` environment variables are set. These can be found in the token page of drone:
```
export DRONE_SERVER=blah
export DRONE_TOKEN=blah
./bin/drone.py -f seed_drone.envfile -r <reponame>
e.g. ./bin/drone.py -f dev_seed_drone.envfile -r UKHomeOffice/cop-example-repo
```

Run with staging secrets
```
./bin/env.py -f <staging_secrets.yml> -s <your_repo_path>/env.yaml -d -p staging -o staging_seed_drone.envfile
```

Repeat removal of all variables from the dev step above, and remove the *STAGING_* prefix from the drone token and slack variable names.
```
e.g. ./bin/drone.py -f staging_seed_drone.envfile -r UKHomeOffice/cop-example-repo
```

Run with production secrets
```
./bin/env.py -f <production_secrets.yml> -s <your_repo_path>/env.yaml -d -p production -o production_seed_drone.envfile
```

Repeat removal of all variables from the dev step above, and remove the *PRODUCTION_* prefix from the drone token and slack variable names.
```
e.g. ./bin/drone.py -f production_seed_drone.envfile -r UKHomeOffice/cop-example-repo
```

To create the files for uploading the secrets to AWS in step 4, do the following:
```
./bin/env.py -f dev.yml -s <your_repo_path>/env.yaml -d -p dev -o dev_drone_vars.envfile
./bin/env.py -f staging.yml -s <your_repo_path>/env.yaml -d -p staging -o staging_drone_vars.envfile
./bin/env.py -f prod.yml -s <your_repo_path>/env.yaml -d -p prod -o prod_drone_vars.envfile
```

Deactivate the virtualenv
```
deactivate
```

Clean up
```
rm -f *seed_drone.envfile
```

4. cop-secrets repo

Create a virtual environment
```
virtualenv secrets_venv
source secrets_venv/bin/activate
pip install -r requirements.txt
```

Make sure your AWS credentials are unset in your environment
```
unset AWS_SESSION_TOKEN
unset AWS_SECRET_ACCESS_KEY
unset AWS_ACCESS_KEY_ID
```

You may also need to export your AWS_PROFILE name if you do not have a `default` stanza. See [AWS](https://doc.dev.cop.homeoffice.gov.uk/technical.html#aws) for help on setting up your credentials file.

Upload to AWS Secrets Manager Dev
```
export AWS_PROFILE=<your profile name>
./upload_secrets.py -f <env file> -r <repo_name> -l Y -m <digital_email> -p <primary AWS account> -a <assume role account> -n <role/role_name>
e.g. ./upload_secrets.py -f ../manifest/dev_drone_vars.envfile -r UKHomeOffice/cop-example-repo -l Y -m john.doe@digital.homeoffice.gov.uk -p 123456789 -a 111111111 -n role/myrolename
```

Upload to AWS Secrets Manager Staging
```
export AWS_PROFILE=<your profile name>
./upload_secrets.py -f <env file> -r <repo_name> -l Y -m <digital_email> -p <primary AWS account> -a <assume role account> -n <role/role_name>
e.g. ./upload_secrets.py -f ../manifest/staging_drone_vars.envfile -r UKHomeOffice/cop-example-repo -l Y -m john.doe@digital.homeoffice.gov.uk -p 123456789 -a 222222222 -n role/myrolename
```

Upload to AWS Secrets Manager Production
```
export AWS_PROFILE=<your profile name>
./upload_secrets.py -f <env file> -r <repo_name> -l Y -m <digital_email> -p <primary AWS account> -a <assume role account> -n <role/role_name>
e.g. ./upload_secrets.py -f ../manifest/production_drone_vars.envfile -r UKHomeOffice/cop-example-repo -l Y -m john.doe@digital.homeoffice.gov.uk -p 123456789 -a 222222222 -n role/myrolename
```

Update drone variables

Export the `DRONE_SERVER` and `DRONE_TOKEN` environment variables from `https://drone-gitlab.acp.homeoffice.gov.uk/account/token` for gitlab repositories, and `https://drone.acp.homeoffice.gov.uk/account/token` for github repositories. Find the last master build number for your repository in Drone

```
drone deploy <repo-name> <build-number> secrets
```

Clean up
```
cd <manifest repo directory>
rm -f *drone_vars.envfile
```
