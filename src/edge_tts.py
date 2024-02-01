
from typing import List
from pydantic import (
    BaseModel,
    Field,
    AliasChoices
)
import httpx

class VoiceTag(BaseModel):
    content_categories:List[str] = Field(List[str], validation_alias=AliasChoices("ContentCategories"))
    voice_personalities:List[str] = Field(List[str], validation_alias=AliasChoices("VoicePersonalities"))

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
    name:str = Field(str, validation_alias=AliasChoices("Name"))
    short_name:str = Field(str, validation_alias=AliasChoices("ShortName"))
    gender:str = Field(str, validation_alias=AliasChoices("Gender"))
    locale:str= Field(str, validation_alias=AliasChoices("Locale"))
    suggested_codec:str = Field(str, validation_alias=AliasChoices("SuggestedCodec"))
    friendly_name:str = Field(str, validation_alias=AliasChoices("FriendlyName"))
    status:str = Field(str, validation_alias=AliasChoices("Status"))
    voice_tag:VoiceTag =Field(VoiceTag, validation_alias=AliasChoices("VoiceTag"))


class EdgeTtsSDK():
    
    def __init__(self, baseurl=""):
        self.baseurl = baseurl

    def get_voice_type(self, apipath="/consumer/speech/synthesize/readaloud/voices/list", trustedclienttoken="6A5AA1D4EAFF4E9FB37E23D68491D6F4") -> list[VoiceType]:
        """
        """
        api_url = f"{self.baseurl}/{apipath}"
        rst = httpx.get(api_url, params=dict(trustedclienttoken=trustedclienttoken))
        if rst.status_code == 200:
            out_l = []
            for i in rst.json():
                out_l.append(VoiceType.model_validate(i))
            return out_l
        else:
            raise  rst.raise_for_status()
        return []

