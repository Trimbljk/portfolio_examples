import json
from httplib2 import Http
import uuid
import json


def messenger(event, context):
    """Google Chat incoming webhook."""
    url = "someurl
    sub = "S**t's F**ked Up!"
    imgUrl = "https://external-content.duckduckgo.com/iu/?u=http%3A%2F%2Fwww.pngall.com%2Fwp-content%2Fuploads%2F2017%2F05%2FAlert-PNG.png&f=1&nofb=1&ipt=e091e8973acdc27563c70aa7a28e9ad7c93ae0cdb78fd879fc38489f7aa60e88&ipo=images"
    bot_message = {
        "cardsV2": [
            {
                "cardId": str(uuid.uuid4()),
                "card": {
                    "header": {
                        "title": "Lake Formation Engine Failure",
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
                                        "text": f"STATE_MACHINE_EXECUTION: {event['execName']}",
                                    }
                                },
                                {
                                    "decoratedText": {
                                        "text": f"LAMBDA_LOG_STREAM: {context.log_stream_name}",
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
