#!/usr/bin/env python3

import base64
import requests
from botocore.exceptions import ClientError


def processAWSSecret(client, secret, action, repo_name=''):
    if action == 'list':
        secret = secret.lower()
        try:
            get_response = client.get_secret_value(SecretId=secret)
            if 'SecretString' in get_response:
                return get_response['SecretString']
            else:
                return base64.b64decode(get_response['SecretBinary'])
        except ClientError as list_e:
            if list_e.response['Error']['Code'] == 'DecryptionFailureException':
                print('Secrets Manager cannot decrypt the protected secret text using the provided KMS key')
                exit(1)
            elif list_e.response['Error']['Code'] == 'AccessDeniedException':
                print('Access Denied')
                exit(1)
            else:
                raise list_e

    elif action == 'remove':
        try:
            get_response = client.get_secret_value(SecretId=secret)
            delete_response = client.delete_secret(SecretId=secret)
        except ClientError as remove_e:
            raise remove_e
        else:
            return ""

    elif action == 'update':
        try:
            secret_name = secret[0].lower()
            secret_value = secret[1]
            get_response = client.get_secret_value(SecretId=secret_name)
            #We need to know when a secret is not unique when adding from another repo,
            #so we cannot blindly update, only update if the repo name is the same
            describe_response = client.describe_secret(SecretId=secret_name)
            if 'Description' in describe_response:
                if describe_response['Description'] == repo_name:
                    put_response = client.put_secret_value(SecretId=secret_name, SecretString=secret_value)
                else:
                    msg='Found non-unique secret for ' + repo_name + ', currently in use by ' + describe_response['Description']
                    raise Exception(msg)
            else:
                update_response = client.update_secret(SecretId=secret_name, SecretString=secret_value, Description=repo_name)
        except ClientError as update_e:
            if update_e.response['Error']['Code'] == 'ResourceNotFoundException':
                try:
                    create_response = client.create_secret(Name=secret_name, SecretString=secret_value, Description=repo_name)
                except ClientError as create_e:
                    raise create_e
            else:
                raise update_e
        except Exception as general_e:
            raise general_e

        return ""


def updateDroneSecret(drone_url, drone_token, secret_key, secret_value):
    header_str = {'Authorization': "Bearer " + drone_token}

    try:
        get_response = requests.request("GET", drone_url + '/' + secret_key, headers=header_str)

        if get_response.status_code == 200:
            print('**Deleting** ' + secret_key)
            response = requests.delete(drone_url + '/' + secret_key, headers=header_str)
            if response.status_code != 204:
               raise Exception(str(response.status_code) + ' ' + response.text)

        # Create secret
        if get_response.status_code == 401:
            raise Exception('**Access denied** Please check the drone credentials for ' + drone_url + '/' + secret_key)

        print(secret_key + ' does not exist, adding')
        payload = {'name': "" + secret_key, 'value': "" + secret_value, 'event': ['push','tag','deployment']}
        response = requests.post(drone_url, json=payload, headers=header_str)

        if response.status_code != 200:
           raise Exception(str(response.status_code) + ' ' + response.text)

    except Exception as droneError:
        raise(droneError)

    return
