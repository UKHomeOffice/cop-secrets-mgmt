#  aws_handler - This handles various aws functions

import base64
import boto3
import json
import logging
from botocore.exceptions import ClientError


class AWS(object):

    def __init__(self, data=None):
        self.data = data
        self.client = None

    def get_credentials(self):
        if self.data['aws']['authenticate']:
            self.client = self.get_assume_role_creds()
        else:
            self.client = self.get_secrets_manager_creds()

    def get_assume_role_creds(self):
        role_arn = self.data['aws']['role_arn']
        mfa_arn = self.data['aws']['mfa_arn']

        sts_default_provider_chain = boto3.client('sts')
        # Prompt for MFA time-based one-time password (TOTP)
        mfa_TOTP = str(input("Enter the MFA code: "))

        response = sts_default_provider_chain.assume_role(
            RoleArn=role_arn,
            RoleSessionName='secrets_management',
            SerialNumber=mfa_arn,
            TokenCode=mfa_TOTP
        )
        creds = response['Credentials']

        logging.warning(f"\nexport AWS_ACCESS_KEY_ID={creds['AccessKeyId']}"
                        f"\nexport AWS_SECRET_ACCESS_KEY={creds['SecretAccessKey']}"
                        f"\nexport AWS_SESSION_TOKEN={creds['SessionToken']}")

        return boto3.client('secretsmanager',
                            aws_access_key_id=creds['AccessKeyId'],
                            aws_secret_access_key=creds['SecretAccessKey'],
                            aws_session_token=creds['SessionToken'],
                            )

    def get_secrets_manager_creds(self):
        region = self.data['aws']['region']
        session = boto3.session.Session()
        return session.client(
            service_name='secretsmanager',
            region_name=region
        )

    def get_secret(self, secret=None):
        secret_data = {}
        secret_name = secret.lower()

        try:
            response = self.client.get_secret_value(SecretId=secret_name)
        except ClientError as list_e:
            if list_e.response['Error']['Code'] == 'DecryptionFailureException':
                logging.error('Secrets Manager cannot decrypt the protected secret text using the provided KMS key')
                exit(1)
            elif list_e.response['Error']['Code'] == 'AccessDeniedException':
                logging.error('Access Denied')
                exit(1)
            elif list_e.response['Error']['Code'] == 'ResourceNotFoundException':
                logging.warning(f'secret: {secret_name} not found :: skipping entry')
            else:
                raise list_e
        else:
            if 'SecretString' in response:
                secret = response['SecretString']
            else:
                secret = base64.b64decode(response['SecretBinary'])

        try:
            secret_data[secret_name] = json.loads(secret)
        except (TypeError, ValueError):
            secret_data[secret_name] = secret

        return secret_data

    def create_secret(self, name=None, secret_data=None):
        response = None
        if isinstance(secret_data, dict):
            secret_data = json.dumps(secret_data, indent=4)

        if not isinstance(secret_data, str):
            secret_data = str(secret_data)

        try:
            response = self.client.create_secret(
                Name=name,
                SecretString=secret_data
            )
        except ClientError as list_e:
            if list_e.response['Error']['Code'] == 'DecryptionFailureException':
                logging.error('Secrets Manager cannot decrypt the protected secret text using the provided KMS key')
                exit(1)
            elif list_e.response['Error']['Code'] == 'AccessDeniedException':
                logging.error('Access Denied')
                exit(1)
            elif list_e.response['Error']['Code'] == 'ResourceExistsException':
                logging.warning(f'secret: {name} already exists :: skipping entry')
            else:
                raise list_e

        return response

    def update_secret(self, secret=None):
        # ToDo: this code needs work - just copy / pasted from original
        # commented out for now
        return None
        # try:
        #    secret_name = secret[0].lower()
        #    secret_value = secret[1]
        #    get_response = self.client.get_secret_value(SecretId=secret_name)
        #    # We need to know when a secret is not unique when adding from another repo,
        #    # so we cannot blindly update, only update if the repo name is the same
        #    describe_response = self.client.describe_secret(SecretId=secret_name)
        #    if 'Description' in describe_response:
        #        if describe_response['Description'] == repo_name:
        #            put_response = self.client.put_secret_value(SecretId=secret_name, SecretString=secret_value)
        #        else:
        #            msg = 'Found non-unique secret for ' + repo_name + ', currently in use by ' + describe_response[
        #                'Description']
        #            raise Exception(msg)
        #    else:
        #        update_response = client.update_secret(SecretId=secret_name, SecretString=secret_value,
        #                                               Description=repo_name)
        # except ClientError as update_e:
        #    if update_e.response['Error']['Code'] == 'ResourceNotFoundException':
        #        try:
        #            create_response = client.create_secret(Name=secret_name, SecretString=secret_value,
        #                                                   Description=repo_name)
        #        except ClientError as create_e:
        #            raise create_e
        #    else:
        #        raise update_e
        # except Exception as general_e:
        #    raise general_e

    def delete_secret(self, secret=None):
        # ToDO: this code needs work - just copy / pasted from original
        # commented out for now
        return None
        # try:
        #    get_response = client.get_secret_value(SecretId=secret)
        #    delete_response = client.delete_secret(SecretId=secret)
        # except ClientError as remove_e:
        #    raise remove_e
        # else:
        #    return None
