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
    '3d961844-d360-45fc-989b-f6fca761d511': "BTC",
    "76637d50-c702-4ed1-bcb5-5b0732a81f48": 'ETH',
    '2f2b77c4-e426-4271-ae49-18d5cb296d3a': 'BCH',
    '383280b1-ff53-43fc-9c84-f01afd0989cd': 'LTC',
    '1ef78e1b-049b-4f12-90e5-555dcf2fe204': 'DOGE',
    '7b577ce3-489d-4269-9408-796a0d1abb3a': 'ETC',
    '086a8f9f-6c39-43fa-ac9f-57952f4a1ba6': 'BSV'
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
    
    info = rh.crypto.get_crypto_currency_pairs()
    tradable_crypto = []
    for asset in info:
        if asset['tradability'] == 'tradable':
            tradable_crypto.append(asset['asset_currency']['code'])
    pairs = {}
    for currency in tradable_crypto:
        pairs[currency + 'USD'] = currency
    
    prices = {}
    
    for tick in pairs.values():
        resp = rh.crypto.get_crypto_quote(tick)
        prices[resp['symbol']] = float(resp['mark_price'])
    return(prices, pairs)

def get_crypto_info(sp):
    
    inter = ''
    if sp == 'week':
        inter = 'day'
    else:
        inter = 'hour'
    
    prices = check_prices()
    tick_changes = {}
    for tick in prices[1].values():
        LOGGER.info('Retrieving ' + f'{tick}' + ' historical data' )
        find_best = rh.crypto.get_crypto_historicals(tick, interval=inter, span=sp)
        start = float(find_best[0]['close_price'])
        now = check_prices()[0][find_best[0]['symbol']]
        percentage = ((now - start)/start)*100
        tick_changes[percentage] = tick
        time.sleep(1)
    
    least = min(tick_changes.keys())
    buy_today = tick_changes[least]
    
    return(tick_changes, buy_today)

def get_new_crypto(crypto, dollar_amount):
    buy = rh.order_buy_crypto_by_price(crypto,dollar_amount)
    time.sleep(random.randrange(5, 10))
    status = 'unfilled'
    attempts = 0
    while not (status == 'filled' or status == 'canceled'):
        if attempts < 3:
            new_item = rh.orders.get_crypto_order_info(buy["id"])
            status = new_item['state']
            LOGGER.info("Checking Status")
            LOGGER.info(f"{status}")
            if status == 'filled':
                LOGGER.info('FILLED')
                LOGGER.info("Writing to DynamoDB")
                output = dydb.put_item(
                    TableName='robinhood-stocks-trading',
                    Item = {
                        "item_id" : {"S" : new_item["id"]},
                        "price": {"N" : new_item['executions'][0]['effective_price']},
                        "side": {"S": new_item["side"]},
                        "quantity" : {"N" : new_item["quantity"]},
                        "cost": {"N": new_item["rounded_executed_notional"]},
                        "tick": {"S": currency_pair_ids[new_item['currency_pair_id']] + 'USD'}
                    }
                )
                
            else:
                LOGGER.info('UNFILLED')
                time.sleep(10)
                attempts +=1
        else:
            canceled = rh.orders.cancel_crypto_order(buy['id'])
            time.sleep(2)
            item_again = rh.orders.get_crypto_order_info(buy["id"])
            if item_again['state'] == 'filled':
                status = item_again['state']
                LOGGER.info("Checking Status")
                LOGGER.info(f"{status}")
                output = dydb.put_item(
                        TableName='robinhood-stocks-trading',
                        Item = {
                            "item_id" : {"S" : item_again["id"]},
                            "price": {"N" : item_again['executions'][0]['effective_price']},
                            "side": {"S": item_again["side"]},
                            "quantity" : {"N" : item_again["quantity"]},
                            "cost": {"N": item_again["rounded_executed_notional"]},
                            "tick": {"S": currency_pair_ids[new_item['currency_pair_id']] + 'USD'}
                        }
                    )
                            
            else:
                status = item_again['state']
                LOGGER.info("Checking Status")
                LOGGER.info(f"{status}")
                if status == 'canceled':
                    output = "CANCEL ORDER COMPLETE"
                else:
                    output = status

    return(output)

def new_purchase():

    purchases = []
    
    get_cash = rh.account.build_user_profile()
    if float(get_cash['equity']) >= 12:
        for span in ['week', 'day']:
            LOGGER.info('Buying: '+ str(span))
            get_info = get_crypto_info(span)
            tick = get_info[1]
            info = get_info[0]
            new = get_new_crypto(tick, 2) 
            purchases.append(new)
        return(purchases)       
    else:
        return('INSUFFICIENT FUNDS')

def purchase_new_crypto(event, context):
    if event:
        np = new_purchase()
        
    return(np)
