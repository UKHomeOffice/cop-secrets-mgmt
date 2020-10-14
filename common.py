#!/usr/bin/env python

import argparse
import os
import yaml
from credentials import *


global_exclusion_list = ['accept_test_aws_access_key_id', 'accept_test_aws_secret_access_key', 'accept_test_cypress_auth_client_id', 'accept_test_cypress_db_user', 'accept_test_cypress_delegate_ui_user', 'accept_test_cypress_integrity_lead_ui_user', 'accept_test_cypress_line_manager2_ui_user', 'accept_test_cypress_line_manager_ui_user', 'accept_test_cypress_mandec_ui_user', 'accept_test_cypress_new_ui_user', 'accept_test_cypress_oar_ui_user',  'accept_test_cypress_profile_manager_ui_user', 'accept_test_cypress_ref_data_client', 'accept_test_cypress_refdata_user', 'accept_test_cypress_ui_user', 'accept_test_image', 'accept_test_name', 'api_cop_image', 'api_cop_port', 'api_form_aws_access_key_id', 'api_form_aws_secret_access_key', 'aws_region', 'camunda_aws_access_key_id', 'camunda_aws_secret_access_key', 'cbp_heartbeat_aws_access_key_id', 'cbp_heartbeat_aws_secret_access_key', 'cbp_heartbeat_image', 'cbp_heartbeat_name', 'cfssl_sidekick_image', 'cfssl_sidekick_tag', 'cop_prototype_aws_access_key_id', 'cop_prototype_aws_secret_access_key', 'cop_tools_aws_access_key_id', 'cop_tools_aws_secret_access_key', 'cop_ui_image', 'cop_ui_name', 'db_cop_port', 'db_ref_default_username', 'db_ref_governance_anon_username', 'db_ref_governance_authenticator_username', 'db_ref_governance_owner_username', 'db_ref_governance_readonly_username', 'db_ref_governance_schema', 'db_ref_governance_service_username', 'db_ref_jdbc_options', 'db_ref_options', 'db_ref_port', 'db_ref_private_gitkey', 'db_ref_private_gitrepo', 'db_ref_reference_anon_username', 'db_ref_reference_authenticator_username', 'db_ref_reference_dbname', 'db_ref_reference_owner_username', 'db_ref_reference_readonly_username', 'db_ref_reference_schema', 'db_ref_reference_service_username', 'doc_cop_aws_access_key_id', 'doc_cop_aws_secret_access_key', 'doc_training_aws_access_key_id', 'doc_training_aws_secret_access_key', 'docker_credentials', 'docker_password', 'docker_username', 'drone_private_token', 'drone_public_token', 'engine_port', 'executor_aws_access_key_id', 'executor_aws_secret_access_key', 'file_upload_service_keycloak_client_id', 'file_upload_service_name', 'file_upload_service_port', 'flyway_image', 'flyway_tag', 'formbuilder_aws_access_key_id', 'formbuilder_aws_secret_access_key', 'git_repo_private_giturl', 'git_repo_private_port', 'git_repo_private_url', 'ide_prototype_aws_access_key_id', 'ide_prototype_aws_secret_access_key', 'jira_db_host_port', 'jira_db_user', 'keycloak_gatekeeper_image', 'keycloak_gatekeeper_tag', 'log_level_debug', 'log_level_info', 'nginx_image', 'nginx_tag', 'pdf_generator_aws_access_key_id', 'pdf_generator_aws_s3_endpoint', 'pdf_generator_aws_s3_port', 'pdf_generator_aws_s3_region', 'pdf_generator_aws_secret_access_key', 'perf_test_aws_access_key_id', 'perf_test_aws_secret_access_key', 'postgres_image', 'postgres_tag', 'protocol_awbs', 'protocol_https', 'protocol_jdbc', 'protocol_postgres', 'prototype_keycloak_client_id', 'quay_password', 'quay_username', 'report_aws_access_key_id', 'report_aws_secret_access_key', 'sgmr_cbp_integration_aws_access_key_id', 'sgmr_cbp_integration_aws_secret_access_key', 'sgmr_cbp_integration_image', 'sgmr_cbp_integration_name', 'sgmr_cbp_integration_port', 'sgmr_data_api_aws_access_key_id', 'sgmr_data_api_aws_secret_access_key', 'sgmr_data_api_image', 'sgmr_data_api_name', 'sgmr_data_api_port', 'sgar_prototype_aws_access_key_id', 'sgar_prototype_aws_secret_access_key', 'sgmr_prototype_aws_access_key_id', 'sgmr_prototype_aws_secret_access_key', 'sgmr_prototype_docker_repo', 'sgmr_prototype_keycloak_client_id', 'sgmr_service_image', 'sgmr_service_name', 'sgmr_service_port', 'slack_webhook', 'tests_report_base_url', 'tests_s3_access_key', 'tests_s3_bucket_name', 'tests_s3_kms_key_id', 'tests_s3_secret_key', 'tests_slack_webhook', 'workflow_service_image', 'workflow_service_name', 'workflow_ui_image', 'workflow_ui_name', 'www_image', 'www_keycloak_access_role', 'www_keycloak_client_id', 'www_name', 'www_port', 'www_ref_image', 'www_ref_keycloak_client_id', 'www_ref_name', 'www_ref_port', 'www_ui_version']

