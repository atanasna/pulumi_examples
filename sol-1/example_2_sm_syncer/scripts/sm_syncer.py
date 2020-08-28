import json
import boto3
import os

def main(event, context):
    return sync_secrets(event)

def sync_secrets(event):
    local_region = os.environ['AWS_REGION']
    remote_region = os.environ['remote_region']
    exceptions = os.environ['exceptions'].split(',')
    secret_id = event["detail"]["requestParameters"]["secretId"]

    if secret_id in exceptions:
        print(f"Secret-id {secret_id} is in the exceptions list and will not be synced")
        return {
            'statusCode': 403,
            'body': f"Secret-id {secret_id} is in the exceptions list and will not be synced" 
        }

    if not check_secret_availability(secret_id, local_region):
        return {
            'statusCode': 503,
            'body': f"Secret-id {secret_id} is unavailable in {local_region}" 
        }

    if not check_secret_availability(secret_id, remote_region):
        return {
            'statusCode': 503,
            'body': f"Secret-id {secret_id} is unavailable in {remote_region}" 
        }

    try:
        local_sm = boto3.client('secretsmanager', region_name=local_region)
        remote_sm = boto3.client('secretsmanager', region_name=remote_region)

        local_secret_value = local_sm.get_secret_value(SecretId=secret_id)['SecretString']
        remote_secret_value = remote_sm.get_secret_value(SecretId=secret_id)['SecretString']
        
        if local_secret_value != remote_secret_value:
            print(f"Secret {secret_id} is out of sync")
            remote_sm.put_secret_value(SecretId=secret_id,SecretString=local_secret_value)
            print(f"Synchronization complete!")
            return {
                'statusCode': 200,
                'body': f"Syncing of secret:{secret_id} completed!"
            }
        else:
            print(f"Secret {secret_id} is in sync, no need to resync")
            return {
                'statusCode': 200,
                'body': f"Secret:{secret_id} is already synced!"
            }

    except Exception as e: 
        return {
            'statusCode': 503,
            'body': e
        }
    
def check_secret_availability(secret_id, region):
    sm = boto3.client('secretsmanager', region_name=region)
    try:
        sm.describe_secret(SecretId=secret_id)
        print(f"Secret {secret_id} is available in {region}")
        return True
    except Exception as e: 
        print(f"Secret {secret_id} is NOT available in {region}")
        print(e)
        return False