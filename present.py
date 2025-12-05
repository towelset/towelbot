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
    ImageMessage,
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

image_list = ['https://i.ibb.co/QFBdwK9c/2025-12-05-6-02-39.png', 'https://i.ytimg.com/vi/0hD69lbpbHI/mqdefault.jpg', 'https://megapx-assets.dcard.tw/images/ee292ca7-b199-4513-8401-9229c90acc5f/640.jpeg']

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_message = event.message.text
    image = random.choice(image_list)
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        if user_message == '嗨' or user_message == '你好' or user_message.lower() == 'hi' or user_message.lower() == 'hello':
            reply_req = ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    ImageMessage(
                        original_content_url=image,
                        preview_image_url=image
                    )
                ]
            )
        if not image:
            reply_req = ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(
                        text="Oh no, image not found."
                    )
                ]
            )
        else:
            reply_req = ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(
                        text='I have no idea what happened.'
                    )
                ]
            )
        line_bot_api.reply_message_with_http_info(reply_req)

if __name__ == "__main__":
    app.run()