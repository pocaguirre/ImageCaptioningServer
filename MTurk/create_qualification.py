import boto3
import json

# Qual: 35NJKTSSL4WD2NU54PDPPEUE8AHZXS
# Qual not sandbox: 3874R5DF6U2ITZNA0D54D39N6LDJPI

questions = open('qualifications/questions.xml', mode='r').read()
answers = open('qualifications/answers.xml', mode='r').read()

aws_key = json.load(open("keys.json"))

mturk = boto3.client('mturk',
                    aws_access_key_id = aws_key["aws_access_key_id"],
                        aws_secret_access_key = aws_key["aws_secret_access_key"],
                      region_name='us-east-1',
                      endpoint_url='https://mturk-requester.us-east-1.amazonaws.com')

qual_response = mturk.create_qualification_type(
                        Name='Good Image Caption Rater',
                        Keywords='test, qualification, sample, image, captions, descriptions',
                        Description='This is a brief test for image description rater',
                        QualificationTypeStatus='Active',
                        Test=questions,
                        AnswerKey=answers,
                        TestDurationInSeconds=600)

print(qual_response['QualificationType']['QualificationTypeId'])