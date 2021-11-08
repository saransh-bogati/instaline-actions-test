from pydantic.fields import Field
from actions.responses.response import BaseInlineResponse, ResponseTypeEnum


class BaseResponseText(BaseInlineResponse):
    content: str = Field(..., min_length=1, max_length=1024)


class PlainText(BaseResponseText):
    type = ResponseTypeEnum.plaintext


class Markdown(BaseResponseText):
    type = ResponseTypeEnum.markdown
