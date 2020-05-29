# cloudwatch-to-slack
a lambda function that expands on what AWS provides as a blueprint
for slack messages from cloudwatch alarms

## What's Different?
Messages have "attachments" so there is a colored side bar based on what
the alarm has changed from 

green -> new state is 'OK'
red -> new state is 'ALARM'
orange -> new state is 'INSUFFICIENT_DATA'

### What you need for the function
You need to have an AWS role that has the 
'AWSLambdaBasicExecutionRole' attached to it as well as 
a role that can do kms decrytion. If you need that policy,
here it is:

{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "Stmt1443036478000",
            "Effect": "Allow",
            "Action": [
                "kms:Decrypt"
            ],
            "Resource": [
                "arn:aws:kms:us-east-2:517592134955:key/99ac5342-2b1c-42e8-8080-f8ac7d8b0abb"
            ]
        }
    ]
}