import boto3
from botocore.exceptions import ClientError
import json
import logging

# Get current account ID
accountId = boto3.client('sts').get_caller_identity().get('Account')
allowedArn = "arn:aws:::851725350401:*"

# Define Bucket and log file
# logFile = input("Enter Log file name: ")
logFile = "sqs-logs.txt"
bucketName = "python-task-01"
# bucketName = input("Enter Bucket name: ")
bucket = boto3.client('s3')


def contains_account_id(data, account_id):
  if isinstance(data, dict):
      for key, value in data.items():
          if contains_account_id(value, account_id):
              return True
  elif isinstance(data, list):
      for item in data:
          if contains_account_id(item, account_id):
              return True
  elif isinstance(data, str):
      if account_id in data:
          return True
  return False

def check_policy_for_account_id(policy, account_id):
    for statement in policy.get('Statement', []):
        principal = statement.get('Principal', {})
        condition = statement.get('Condition', {})
        
        if contains_account_id(principal, account_id) or contains_account_id(condition, account_id):
            return True
    return False
  
# def update_policy_with_arn(policy, account_id, new_arn):
#     for statement in policy.get('Statement', []):
#         principal = statement.get('Principal', {})
#         condition = statement.get('Condition', {})
        
#         if not contains_account_id(principal, account_id):
#             statement['Principal']['AWS'] = new_arn
        
#         if 'Condition' not in statement and not contains_account_id(condition, account_id):
#             statement['Condition']['ArnEquals']['aws:SourceArn'] = new_arn

# Get regions list
ec2Regions = boto3.client('ec2')
regions = [region['RegionName'] for region in ec2Regions.describe_regions()['Regions']]
for region in regions:
  
  # Get SQS info
  try:
    sqs = boto3.client('sqs', region_name=region)
      # Get SQS list and URLs
    sqsList = sqs.list_queues()
    queueUrls = sqsList["QueueUrls"]

  except ClientError as e:
    # logging.error(e)
    print("Couldn't access region: "+region)
    continue

  # Check both policies
  # Get SQS Policy
  for sqsSingleUrl in queueUrls:
    sqsPolicy = sqs.get_queue_attributes(
      QueueUrl=sqsSingleUrl,
      AttributeNames=['Policy']
    )
    sqsName = (sqsSingleUrl.split("/"))[4]
    # Check if the principal or condition ARN contains the current account ID
    policy = json.loads(sqsPolicy['Attributes']['Policy'])
    if check_policy_for_account_id(policy, accountId):
        print(f"Account ID found in {sqsSingleUrl}")     


    else:
        print(f"Account ID not found in {sqsSingleUrl}")
        # print(f"Updating the policy of {sqsSingleUrl}..")
        # update_policy_with_arn(policy, accountId, allowedArn)
        # updatedPolicyJson = json.dumps(policy)
        # print(updatedPolicyJson+'\n')
        # response = sqs.set_queue_attributes(
        #   QueueUrl=sqsSingleUrl,
        #   Attributes={'Policy': updatedPolicyJson}
        # )
        with open(logFile, "a") as logs:
          logs.write(sqsName + '\n')

try:
    logging.info('Trying to upload file to bucket')
    response = bucket.upload_file(logFile, bucketName, logFile)
except ClientError as e:
    logging.error(e)