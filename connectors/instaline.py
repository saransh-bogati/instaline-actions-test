import inspect
import json
from typing import Text, Dict, Any, Optional, Callable, Awaitable

from rasa.core.channels.channel import (
    InputChannel,
    CollectingOutputChannel,
    UserMessage,
)
from sanic import Blueprint, response
from sanic.request import Request
from sanic.response import HTTPResponse


class Instaline(InputChannel):
    @classmethod
    def name(cls) -> Text:
        return "instaline"

    def blueprint(self, on_new_message: Callable[[UserMessage], Awaitable[Any]]) -> Blueprint:
        custom_webhook = Blueprint(
            f"custom_webhook_{type(self).__name__}",
            inspect.getmodule(self).__name__
        )

        @custom_webhook.route('/', methods=["GET"])
        async def health(request: Request) -> HTTPResponse:
            return response.json({"status": "ok"})

        @custom_webhook.route('/webhook', methods=["POST"])
        async def receive(request: Request) -> HTTPResponse:
            sender = request.json.get("sender")
            message = request.json.get("message")
            input_channel = self.name()
            metadata = self.get_metadata(request)

            collector = CollectingOutputChannel()

            await on_new_message(
                UserMessage(
                    text=message,
                    output_channel=collector,
                    sender_id=sender,
                    input_channel=input_channel,
                    metadata=metadata
                )
            )

            return response.json(collector.messages)

        return custom_webhook

    def get_metadata(self, request: Request) -> Optional[Dict[Text, Any]]:
        _metadata = super(Instaline, self).get_metadata(request)

        metadata = _metadata if _metadata is not None else {}
        if 'instaline' not in metadata:
            metadata['instaline'] = {}
        metadata['instaline'] = request.json.get('metadata')

        return metadata
