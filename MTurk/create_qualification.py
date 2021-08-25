import boto3
import json

# Qual: 3QQSP4JEPW0HZY43K8HY4DDXKLO76U
# Qual not sandbox: 3S7VZ13DOG57A1JJVMJB0150BGYRIV

questions = open('qualifications/questions.xml', mode='r').read()
answers = open('qualifications/answers.xml', mode='r').read()

aws_key = json.load(open("keys.json"))

mturk = boto3.client('mturk',
                    aws_access_key_id = aws_key["aws_access_key_id"],
                        aws_secret_access_key = aws_key["aws_secret_access_key"],
                      region_name='us-east-1',
                      endpoint_url='https://mturk-requester-sandbox.us-east-1.amazonaws.com')

qual_response = mturk.create_qualification_type(
                        Name='Good Image Caption Rater',
                        Keywords='test, qualification, sample, image, captions, descriptions',
                        Description='This is a brief test for image description rater',
                        QualificationTypeStatus='Active',
                        Test=questions,
                        AnswerKey=answers,
                        TestDurationInSeconds=600)

print(qual_response['QualificationType']['QualificationTypeId'])