from datetime import datetime
from typing import Any, Dict, List, Text

import pytz
from rasa_sdk import Action, Tracker
from rasa_sdk.events import (
    EventType,
)
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

from actions.services.square import Square
from actions.utils.time_utils import parse_period


class ActionSearch(Action):
    def name(self) -> Text:
        return "action_search"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict
    ) -> List[EventType]:
        item = tracker.get_slot('item')
        quantity = tracker.get_slot('quantity')

        dispatcher.utter_message(text=f"Thank You for ordering {item}")
        return []


class ActionShowLocation(Action):
    def name(self) -> Text:
        return "action_show_location"

    async def run(self, dispatcher: "CollectingDispatcher", tracker: Tracker, domain: DomainDict) \
            -> List[Dict[Text, Any]]:
        # get and show location
        square = Square(tracker)
        data = square.show_location()

        # dispatcher.utter_message(json_message=data)
        dispatcher.utter_message(text="We are located at:\n" + data)

        return []


class ActionCheckItem(Action):
    """
    1. If there is one item variant, pick that item variant
    2. If only one item pick item
    3. If there is one category pick the category
    4. Ask the user to rephrase

    User queries Response Possibilities
    1. Categories
        - Ask for item and item variant
    2. Items
        - We ask for item variant / modifier
        - Move to the next step (quantity etc...)
    3. Item Variant
        - If there is one item variant, choose it as default
        - Confirm Add variant instead?
    """

    def name(self) -> Text:
        return "action_check_item"

    async def run(self, dispatcher: "CollectingDispatcher", tracker: Tracker, domain: DomainDict) \
            -> List[Dict[Text, Any]]:
        # dispatcher.utter_message(text="CheckItemMethod")
        return []


class ActionCheckModifiers(Action):
    def name(self) -> Text:
        return "action_check_modifiers"

    async def run(self, dispatcher: "CollectingDispatcher", tracker: Tracker, domain: DomainDict) \
            -> List[Dict[Text, Any]]:
        # dispatcher.utter_message(text="ActionCheckModifiers")

        return []


class ActionShowModifiers(Action):
    def name(self) -> Text:
        return "action_show_modifiers"

    async def run(self, dispatcher: "CollectingDispatcher", tracker: Tracker, domain: DomainDict) \
            -> List[Dict[Text, Any]]:
        # dispatcher.utter_message(text="ActionShowModifiers")
        return []


class ActionValidateInput(Action):
    def name(self) -> Text:
        return "action_validate_input"

    async def run(self, dispatcher: "CollectingDispatcher", tracker: Tracker, domain: DomainDict) \
            -> List[Dict[Text, Any]]:
        # item_slot = tracker.get_slot("item")
        # quantity = tracker.get_slot("quantity")
        # category = tracker.get_slot("category")
        # if category == "dummy":
        #     res = square.menu_item_exists(item_slot)["objects"]
        #     for item in res:
        #         if item["type"] == "CATEGORY":
        #             category_name = item["category_data"]["name"]
        #             dispatcher.utter_message(response="utter_category", category=category_name)
        #             SlotSet("category", category_name)
        # if quantity == 0:
        #     dispatcher.utter_message(response="utter_ask_quantity")
        # elif quantity < 0:
        #     dispatcher.utter_message(response="utter_ask_valid_quantity")

        return []


class ActionBusinessHours(Action):
    def name(self) -> Text:
        return "action_business_hours"

    async def run(self, dispatcher: "CollectingDispatcher", tracker: Tracker, domain: DomainDict) \
            -> List[Dict[Text, Any]]:
        # get and show business hours
        square = Square(tracker)
        data = square.get_business_hours_formatted()

        # dispatcher.utter_message(json_message=data)
        dispatcher.utter_message(text="Our office remains open at:\n" + data)
        return []


class ActionGreet(Action):
    def name(self) -> Text:
        return "action_greet"

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict) \
            -> List[Dict[Text, Any]]:
        # get and show business hours
        print(tracker)
        square = Square(tracker)
        location_data = square.get_location_data()
        if location_data:
            data = location_data['location']['business_hours']['periods']
            location_tz = pytz.timezone(location_data['location']['timezone'])

            if data:
                current_time = datetime.now(tz=location_tz)
                for index, period in enumerate(data):
                    if period['day_of_week'] == current_time.strftime("%a").upper():
                        start_time = parse_period(period['start_local_time'], location_tz)
                        end_time = parse_period(period['end_local_time'], location_tz)

                        if start_time > current_time:
                            dispatcher.utter_message("We are closed at the moment and will be open today at {}."
                                                     .format(start_time.strftime('%I:%M %p')))
                            return []
                        elif end_time < current_time:
                            next_period = data[(index + 1) % len(data)]
                            next_start_time = parse_period(next_period['start_local_time'], location_tz,
                                                           next_period['day_of_week'], True)
                            dispatcher.utter_message("We are closed at the moment and will be open on {}."
                                                     .format(next_start_time.strftime('%a %I:%M %p')))
                            return []

        dispatcher.utter_message(response="utter_greet")
        return []


class ActionItemsModified(Action):
    def name(self) -> Text:
        return "action_items_modified"

    async def run(self, dispatcher: "CollectingDispatcher", tracker: Tracker, domain: DomainDict) \
            -> List[Dict[Text, Any]]:
        # get and show business hours
        # square = Square(tracker)
        # data = square.get_business_hours_formatted()

        # # dispatcher.utter_message(json_message=data)
        food = next(tracker.get_latest_entity_values("food"),None)
        dispatcher.utter_message(f"{food} has been added to cart.")
        dispatcher.utter_message("Please leave a special note or continue adding new items")
        return []