env_exclusion_list = ['analytics_site_id', 'analytics_url', 'api_cop_url', 'api_form_url', 'api_ref_port', 'api_ref_url', 'bucket_name_prefix', 'cawemo_api_server_host', 'cawemo_garufa_host', 'cawemo_pusher_secret','cbp_username', 'cbp_password', 'cbp_endpoint','db_cop_hostname', 'db_cop_operation_authenticator_password', 'db_cop_operation_authenticator_username', 'db_cop_operation_dbname', 'db_cop_operation_schema', 'db_cop_options', 'db_cop_port', 'db_engine_default_dbname', 'db_engine_default_password', 'db_engine_default_username', 'db_engine_driver', 'db_engine_hostname', 'db_engine_jdbc_options', 'db_engine_options', 'db_engine_type', 'db_engine_port', 'db_ref_default_dbname', 'db_ref_default_password', 'db_ref_governance_authenticator_password', 'db_ref_governance_owner_password', 'db_ref_hostname', 'db_ref_reference_authenticator_password', 'db_ref_reference_owner_password', 'drone_aws_access_key_id', 'drone_aws_secret_access_key', 'engine_url', 'environment', 'file_upload_service_aws_access_key', 'file_upload_service_aws_secret_access_key', 'file_upload_service_aws_sse_kms_key_id', 'file_upload_service_aws_s3_bucket', 'file_upload_service_url', 'fincore_xml_namespace', 'gov_notify_api_key', 'gov_notify_notification_email_template_id', 'gov_notify_notification_sms_template_id', 'keycloak_realm', 'keycloak_url', 'kube_namespace_cop_ops', 'kube_namespace_cop_prototype', 'kube_namespace_cop_sgmr', 'kube_namespace_private_cop', 'kube_namespace_public_cop', 'kube_namespace_refdata', 'kube_server', 'kube_token', 'pdf_generator_aws_s3_access_key', 'pdf_generator_aws_s3_kms_key', 'pdf_generator_aws_s3_pdf_bucketname', 'pdf_generator_aws_s3_secret_key', 'prototype_keycloak_client_secret', 'prototype_keycloak_encryption_key', 'prototype_kube_token', 'redis_port', 'redis_ssl', 'redis_token', 'redis_url', 'report_url', 'sgmr_cbp_integration_url', 'sgmr_data_api_url', 'sgmr_kube_token', 'sgmr_prototype_url', 'sgmr_service_url', 's3_aws_access_key_id', 's3_aws_secret_access_key', 'whitelist', 'workflow_service_url', 'www_ref_read_only_mode', 'www_ref_url', 'www_ui_environment', 'www_url']


def getCredentials(args):
    if args.authenticate == "Y":
        role_arn = 'arn:aws:iam::' + args.account + ':' + args.rolename
        mfa_arn  = 'arn:aws:iam::' + args.primaryaccount + ':mfa/' + args.mfa
        client = getAssumeRoleCreds(role_arn, mfa_arn)
    else:
        client = getAWSSecretsManagerCreds('eu-west-2')

    return client


def getUserParser():
    parser = argparse.ArgumentParser(description='Secrets management')

    parser.add_argument('-l', '--auth', dest='authenticate', default='N', choices=['Y', 'N'], help='Authentication required Y/N, default N')
    parser.add_argument('-m', '--mfa', dest='mfa', help='MFA device id')
    parser.add_argument('-p', '--primaryaccount', dest='primaryaccount', help='HO primary account')
    parser.add_argument('-a', '--account', dest='account', help='AWS Account number')
    parser.add_argument('-n', '--rolename', dest='rolename', help='AWS role name')

    return parser


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


def summaryStatus(success_list, error_list):
    print ('Successful secrets')
    print ('------------------')
    for success_item in success_list:
        print(success_item)

    print ('\n\nUnsuccessful secrets')
    print ('--------------------')
    for error_item in error_list:
        print(error_item)


def validateFile(src_file):
    try:
        data = yaml.safe_load(open(src_file))
        return True
    except yaml.YAMLError as e:
        print(e)
        return False


def validateArgs(arguments):
    # TODO
    # if logging in, mfa needs to be supplied
    # if update, service, env_deploy needs to be supplied
    return True
