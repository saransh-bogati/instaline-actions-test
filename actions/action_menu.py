from typing import List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.events import (
    EventType,
)
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict


class ActionShowMenu(Action):
    def name(self) -> Text:
        return "action_show_menu"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict
    ) -> List[EventType]:
        # catalog_response = square.get_catalog()
        # catalog = catalog_response.json(
        # ) if catalog_response.status_code == httpx.codes.OK else None
        #
        # response = ResponseInstabot(
        #     card_type=ResponseInstabotCardTypeEnum.product_catalog,
        #     content=catalog
        # )
        #
        # payload = Payload(response=response)
        # dispatcher.utter_message(json_message=payload.dict())

        return []
