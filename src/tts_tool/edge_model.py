
import re
import hashlib
from typing import List, Optional
from pydantic import (
    BaseModel,
    Field,
    AliasChoices,
    computed_field
)


class VoiceTag(BaseModel):
    content_categories: List[str] = Field(
        List[str], validation_alias=AliasChoices("ContentCategories"))
    voice_personalities: List[str] = Field(
        List[str], validation_alias=AliasChoices("VoicePersonalities"))


class VoiceType(BaseModel):
    """
        {
            "Name": "Microsoft Server Speech Text to Speech Voice (af-ZA, AdriNeural)",
            "ShortName": "af-ZA-AdriNeural",
            "Gender": "Female",
            "Locale": "af-ZA",
            "SuggestedCodec": "audio-24khz-48kbitrate-mono-mp3",
            "FriendlyName": "Microsoft Adri Online (Natural) - Afrikaans (South Africa)",
            "Status": "GA",
            "VoiceTag": {
            "ContentCategories": [
                "General"
            ],
            "VoicePersonalities": [
                "Friendly",
                "Positive"
            ]
            }
        }
    """
    name: str = Field(str, validation_alias=AliasChoices("Name"))
    name_md5: Optional[str] = None
    short_name: str = Field(str, validation_alias=AliasChoices("ShortName"))
    gender: str = Field(str, validation_alias=AliasChoices("Gender"))
    locale: str = Field(str, validation_alias=AliasChoices("Locale"))
    suggested_codec: str = Field(
        str, validation_alias=AliasChoices("SuggestedCodec"))
    friendly_name: str = Field(
        str, validation_alias=AliasChoices("FriendlyName"))
    status: str = Field(str, validation_alias=AliasChoices("Status"))
    voice_tag: VoiceTag = Field(
        VoiceTag, validation_alias=AliasChoices("VoiceTag"))

    @computed_field
    def suggested_codec_audio_type(self) -> str:
        return self.suggested_codec.split("-")[-1]

    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, **kwargs)
        self.name_md5 = hashlib.md5(self.name.encode("utf8")).hexdigest()
