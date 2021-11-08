from __future__ import annotations
from typing import Any, List, Optional, Union
from pydantic import BaseModel
from enum import Enum

from pydantic.fields import Field


class ResponseTypeEnum(str, Enum):
    header = 'header'
    section = 'section'
    plaintext = 'plaintext'
    markdown = 'markdown'
    card = 'card'
    select = 'select'
    button = 'button'
    image = 'image'
    grid_item = 'grid_item'


class ResponsePlacementEnum(str, Enum):
    inline = 'inline'
    block = 'block'
    grid = 'grid'


class BaseResponse(BaseModel):
    type: ResponseTypeEnum = Field(...)
    placement: ResponsePlacementEnum = Field(ResponsePlacementEnum.block)
    content: Any = None


class BaseInlineResponse(BaseResponse):
    placement = ResponsePlacementEnum.inline
    content: Optional[Union[str, BaseInlineResponse]] = None
    emoji: bool = False


class BaseBlockResponse(BaseResponse):
    placement = ResponsePlacementEnum.block
    content: Optional[
        Union[BaseResponse, List[BaseResponse]]] = None


class StackResponseDirectionEnum(str, Enum):
    horizontal = 'horizontal'
    vertical = 'vertical'


class StackResponse(BaseBlockResponse):
    type = ResponseTypeEnum.section
    placement = ResponsePlacementEnum.block
    direction: StackResponseDirectionEnum = StackResponseDirectionEnum.horizontal


class GridItem(BaseBlockResponse):
    type = ResponseTypeEnum.grid_item
    row: int = Field(...)
    col: int = Field(...)
    rowspan: int = Field(...)
    colspan: int = Field(...)
    content: Optional[BaseBlockResponse] = None


class GridResponse(BaseBlockResponse):
    type = ResponseTypeEnum.section
    placement = ResponsePlacementEnum.grid
    content: List[GridItem] = None
