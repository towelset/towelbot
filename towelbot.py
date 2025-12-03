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
    QuickReplyItem,
    LocationAction
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    LocationMessageContent
)
import sqlite3

app = Flask(__name__)
DB_NAME = 'user_data.db'

configuration = Configuration(
    access_token='wPZmtiJeIuQkoUadNureJRrq3iOGVhSbk9f3XEnVXkBtaE0ssfTSJzoOVLKxIYYNMdyDqIJA4K8Nz+9giY4DrEOahxTE9PbrC7aNfR+u2tR033r9pHKzB75wR49IzhmLExd0PuC64vQp+OiZmXtGvwdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('daeb40795e3abd094939199d0ebffc2c')


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS locations (
            user_id TEXT PRIMARY KEY,
            latitude REAL,
            longitude REAL
        )
    ''')

    conn.commit()
    conn.close()


init_db()


def save_user_location(user_id, lat, lon):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO locations (user_id, latitude, longitude)
        VALUES (?, ?, ?)
    ''', (user_id, lat, lon))

    conn.commit()
    conn.close()


def get_user_location(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('SELECT latitude, longitude FROM locations WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()

    conn.close()

    if result:
        return result[0], result[1]  # 回傳 (lat, lon)
    else:
        return None


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


@handler.add(MessageEvent, message=LocationMessageContent)
def handle_location(event):
    user_id = event.message.source.user_id
    lat = event.message.latitude
    lon = event.message.longitude
    save_user_location(user_id, lat, lon)


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_id = event.source.user_id
    location = get_user_location(user_id)

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        if location:
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=event.message.text)]
                )
            )
        else:
            reply_req = ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(
                        text="請點選下方按鈕分享您的位置：",
                        quick_reply=QuickReply(
                            items=[
                                QuickReplyItem(
                                    action=LocationAction(label="傳送目前位置")
                                )
                            ]
                        )
                    )
                ]
            )
        line_bot_api.reply_message_with_http_info(reply_req)


if __name__ == "__main__":
    app.run()