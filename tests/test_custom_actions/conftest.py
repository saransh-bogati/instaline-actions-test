from pathlib import Path
import pytest
import json

from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk import Tracker

here = Path(__file__).parent.resolve()

EMPTY_TRACKER = Tracker.from_dict(json.load(open(here / "./tracker_data/empty_tracker.json")))
TRACKER_WITH_ITEM = Tracker.from_dict(json.load(open(here / "./tracker_data/tracker_with_item.json")))
TRACKER_WITH_ITEM_AND_QUANTITY = Tracker.from_dict(json.load(open(here / "./tracker_data/tracker_with_item_and_quantity.json")))


@pytest.fixture
def dispatcher():
    return CollectingDispatcher()


@pytest.fixture
def domain():
    return dict()
