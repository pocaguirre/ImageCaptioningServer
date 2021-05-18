import boto3
import json
import os


if __name__ == "__main__":
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

    # create mturk connection through boto3
    mturk = boto3.client('mturk',
       aws_access_key_id = aws_key["aws_access_key_id"],
       aws_secret_access_key = aws_key["aws_secret_access_key"],
       region_name=HIT["REGION_NAME"],
       endpoint_url = endpoint_url
    )

    new_hit_type = mturk.create_hit_type(
        Title = HIT['Title'],
        Description = HIT["Description"],
        Keywords = HIT["Keywords"],
        Reward = HIT["Reward"],
        AssignmentDurationInSeconds = HIT["AssignmentDurationInSeconds"],
        AutoApprovalDelayInSeconds = HIT["AutoApprovalDelayInSeconds"]
    )
    print("HIT type Id: " + new_hit_type['HITTypeId'])