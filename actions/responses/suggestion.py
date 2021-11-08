from enum import Enum
from typing import List, Text
from pydantic.fields import Field

from pydantic import BaseModel


class SuggestionVariant(str, Enum):
    primary = 'primary'
    secondary = 'secondary'
    default = 'default'
    accent = 'accent'
    neutral = 'neutral'


class SuggestionItem(BaseModel):
    variant: SuggestionVariant = SuggestionVariant.default
    text: Text = Field(...)
    value: Text = Field(...)
    emoji: bool = Field(False)


class Suggestion(BaseModel):
    title: str = Field(None, max_length=16)
    suggestions: List[SuggestionItem] = Field(...)
