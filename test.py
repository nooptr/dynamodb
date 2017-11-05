import boto3
import requests
from boto3.session import Session
from boto3.dynamodb.conditions import Key, Attr
import datetime
import time

profile = 'chalice'
session = Session(profile_name=profile)
dynamodb = session.resource('dynamodb', region_name='us-east-1')

table = dynamodb.Table('test')
TRADE_API="https://api.bitfinex.com/v1/trades/BTCUSD"
CHUNK = 25

def insertItems(records):
    count = 0
    items = []
    isDone = False
    for record in records:
        if count == CHUNK:
            count = 0
            items = []
            runBactchWriter(items)
            isDone = True

        isDone = False
        count+=1
        items.append({
            'tid': record['tid'],
            'amount': record['amount'],
            'type': record['type'],
            'price': record['price'],
            'timestamp': record['timestamp']
        })

    if isDone != True:
        runBactchWriter(items)

def runBactchWriter(items):
    with table.batch_writer() as batch:
        for item in items:
            tid = item['tid']
            amount = item['amount']
            price = item['price']
            type = item['type']
            timestamp = item['timestamp']

            batch.put_item(
                Item={
                    'tid': tid,
                    'amount': amount,
                    'price': price,
                    'timestamp': timestamp,
                    'type': type,
                }
            )

def insertItem():
    table.put_item(
       Item={
            'tid': 85403572,
            'amount': 12,
            'price': "7395.21",
            'timestamp': 1509857277,
            'type': 'sell',
        }
    )

# response = requests.request("GET", TRADE_API)
# insertItems(response.json())

# response = table.get_item(
#     Key={
#         'type': 'sell'
#     }
# )
# item = response['Item']
# print(item['price'])


# response = table.query(
#     KeyConditionExpression=Key('tid').eq(85403572)
# )
# items = response['Items']
# print(items)

now = datetime.datetime.now()
startTime = now - datetime.timedelta(days=30)
startTimeUnix = int(startTime.strftime('%s'))
print startTime
print startTimeUnix

response = table.scan(
    FilterExpression=Attr('timestamp').gt(startTimeUnix)
)
items = response['Items']
buyVol = 0
sellVol = 0
for item in items:
    price = float(item['price'])
    amount = float(item['amount'])
    total = price * amount
    type = item['type']
    if type == 'sell':
        sellVol += total
    else:
        buyVol += total

print sellVol
print buyVol
