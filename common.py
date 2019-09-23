#!/usr/bin/env python

import yaml

global_exclusion_list = ['api_form_aws_access_key_id', 'api_form_aws_secret_access_key', 'api_form_protocol', 'camunda_aws_access_key_id', 'camunda_aws_secret_access_key', 'cop_ops_sql_clients_aws_access_key_id', 'cop_ops_sql_clients_aws_secret_access_key', 'db_engine_protocol', 'db_ref_default_username', 'db_ref_governance_anon_username', 'db_ref_governance_authenticator_username', 'db_ref_governance_owner_username', 'db_ref_governance_readonly_username' , 'db_ref_governance_schema', 'db_ref_governance_service_username', 'db_ref_jdbc_options', 'db_ref_options', 'db_ref_port', 'db_ref_private_gitkey', 'db_ref_private_gitrepo', 'db_ref_protocol', 'db_ref_reference_anon_username', 'db_ref_reference_authenticator_username', 'db_ref_reference_dbname', 'db_ref_reference_owner_username', 'db_ref_reference_readonly_username', 'db_ref_reference_schema', 'db_ref_reference_service_username', 'doc_cop_aws_access_key_id', 'doc_cop_aws_secret_access_key', 'doc_training_aws_access_key_id', 'doc_training_aws_secret_access_key', 'docker_credentials', 'docker_password', 'docker_username', 'drone_private_token', 'drone_public_token', 'engine_protocol', 'executor_aws_access_key_id', 'executor_aws_secret_access_key', 'flyway_image', 'flyway_tag', 'formbuilder_aws_access_key_id', 'formbuilder_aws_secret_access_key', 'git_repo_private_giturl', 'git_repo_private_port', 'git_repo_private_url', 'nginx_image', 'nginx_tag', 'pdf_generator_aws_access_key_id', 'pdf_generator_aws_s3_endpoint', 'pdf_generator_aws_s3_port', 'pdf_generator_aws_s3_protocol', 'pdf_generator_aws_s3_region', 'pdf_generator_aws_secret_access_key', 'translation_private_key_path', 'postgres_image', 'postgres_tag', 'quay_password', 'quay_username', 'report_aws_access_key_id', 'report_aws_secret_access_key', 'slack_webhook', 'translation_image', 'translation_keycloak_client_id', 'translation_name', 'translation_port', 'translation_protocol', 'www_image', 'www_keycloak_access_role', 'www_keycloak_client_id', 'www_name', 'www_port', 'www_protocol', 'www_ui_protocol', 'www_ui_txt_protocol', 'www_ui_version']

env_exclusion_list = ['analytics_site_id', 'analytics_url', 'api_cop_port', 'api_cop_protocol', 'api_cop_url', 'api_form_url', 'api_ref_port', 'api_ref_protocol', 'api_ref_url', 'db_cop_hostname', 'db_cop_operation_authenticator_password', 'db_cop_operation_authenticator_username', 'db_cop_operation_dbname', 'db_cop_operation_schema', 'db_cop_options', 'db_cop_port', 'db_cop_protocol', 'db_ref_default_dbname', 'db_ref_default_password', 'db_ref_governance_authenticator_password', 'db_ref_governance_owner_password', 'db_ref_hostname', 'db_ref_reference_authenticator_password', 'db_ref_reference_owner_password', 'drone_aws_access_key_id', 'drone_aws_secret_access_key', 'engine_url', 'keycloak_protocol', 'keycloak_realm', 'keycloak_url', 'kube_server', 'kube_token', 'pdf_generator_aws_s3_access_key', 'pdf_generator_aws_s3_kms_key', 'pdf_generator_aws_s3_pdf_bucketname', 'pdf_generator_aws_s3_secret_key', 'redis_port', 'redis_ssl', 'redis_token', 'redis_url', 'report_protocol', 'report_url', 'translation_url', 'whitelist', 'www_ui_environment', 'www_url']

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
