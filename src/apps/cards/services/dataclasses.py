from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SetData:
    set_id: str
    name: str
    release_date: str
    card_count: int
    tcgplayer_id: str


@dataclass
class CardData:
    external_api_id: str
    name: str
    riftbound_id: str
    tcgplayer_id: str
    might: int
    energy_cost: int
    power_cost: int
    body_text: str
    flavour_text: str
    variant: Optional[str]
    artist: str
    image_url: str
    type: str
    supertype: Optional[str]
    rarity: str
    set_id: str
    tags: list[str] = field(default_factory=list)
    domains: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
