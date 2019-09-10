# cop-secrets

This is being developed by the UK Home Office and is used to store the configuration and scripts required to securely store secrets in AWS Secret Manager and sync Drone with the required secrets per repository during builds and deployments.

# Requirements

* AWS credentials
* Drone credentials
* Python3

# Usage

To use cop-secrets, first clone this repo

```
git@github.com:UKHomeOffice/cop-secrets.git
```

## Development with Docker
Once you've cloned the project, build the cop-secrets Docker container

```sh
docker build -t cop-secrets .
```

To run the resulting Docker container:

```sh
docker run cop-secrets
```

## Secret Management

### Application repo

Your repository must contain an env.yaml file otherwise this will cause your build to fail.

Add all the variables your application needs, see the manifest repo local.yml for structure and an example.
Additionally you will need these variables
```
keys:
  - drone:
      aws_access_key_id
      aws_secret_access_key
      public_token  or   private_token
```

In the `.drone.yml` file, add this snippet to the beginning of the pipeline, changing the private or public url for gitlab/github
```
  synch_dev_secrets:
    image: quay.io/ukhomeofficedigital/cop-secrets
    environment:
      - DRONE_SERVER=https://drone-gitlab.acp.homeoffice.gov.uk
    secrets:
      - source: DEV_DRONE_AWS_ACCESS_KEY_ID
        target: AWS_ACCESS_KEY_ID
      - source: DEV_DRONE_AWS_SECRET_ACCESS_KEY
        target: AWS_SECRET_ACCESS_KEY
      - source: DRONE_PRIVATE_TOKEN
        target: DRONE_TOKEN
    when:
      event: push

  synch_staging_secrets:
    image: quay.io/ukhomeofficedigital/cop-secrets
    environment:
      - DRONE_SERVER=https://drone-gitlab.acp.homeoffice.gov.uk
    secrets:
      - source: STAGING_DRONE_AWS_ACCESS_KEY_ID
        target: AWS_ACCESS_KEY_ID
      - source: STAGING_DRONE_AWS_SECRET_ACCESS_KEY
        target: AWS_SECRET_ACCESS_KEY
      - source: DRONE_PRIVATE_TOKEN
        target: DRONE_TOKEN
    when:
      event: deployment
      environment: staging

  synch_production_secrets:
    image: quay.io/ukhomeofficedigital/cop-secrets
    environment:
      - DRONE_SERVER=https://drone-gitlab.acp.homeoffice.gov.uk
    secrets:
      - source: PRODUCTION_DRONE_AWS_ACCESS_KEY_ID
        target: AWS_ACCESS_KEY_ID
      - source: PRODUCTION_DRONE_AWS_SECRET_ACCESS_KEY
        target: AWS_SECRET_ACCESS_KEY
      - source: DRONE_PRIVATE_TOKEN
        target: DRONE_TOKEN
    when:
      event: deployment
      environment: production
```

You will need to do the manifest repo and cop-secrets repo steps before you can push this change.


### Manifest repo

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

This will create a `drone_vars.envfile` with local dummy values. Make a copy of this file called `seed_drone.envfile` and remove all the variables apart from the following, and also remove the *DEV_* prefix from the drone token variable name. Change the dummy values to dev values.
  - drone_aws_access_key_id
  - drone_aws_secret_access_key
  - drone_private_token or drone_public_token

In order to sync secrets the Drone and AWS, credentials need to be in Drone, which you will write to from your laptop using your credentials. Ensure your `DRONE_SERVER` and `DRONE_TOKEN` environment variables are set:
```
./bin/drone.py -f seed_drone.envfile -r <reponame>
```

Repeat above changing the `seed_drone.envfile` with staging and production values, and changing *DEV_* to *STAGING_* and *PRODUCTION_*.

If you are happy with what you see in `drone_vars.envfile`, you basically need to make a `dev`, `staging` and `prod` version of the `local.yml` with the correct passwords. To update each environment, do:
```
./bin/env.py -f dev.yml -s <your_repo_path>/env.yaml -d -p dev -o dev_drone_vars.envfile
./bin/env.py -f staging.yml -s <your_repo_path>/env.yaml -d -p staging -o staging_drone_vars.envfile
./bin/env.py -f prod.yml -s <your_repo_path>/env.yaml -d -p prod -o prod_drone_vars.envfile
```

Deactivate the virtualenv
```
deactivate
```

### cop-secrets repo

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

Your `~/.aws/credentials` file must have a *[default]* stanza with your HO Main account access key id and secret access key.

#### Uploading
```
./upload_secrets.py -l Y -m <your_digital_email> -f ../../gitlab/manifest/drone_vars.envfile -e notprod -r <repo_name>
```

If you were successfully authenticated you can then export the AWS credentials that it prints out as these will be valid for an hour and you will not need to login if uploading more secrets. Uploading secrets without logging in:
```
./upload_secrets.py -f ../../gitlab/manifest/drone_vars.envfile -e notprod -r <repo_name>
```

If you are uploading to staging or production, you will need to specify `-e prod` and re-authenticate as the script defaults to the non prod account when assuming your role.

#### Changing secrets

##### Using AWS CLI
See [AWS account information](https://gitlab.digital.homeoffice.gov.uk/cop/cop-docs/blob/master/source/documentation/overview/cop_guide.md) for connecting using MFA and assuming a role into nonprod and prod AWS accounts.

Get secret value
```
aws secretsmanager get-secret-value --secret-id=<secret_name>
aws secretsmanager describe-secret --secret-id=<secret_name>
```

When updating or creating secrets, ensure the description field is populated with the following
- Global (if the same secret is used across accounts and environments
- DEV|STAGING|PRODUCTION Environment (if the same secret is used across the environment, i.e. STAGING Environment)
- <Repo-name> (if the secret is specific to a repo, i.e. cop/cop-vault)

Update secret value
```
aws secretsmanager update-secret --secret-id=<secret_name> --description=<repo-name> --secret-string=<secret_value>
```
Create secret value
```
aws secretsmanager create-secret --name=<secret_name> --description=<repo-name> --secret-string=<secret_value>
```

##### Using python

Manufacture an envfile and then run the python script as normal
```
./upload_secrets.py -f <env file> -r <repo_name> -l Y -m <digital_email> -p <primary AWS account> -a <assume role account> -n <role/role_name>
```
