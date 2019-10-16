import boto3


def getAssumeRoleCreds(role_arn, mfa_arn):
    sts_default_provider_chain = boto3.client('sts')
    
    # Prompt for MFA time-based one-time password (TOTP)
    mfa_TOTP = str(input("Enter the MFA code: "))
    
    response=sts_default_provider_chain.assume_role(
        RoleArn=role_arn,
        RoleSessionName='secrets_management',
        SerialNumber=mfa_arn,
        TokenCode=mfa_TOTP
    )
   
    creds = response['Credentials']

    print ('export AWS_ACCESS_KEY_ID=' + creds['AccessKeyId'])
    print ('export AWS_SECRET_ACCESS_KEY=' + creds['SecretAccessKey'])
    print ('export AWS_SESSION_TOKEN=' + creds['SessionToken'])

    return boto3.client('secretsmanager',
        aws_access_key_id=creds['AccessKeyId'],
        aws_secret_access_key=creds['SecretAccessKey'],
        aws_session_token=creds['SessionToken'],
)


def getAWSSecretsManagerCreds(region_name='eu-west-2'):
    session = boto3.session.Session()
    return session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
