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
        qual_id = "2ARFPLSP75KLA8M8DH1HTEQVJT3SY6"
    else:
        print("create HIT on mturk")
        mturk_var = "mturk"
        endpoint_url = "https://mturk-requester.us-east-1.amazonaws.com"
        mturk_form_action = "https://www.mturk.com/mturk/externalSubmit"
        mturk_url = "https://worker.mturk.com/"
        qual_id = "2F1QJWKUDD8XADTFD2Q0G6UTO95ALH"


    worker_requirements = [
        {
            'QualificationTypeId': '000000000000000000L0',
            'Comparator': 'GreaterThanOrEqualTo',
            'IntegerValues': [95],
            'RequiredToPreview': True,
        },
        {
            'QualificationTypeId': '00000000000000000040',
            'Comparator': 'GreaterThanOrEqualTo',
            'IntegerValues': [5000],
            'RequiredToPreview': True,
        }, {
            'QualificationTypeId': qual_id,
            'Comparator': 'Exists',
            'RequiredToPreview': True,
        }
    ]

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
        AutoApprovalDelayInSeconds = HIT["AutoApprovalDelayInSeconds"],
        QualificationRequirements = worker_requirements
    )
    print("HIT type Id: " + new_hit_type['HITTypeId'])