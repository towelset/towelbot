from flask import Flask, request, abort

from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    QuickReply,
    QuickReplyItem
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)
import random

app = Flask(__name__)

configuration = Configuration(
    access_token='jh6odJ/JkJ8CvC+9SNnLvAyLPQE/3bIFv01WopP8WGXyLCYzaWniYEKuIl8mcFSGET6M0MVvu8F+92Asyb2kkvpE1wE5hOcMxOYMgYNbB2q80VjPHAIH+uL3T+PA3BJSCfpTXj1+sAJ+di8eGMhhOwdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('8c9300fbaf4aa60be0cfb48170415380')

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

image_list = ['https://ibb.co/GvwTS57J', 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSSyJZJYD1zkfS20r2T64Iukda_ij0URw0tAQ&s', 'https://megapx-assets.dcard.tw/images/ee292ca7-b199-4513-8401-9229c90acc5f/640.jpeg']

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_message = event.message.text
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        if user_message == '嗨' or user_message == '你好' or user_message.lower() == 'hi' or user_message.lower() == 'hello':
            image_number = random.randint(0, 2)
            reply_req = ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[{
                    "type": "image",
                    "originalContentUrl": image_list[image_number],
                    "previewImageUrl": image_list[image_number]
                }]
            )
            line_bot_api.reply_message_with_http_info(reply_req)

if __name__ == "__main__":
    app.run()