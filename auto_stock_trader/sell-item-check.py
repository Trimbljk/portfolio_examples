from robin_stocks import robinhood as rh
import pyotp
import boto3
import json
import os
import random
import time
import logging

username = os.environ['USERNAME']
otp = os.environ['PYOTP']

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
LOGGER.info("establishing credentials and connecting to dynamoDB")

secret_name = "api-test"
region_name = "us-east-1"
session = boto3.session.Session()
client = session.client(
    service_name='secretsmanager',
    region_name=region_name,
    )
dydb = session.client(service_name='dynamodb',
    region_name=region_name)

currency_pair_ids = {
    '76637d50-c702-4ed1-bcb5-5b0732a81f48': 'ETHUSD',
    '3d961844-d360-45fc-989b-f6fca761d511': 'BTCUSD',
    '383280b1-ff53-43fc-9c84-f01afd0989cd': 'LTCUSD',
    '1ef78e1b-049b-4f12-90e5-555dcf2fe204': 'DOGEUSD',
    '7b577ce3-489d-4269-9408-796a0d1abb3a': 'ETCUSD',
    '086a8f9f-6c39-43fa-ac9f-57952f4a1ba6': 'BSVUSD',
    '2f2b77c4-e426-4271-ae49-18d5cb296d3a': 'BCHUSD',
}
currency_to_genericpair = {
    'ETHUSD': 'ETH',
    'BTCUSD': 'BTC',
    'LTCUSD': 'LTC',
    'DOGEUSD':'DOGE',
    'BSVUSD': 'BSV',
    'BCHUSD': 'BCH',
    'ETCUSD': 'ETC'
}
def get_secret():
    get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    return(get_secret_value_response)

LOGGER.info("logging into Robinhood")
secret = get_secret()
pw = json.loads(secret['SecretString'])[username]
totp = pyotp.TOTP(otp).now()
login = rh.login(username, pw, mfa_code=totp)

def check_prices():
    ticker = []
    for value in currency_pair_ids.values():
        switch = currency_to_genericpair[value]
        ticker.append(switch) 
    
    prices = {}
    
    for tick in ticker:
        resp = rh.crypto.get_crypto_quote(tick)
        prices[resp['symbol']] = float(resp['mark_price'])
    return(prices)    

def collar_hurdle(purchase, market_price):
    
    sell = 'no'
    perh = purchase * .10
    total = purchase + perh
    if market_price >= total:
        sell = 'yes'
    else:
        sell = 'no'
    return(sell)

def check_buyside(event, context):
    if event:
    
        cp = check_prices()
        LOGGER.info('scanning dynamoDB')
        dbscan = dydb.scan(TableName='robinhood-stocks-trading')
        for i in dbscan['Items']:
            tick = i['tick']['S']
            if i['side']['S'] == 'buy':
                yesno = collar_hurdle(float(i['price']['N']), cp[tick])
                if yesno == 'yes':
                    LOGGER.info('generating deduplication keys')
                    data = json.dumps(i)
                    LOGGER.info("SOLD: " + str(i))
                    LOGGER.info(f"Sending {i} to SNS")
                    SNS = boto3.client("sns")
                    resp = SNS.publish(Message=data, TopicArn='arn:aws:sns:us-east-1:022858746308:db-sell-crypto')
                else:
                    resp = 'UNSOLD'
            else:
                resp = "NO BUY ITEMS"
            
    return(resp)

