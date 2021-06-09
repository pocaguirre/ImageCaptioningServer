import boto3
from datetime import datetime
import os
import json

if not os.path.exists("keys.json"):
    raise Exception('Please add your aws keys to create HIT on aws')

# add your aws keys to
aws_key = json.load(open("keys.json"))
config = json.load(open("config.json"))
HIT = config["HIT"]
if HIT["USE_SANDBOX"]:
    print("create HIT on sandbox")
    mturk_var = "sandbox"
    endpoint_url = "https://mturk-requester-sandbox.us-east-1.amazonaws.com"
    mturk_form_action = "https://workersandbox.mturk.com/mturk/externalSubmit"
    mturk_url = "https://workersandbox.mturk.com/"
else:
    print("create HIT on mturk")
    mturk_var = "mturk"
    endpoint_url = "https://mturk-requester.us-east-1.amazonaws.com"
    mturk_form_action = "https://www.mturk.com/mturk/externalSubmit"
    mturk_url = "https://worker.mturk.com/"

# Get the MTurk client
mturk=boto3.client('mturk',
        aws_access_key_id=aws_key["aws_access_key_id"],
        aws_secret_access_key=aws_key["aws_secret_access_key"],
                   region_name=HIT["REGION_NAME"],
                   endpoint_url=endpoint_url
                   )

# Delete HITs
for item in mturk.list_hits()['HITs']:
    hit_id=item['HITId']
    print('HITId:', hit_id)

    # Get HIT status
    status=mturk.get_hit(HITId=hit_id)['HIT']['HITStatus']
    print('HITStatus:', status)

    # If HIT is active then set it to expire immediately
    if status=='Assignable':
        response = mturk.update_expiration_for_hit(
            HITId=hit_id,
            ExpireAt=datetime(2015, 1, 1)
        )

    # Delete the HIT
    try:
        mturk.delete_hit(HITId=hit_id)
    except:
        print('Not deleted')
    else:
        print('Deleted')