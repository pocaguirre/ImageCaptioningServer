import boto3
import json
import os
from jinja2 import Environment, FileSystemLoader
import argparse


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--HIT_type", type=str, default="", help="HIT type")
    parser.add_argument("--HIT_number", type=int, default=4, help='Number of HITs per user')
    args = parser.parse_args()
    return args

def create_xml_question(html_text):
    return '<HTMLQuestion xmlns="http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2011-11-11/HTMLQuestion.xsd"><HTMLContent><![CDATA[\n' + \
           html_text +\
           '\n]]></HTMLContent><FrameHeight>600</FrameHeight></HTMLQuestion>'


if __name__ == "__main__":
    args = get_args()
    if args.HIT_type == "":
        raise Exception("Please give a hit type argument")
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

    # create hit with config
    file_loader = FileSystemLoader('static/tasks')
    env = Environment(loader=file_loader)
    template = env.get_template('main.html')
    html_text = template.render(mturk=mturk_var)

    hits = []
    for i in range(args.HIT_number):
        hits.append(mturk.create_hit_with_hit_type(
            HITTypeId=args.HIT_type,
            MaxAssignments = HIT["MaxAssignments"],
            LifetimeInSeconds = HIT["LifetimeInSeconds"],
            Question = create_xml_question(html_text),
        ))
    for hit in hits:
        print("HITId: " + hit['HIT']['HITId'])
        print("A new HIT has been created. You can preview it here:")
        print(mturk_url + "mturk/preview?groupId=" + hit['HIT']['HITGroupId'])