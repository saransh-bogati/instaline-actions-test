from pydantic.fields import Field
from actions.responses.response import BaseBlockResponse, ResponseTypeEnum


class ImageResponse(BaseBlockResponse):
    type = ResponseTypeEnum.image
    content: str = Field(...) # image_url / b64
    alt_text: str = Field('Contains image from instabot.')
