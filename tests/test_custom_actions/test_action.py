import pytest

from pathlib import Path

from conftest import EMPTY_TRACKER, TRACKER_WITH_ITEM, TRACKER_WITH_ITEM_AND_QUANTITY
import pprint
import sys
p = Path(__file__).parents[2]
sys.path.insert(0,str(p))
pprint.pprint(sys.path)
from actions.actions import ActionGreet, ActionItemsModified, ActionShowLocation
from actions.action_order import ActionAddNotes, ActionCancelOrder, ActionPlaceOrder, ValidateRestaurantForm


@pytest.mark.asyncio
async def test_action_greet(dispatcher, domain):
    tracker = EMPTY_TRACKER
    action = ActionGreet()
    events = await action.run(dispatcher, tracker, domain)
    expected_template = "utter_greet"
    assert dispatcher.messages[0]["template"] == expected_template

@pytest.mark.asyncio
async def test_restaurant_form_ask_quantity(dispatcher, domain):
    tracker = TRACKER_WITH_ITEM
    action = ValidateRestaurantForm()
    events = await action.run(dispatcher, tracker, domain)
    expected_events = [

    ]
    print(events)
    expected_template = "utter_ask_quantity"
    print(dispatcher)
    # assert dispatcher.message[0]["template"] == expected_template

@pytest.mark.asyncio
async def test_action_show_location(dispatcher, domain):
    tracker = EMPTY_TRACKER
    action = ActionShowLocation()
    events = await action.run(dispatcher, tracker, domain)
    assert dispatcher.messages[0]["text"] and dispatcher.messages[0]["text"] is not ""

@pytest.mark.asyncio
async def test_action_business_hours(dispatcher, domain):
    tracker = EMPTY_TRACKER
    action = ActionShowLocation()
    events = await action.run(dispatcher, tracker, domain)
    assert dispatcher.messages[0]["text"] and dispatcher.messages[0]["text"] is not ""

@pytest.mark.asyncio
async def test_action_items_modified(dispatcher, domain):
    tracker = TRACKER_WITH_ITEM
    action = ActionItemsModified()
    events = await action.run(dispatcher, tracker, domain)
    assert dispatcher.messages[0]["text"] and dispatcher.messages[0]["text"] is not ""

@pytest.mark.asyncio
async def test_action_place_order_add(dispatcher, domain):
    tracker = TRACKER_WITH_ITEM_AND_QUANTITY
    action = ActionPlaceOrder()
    events = await action.run(dispatcher, tracker, domain)
    expected_events = [
        {"event": "reset_slots", "timestamp": None } 
    ]
    expected_template = "utter_order_add_confirmation"
    assert dispatcher.messages[0]["template"] == expected_template
    assert events == expected_events


@pytest.mark.asyncio
async def test_action_cancel_order(dispatcher, domain):
    tracker = TRACKER_WITH_ITEM_AND_QUANTITY
    action = ActionCancelOrder()
    events = await action.run(dispatcher, tracker, domain)
    expected_events = [
        {"event": "reset_slots", "timestamp": None } 
    ]
    expected_template = "utter_order_remove_confirmation"
    assert dispatcher.messages[0]["template"] == expected_template
    assert events == expected_events

# @pytest.mark.asyncio
# async def test_action_add_notes(dispatcher, domain):
#     tracker = TRACKER_WITH_ITEM_AND_QUANTITY
#     action = ActionAddNotes()
#     events = await action.run(dispatcher, tracker, domain)
#     expected_message = "Note added. You can add more items or continue to checkout"
#     assert dispatcher.messages[0]["text"] == expected_message

@pytest.mark.asyncio
async def test_validate_restaurant_form_item(dispatcher, domain):
    tracker = TRACKER_WITH_ITEM_AND_QUANTITY
    action = ValidateRestaurantForm()
    event = await action.validate_item(tracker.get_slot("item"), dispatcher, tracker , domain)
    expected_event = {
        "item": tracker.get_slot("item")
    }
    assert event == expected_event

@pytest.mark.asyncio
async def test_validate_restaurant_form_quantity(dispatcher, domain):
    tracker = TRACKER_WITH_ITEM_AND_QUANTITY
    action = ValidateRestaurantForm()
    event = await action.validate_quantity(tracker.get_slot("quantity"), dispatcher, tracker , domain)
    
    assert str(event['quantity']) == tracker.get_slot("quantity")

