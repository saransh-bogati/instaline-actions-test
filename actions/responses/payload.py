from typing import Optional, Union, Any
from pydantic.fields import Field
from actions.responses.response import BaseBlockResponse
from actions.responses.response_text import BaseResponseText
from actions.responses.suggestion import Suggestion
from pydantic import BaseModel


class Payload(BaseModel):
    # response: BaseBlockResponse = Field(...)
    response: Optional[Union[BaseBlockResponse, BaseResponseText]] = Field(None)
    suggestion: Optional[Suggestion] = None
    cart: Any = None
    # state: Snapshot of state from backend.
