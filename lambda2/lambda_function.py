import boto3
import re
import requests
from random import randrange
from requests_aws4auth import AWS4Auth
import json

region = 'us-east-2' # e.g. us-west-1
service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

headers = { "Content-Type": "application/json" }

# Regular expressions used to parse some simple log lines
ip_pattern = re.compile('(\d+\.\d+\.\d+\.\d+)')
time_pattern = re.compile('\[(\d+\/\w\w\w\/\d\d\d\d:\d\d:\d\d:\d\d\s-\d\d\d\d)\]')
message_pattern = re.compile('\"(.+)\"')
akey = "AKIA2WJC54562OC5MSVK"
skey = "TjZcfEwS9bYha/YQ2UQVgoDLXHD1QoMEFy2e0S82"


# Query Elastic search and Dynamodb
def queryResult(term):
    f = randrange(1000)
    url = "https://search-restaurants-ssqahmabav7e6rb57i3ahkwxfe.us-east-2.es.amazonaws.com/restaurants/_search"
    params = {"q": term, "from":str(f), "size":"1"}
    r = requests.get(url = url, auth=awsauth, params = params, headers={})
    data = r.json()
    businessid = (data['hits']['hits'][0]['_source']['restaurantid'])
    
    url2 = "arn:aws:dynamodb:us-east-2:735049541501:table/yelp-restaurants"
    dynamodb = boto3.resource('dynamodb', region_name=region, aws_access_key_id=akey, aws_secret_access_key=skey)
    table = dynamodb.Table('yelp-restaurants')
    return table.get_item(Key={'restaurant_id':businessid})['Item']    


def sendMsg(msg, phone):
    sns = boto3.client('sns', aws_access_key_id=akey, aws_secret_access_key=skey, region_name="us-east-1")
    if phone[0] != '+':
        phone = "+1" + phone
    sns.publish(
        PhoneNumber=phone,
        Message=msg,
        MessageAttributes={
            'AWS.SNS.SMS.SenderID': {
                'DataType': 'String',
                'StringValue': 'MySenderID'   
            }    
        }   
    )  
    

def getQueue():
    sqs = boto3.client('sqs', aws_access_key_id=akey, aws_secret_access_key=skey, region_name="us-west-2")
    queue_url = 'https://sqs.us-west-2.amazonaws.com/735049541501/DiningOrders'
    
    response = sqs.receive_message(
        QueueUrl=queue_url,
        AttributeNames=[
            'SentTimestamp'
        ],
        MaxNumberOfMessages=1,
        MessageAttributeNames=[
            'All'
        ],
        VisibilityTimeout=0,
        WaitTimeSeconds=0
    )
    
    message = response['Messages'][0]
    receipt_handle = message['ReceiptHandle']

    sqs.delete_message(
        QueueUrl=queue_url,
        ReceiptHandle=receipt_handle
    )
    
    return message
    

# Lambda execution starts here
def handler(event, context):
    phone = "6463186824"
    term = "Chinese"
    people = 2
    date = "today"
    time = "7pm"
    
    statusCode = 200
    msg = None
    response = []
    
    # --- Get from queue ---
    try:
        info = getQueue()["Body"]
    except:
        info = "No message in queue."
        return info
        
    info = json.loads(info)
    term = info.get('Cuisine', "TBD")
    people = info.get('Number', "TBD")
    phone = info.get('PhoneNumber', "TBD")
    time = info.get('Time', "TBD")
    date = info.get('Date', "TBD")
    location = info.get('Location', "TBD")
    
    # --- Query from ES and DB --- 
    try:
        for i in range(3):
            response.append(queryResult(term))
    except:
        statusCode = 500
        msg = "The server is too busy for now. Please try again or change your keyword."
    
    if not msg:
        msg = "Hi there! Here are my " + str(term) + " retaurant suggestions for " \
            + str(people) + " people, for " + str(date) + " at " + str(time) + " in " + str(location) + \
            ": \n\n 1. " + response[0]['name'] + ", located at " + response[0]['Address'] + \
            ". \n 2. " + response[1]['name'] + ", located at " + response[1]['Address'] + \
            ". \n 3. " + response[2]['name'] + ", located at " + response[2]['Address'] + ". \n\nEnjoy your meal!"
    sendMsg(msg, phone)
    
    return {
        'statusCode': statusCode,        
        'head': {},
        'body': msg
    }