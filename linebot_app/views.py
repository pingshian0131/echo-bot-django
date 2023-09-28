import logging

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from linebot.v3 import WebhookParser
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent

logger = logging.getLogger(__name__)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)
configuration = Configuration(access_token=settings.LINE_CHANNEL_ACCESS_TOKEN)


@csrf_exempt
@require_http_methods(["POST"])
def callback(request):
    signature = request.headers["X-Line-Signature"]

    body = request.body.decode("utf-8")
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        return HttpResponse(status=400)

    for event in events:
        if not isinstance(event, MessageEvent):
            continue

        if not isinstance(event.message, TextMessageContent):
            continue

        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=event.message.text)],
                )
            )
    return HttpResponse(status=200)
