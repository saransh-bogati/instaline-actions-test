from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.events import AllSlotsReset, FollowupAction

from actions.responses.payload import Payload
from actions.responses.response_text import PlainText
from actions.services.square import Square


class ActionPlaceOrder(Action):
    def name(self) -> Text:
        return "action_place_order"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker, domain: DomainDict) -> List[Dict[Text, Any]]:

        item_slot = tracker.get_slot("item")
        quantity = tracker.get_slot("quantity")
        cart_action_group = tracker.get_slot("cart_action_group")
        user_id = tracker.sender_id

        if cart_action_group == "remove":
            return [FollowupAction(name="action_cancel_order")]

        square = Square(tracker)
        result = square.resolve_item_slot(item_slot)
        if result is None:
            if tracker.get_slot("requested_slot") is not None:
                dispatcher.utter_message("Item not in catalog.")
            return []
        res_variant, res_item, res_category, res_options = result

        if res_variant is not None:
            item_order_response = square.save_to_cart(res_item, quantity, user_id)          
            if item_order_response:
                new_item_slot = f"{res_variant['item_variation_data']['name']} {res_item['item_data']['name']}"
                dispatcher.utter_message(response="utter_order_add_confirmation", res_item=new_item_slot)
                payload = Payload(cart=item_order_response)
                dispatcher.utter_message(json_message=payload.dict())

                return [AllSlotsReset()]
            else:
                dispatcher.utter_message(text="Couldn't place order at the moment.")
            return []

        dispatcher.utter_message(text="Couldn't place your order.")
        return []


class ActionCancelOrder(Action):
    def name(self) -> Text:
        return "action_cancel_order"

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict) \
            -> List[Dict[Text, Any]]:
        item_slot = tracker.get_slot("item")
        quantity = tracker.get_slot("quantity")
        user_id = tracker.sender_id
        cart_action: str = tracker.get_slot("cart_action")

        # initial value for cart_action is "add". See domain.yml
        # Fallback quick fix when nlu is not working correctly.
        # if cart_action and cart_action.lower() == "add":
        #     return [FollowupAction(name="action_place_order")]

        square = Square(tracker)
        result = square.resolve_item_slot(item_slot)
        if result is None:
            dispatcher.utter_message("Item not in catalog")
            return []
        res_variant, res_item, res_category, res_options = result
        if res_variant is not None:
            item_remove_response = square.remove_from_cart(res_item, quantity, user_id)

            if item_remove_response:
                new_item_slot = f"{res_variant['item_variation_data']['name']} {res_item['item_data']['name']}"
                dispatcher.utter_message(response="utter_order_remove_confirmation", res_item=new_item_slot)
                payload = Payload(cart=item_remove_response)
                dispatcher.utter_message(json_message=payload.dict())

                if not item_remove_response['cart']['items']:
                    dispatcher.utter_message(response="utter_order_empty")

                return [AllSlotsReset()]
            else:
                dispatcher.utter_message(text="Couldn't remove order at the moment.")
            return []

        dispatcher.utter_message(text="Couldn't place your order.")
        return [AllSlotsReset()]


class ActionAskFoodCategory(Action):
    def name(self) -> Text:
        return "action_ask_food_category"

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict) \
            -> List[Dict[Text, Any]]:
        entities = tracker.latest_message.get('entities')
        if entities[0]['entity'] == 'food_category_name':
            food_category_name = entities[0]['value']
            dispatcher.utter_message(text="Which {} would you prefer?".format(food_category_name))
        else:
            dispatcher.utter_message(text="category not found")
        return []


class ActionAskQuantity(Action):
    def name(self) -> Text:
        return "action_ask_quantity"

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict) \
            -> List[Dict[Text, Any]]:
        entities = tracker.latest_message.get('entities')
        number = entities[0]['value']
        if number <= 0:
            dispatcher.utter_message(text="Please type the correct quantity.")
        else:
            dispatcher.utter_message(text="How many/much?")
        return []


class ValidateRestaurantForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_restaurant_form"

    # @staticmethod
    # def cuisine_db() -> List[Text]:
    #     """Database of supported cuisines"""
    #
    #     return ["caribbean", "chinese", "french"]

    async def validate_cart_action(
            self,
            slot_value: Any,  # Normally this value is Union[str, List[str]]
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:

        cart_action_group = tracker.get_slot("cart_action_group")

        cart_action_value = next(tracker.get_latest_entity_values("cart_action", entity_group="remove"), None)
        if cart_action_value:
            return {"cart_action": slot_value, "cart_action_group": "remove"}

        cart_action_value = next(tracker.get_latest_entity_values("cart_action", entity_group="add"), None)
        if cart_action_value:
            return {"cart_action": slot_value, "cart_action_group": "add"}

        if cart_action_group:
            return {"cart_action": slot_value, "cart_action_group": cart_action_group}

        return {"cart_action": None, "cart_action_group": None}

    async def validate_item(
            self,
            slot_value: Any,  # Normally this value is Union[str, List[str]]
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        square = Square(tracker)
        result = square.resolve_item_slot(slot_value)
        if result is None:
            dispatcher.utter_message("Item not in catalog. Please try other items from the menu.")
            return {"item": None, "quantity": None}
        res_variant, res_item, res_category, res_options = result

        if res_variant is not None:
            return {"item": slot_value}
        else:
            if res_options is None:
                options_string_list = None
            else:
                options_string_list = []
                for option in res_options:
                    if option['type'] == 'ITEM':
                        options_string_list.append(option['item_data']['name'])
                    elif option['type'] == "ITEM_VARIATION":
                        options_string_list.append(option['item_variation_data']['name'])
                    elif option['type'] == "CATEGORY":
                        options_string_list.append(option['category_data']['name'])
            if options_string_list:
                response = PlainText(
                    content=f"Which one would you like? Here are the options: {', '.join(options_string_list)}"
                )
                payload = Payload(response=response)
                dispatcher.utter_message(json_message=payload.dict())
                # dispatcher.utter_message(f"Which one would you like? Here are the options: {options_string_list}")
            else:
                dispatcher.utter_message(response="utter_item_not_understood")

            return {"item": None}

    async def validate_quantity(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        if slot_value is None:
            return {"quantity": None}

        try:
            quantity = int(slot_value)
        except:
            try:
                quantity = float(slot_value)
                dispatcher.utter_message("Invalid quantity. Please enter exact numbers like 1,3,6 etc. ")
            except:
                return {"quantity": None}
            
        if quantity <= 0:
            dispatcher.utter_message("Invalid quantity. Please enter quantity above 0.")
            return {"quantity": None}
        else:
            return {"quantity": quantity}


# class ActionAddNotes(Action):
#     def name(self) -> Text:
#         return "action_add_notes"
    
#     async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict) \
#             -> List[Dict[Text, Any]]:
#         user_id = tracker.sender_id
#         square = Square(tracker)
#         note = tracker.latest_message['text']
#         response = square.add_notes(user_id, note)
#         dispatcher.utter_message("Note added. You can add more items or continue to checkout")
#         return []
        

