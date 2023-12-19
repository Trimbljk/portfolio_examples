from httplib2 import Http
import uuid
import json


def messenger(event_type, database, table, statelogs, stream, chatUrl):
    """Google Chat incoming webhook."""
    url = chatUrl 
    if event_type == "CreateTable":
        sub = "A new table has been added to the production catalog"
        imgUrl= "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Ftse3.mm.bing.net%2Fth%3Fid%3DOIP.yucpakrlFzp5-EHe9du0NgAAAA%26pid%3DApi&f=1&ipt=15c44d75d4faaaa3646952e232d92a4c29de8f83d04cad5e6663797e2614fe19&ipo=images"
    elif event_type == "UpdateTable":
        sub = "A table path has been updated in the production catalog"
        imgUrl= "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Ftse3.mm.bing.net%2Fth%3Fid%3DOIP.yucpakrlFzp5-EHe9du0NgAAAA%26pid%3DApi&f=1&ipt=15c44d75d4faaaa3646952e232d92a4c29de8f83d04cad5e6663797e2614fe19&ipo=images"
    else:
        sub = "A table has been removed from the production catalog"
        imgUrl = "http://www.pngall.com/wp-content/uploads/5/Red-Minus-PNG-Image.png" 
    bot_message = {
        "cardsV2": [
            {
                "cardId": str(uuid.uuid4()),
                "card": {
                    "header": {
                        "title": event_type,
                        "subtitle": sub,
                        "imageUrl": imgUrl,
                        "imageType": "CIRCLE",
                    },
                    "sections": [
                        {
                            "header": "Event Details",
                            "collapsible": "false",
                            "widgets": [
                                {
                                    "decoratedText": {
                                        "text": f"DATABASE:  <b>{database}</b>",
                                    },
                                },
                                {
                                    "decoratedText": {
                                        "text": f"TABLE:  <b>{table}</b>",
                                    }
                                },
                                {
                                    "decoratedText": {
                                        "text": f"STATE_MACHINE_EXECUTION: {statelogs}",
                                    }
                                },
                                {
                                    "decoratedText": {
                                        "text": f"LOG_GROUP: aws/lambda/ShareResourceAcrossAccount",
                                    }
                                },
                                {
                                    "decoratedText": {
                                        "text": f"LAMBDA_LOG_STREAM: {stream}",
                                    }
                                },
                            ],
                        },
                    ],
                },
            }
        ],
    }
    message_headers = {"Content-Type": "application/json; charset=UTF-8"}
    http_obj = Http()
    response = http_obj.request(
        uri=url,
        method="POST",
        headers=message_headers,
        body=json.dumps(bot_message),
    )
    return json.loads(response[1].decode())
