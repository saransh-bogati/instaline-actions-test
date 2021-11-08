from enum import Enum
from typing import Optional, Union
from actions.responses.response_text import BaseResponseText, PlainText
from pydantic.main import BaseModel
from actions.responses.response import BaseBlockResponse, ResponseTypeEnum


class ButtonVariant(str, Enum):
    primary = 'primary'
    secondary = 'secondary'
    default = 'default'
    accent = 'accent'
    neutral = 'neutral'


class ResponseButtonContent(BaseModel):
    id: Optional[str] = None
    text: BaseResponseText = PlainText(content="Button")
    variant: ButtonVariant = ButtonVariant.default

    value: Optional[str] = None # Value to send / pass as argument to the action in action_id
    action_id: Optional[str] = None # Preconfigured actions in the UI


class ResponseButton(BaseBlockResponse):
    type = ResponseTypeEnum.button
    content: ResponseButtonContent
