import boto3
import json
import logging
import os

from base64 import b64decode
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


# The base-64 encoded, encrypted key (CiphertextBlob) stored in the kmsEncryptedHookUrl environment variable
ENCRYPTED_HOOK_URL = os.environ['kmsEncryptedHook']
# The Slack channel to send a message to stored in the slackChannel environment variable
SLACK_CHANNEL = os.environ['channelName']

HOOK_URL = "https://" + boto3.client('kms').decrypt(CiphertextBlob=b64decode(ENCRYPTED_HOOK_URL))['Plaintext'].decode('utf-8')

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info("Event: " + str(event))
    message = json.loads(event['Records'][0]['Sns']['Message'])
    logger.info("Message: " + str(message))

    alarm_name = message['AlarmName']
    alarm_desc = message['AlarmDescription']
    old_state = message['OldStateValue']
    new_state = message['NewStateValue']
    reason = message['NewStateReason']
    metric = message['Trigger']['MetricName']
    threshold = message['Trigger']['Threshold']
    comp = message['Trigger']['ComparisonOperator']
     
    if 'OK' in new_state:
        comp_message = "was not"
    elif 'ALARM' in new_state:
        comp_message = "was"
    elif 'INSUFFICIENT' in new_state:
        comp_message = "did not have enough data to check if data was"
        
    #green for good
    if 'OK' in new_state:
        color = "#008000"
    #orange for intermediate
    elif 'INSUFFICIENT' in new_state:
        color = "#ffa500"
    # red for alarm
    elif 'ALARM' in new_state:
        color = "#fc0335"

    slack_message = {
        'channel': SLACK_CHANNEL,
        'text': ":cloud: *Cloudwatch Notification*",
        'attachments': [{
                        'color' : color,
                        'fields': [
                            {
                                'title': "Alarm Name",
                                'value': "%s" % (alarm_name),
                                'short': True
                            },
                            {
                                'title': "State Change",
                                'value': "%s *->* %s" % (old_state, new_state),
                                'short': True
                            },
                            {
                                'title': "Alarm Description",
                                'value': "%s" % (alarm_desc),
                                'short': False
                            },
                            {
                                'title': "Trigger",
                                'value': "%s %s %s of: %s" % (metric, comp_message, comp, threshold),
                                'short': False
                            },
                            {
                                'title': "Reason",
                                'value': "%s" % (reason),
                                'short': False
                            }
                            
                            ]
                       }]
    }

    req = Request(HOOK_URL, json.dumps(slack_message).encode('utf-8'))
    try:
        response = urlopen(req)
        response.read()
        logger.info("Message posted to %s", slack_message['channel'])
    except HTTPError as e:
        logger.error("Request failed: %d %s", e.code, e.reason)
    except URLError as e:
        logger.error("Server connection failed: %s", e.reason)
