from enum import Enum
from typing import Any
from actions.responses.response import BaseBlockResponse, ResponseTypeEnum
from pydantic import Field


class ResponseInstabotCardTypeEnum(str, Enum):
    product_single = 'product_single'
    product_catalog = 'product_catalog'
    delivery_time = 'delivery_time'
    delivery_location = 'delivery_location'
    payment_invoice = 'payment_invoice'
    payment_receipt = 'payment_receipt'


class ResponseInstabot(BaseBlockResponse):
    type = ResponseTypeEnum.card
    card_type: ResponseInstabotCardTypeEnum = Field(...)
    content: Any = Field(...) # Can be Square / Payment / Delivery Service Specific data.
