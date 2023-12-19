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

def sell_crypto(item):
    
    trade_kind = 'sell'
    quan = float(item['quantity']['N'])
    convert = currency_to_genericpair[item['tick']['S']]
    LOGGER.info('selling item')
    sell = rh.order_sell_crypto_by_quantity(convert, quan)
    dbput = trade_order_dbupdate(sell, trade_kind, item)
    return(sell)
    
    
def get_profit(response, buy_info): 
    
    total = float(response['quantity']) * float(response['price'])
    profit = (total - (float(buy_info['quantity']['N']) * float(buy_info['price']['N'])))
    pocket = profit * .5
    invest = round(total - pocket, 2)
    status = ''
    if profit > 0:
        status = 'gain'
    elif profit < 0:
        status = 'loss'
    else:
        status = 'no-change'
    
    return(
        {'total': str(total), 
         'profit': str(profit), 
         'pocket': str(pocket), 
         'invest': str(invest), 
         'status':status}
    )

def dbputs(data, profit=None):
    
    if profit == None:
        put_data = {
            "item_id" : {"S" : data["id"]},
            "price": {"N" : data['executions'][0]['effective_price']},
            "side": {"S": data["side"]},
            "quantity" : {"N" : data["quantity"]},
            "cost": {"N": data["rounded_executed_notional"]},
            "tick": {"S": currency_pair_ids[data['currency_pair_id']]}
                     }
    elif profit != None:
        put_data = {
            "item_id" : {"S" : data["id"]},
            "price": {"N" : data['executions'][0]['effective_price']},
            "side": {"S": data["side"]},
            "quantity" : {"N" : data["quantity"]},
            "tick": {"S": currency_pair_ids[data['currency_pair_id']]},
            'invest': {'N':  profit['invest']},
            'profit': {'N': profit['profit']},
            'status': {'S': profit['status']},
            'pocket': {"N": profit['pocket']}
                     }
    return(put_data)   
    
def trade_order_dbupdate(new_item, put_item_type, original_item):
    
    time.sleep(random.randrange(5, 10))
    status = 'unfilled'
    attempts = 0
    while not (status == 'filled' or status == 'canceled'):
        if attempts < 3:
            print(new_item['id'])
            info = rh.orders.get_crypto_order_info(new_item["id"])
            status = info['state']
            if status == 'filled':
                if put_item_type == 'sell':
                    profit_info = get_profit(info, original_item)
                    dydb.put_item(
                        TableName='robinhood-stocks-trading',
                        Item = dbputs(info, profit_info)
                    )
                    dydb.delete_item(
                        TableName='robinhood-stocks-trading',
                        Key = {
                            "item_id" : {"S" : original_item["item_id"]['S']},
                            "tick": {"S" : original_item["tick"]['S']},
                        }
                    )
                    return_info = 'put new sell data'
                elif put_item_type == 'buy':
                    print('putting_item')
                    dydb.put_item(
                        TableName='robinhood-stocks-trading',
                        Item = dbputs(info)
                    )
                    print('deleting_item')
                    print(original_item)
                    r = dydb.delete_item(
                        TableName='robinhood-stocks-trading',
                        Key = {
                            "item_id" : {"S" : original_item["item_id"]['S']},
                            "tick": {"S" : original_item["tick"]['S']},
                        }
                    )
                    return_info = r
            else:
                time.sleep(5)
                attempts +=1
        else:
            canceled = rh.orders.cancel_crypto_order(info['id'])
            time.sleep(2)
            item_again = rh.orders.get_crypto_order_info(info["id"])
            if item_again['state'] == 'filled':
                status = item_again['state']
                LOGGER.info("Checking Status")
                LOGGER.info(f"{status}")
                return_info = dydb.put_item(
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
                    return_info = "CANCEL ORDER COMPLETE"
                else:
                    return_info = status

    return(return_info)

def lambda_handler(event, context):
    
    if event:
        msg = event["Records"][0]['Sns']['Message']
        trade = json.loads(msg)
        LOGGER.info(f'{trade}')
        db_r = sell_crypto(trade)
    
    return(msg)
