import re
import requests
from django.conf import settings

from apps.cards.clients.api_client import BaseCardApiClient
from apps.cards.services.dataclasses import SetData, CardData

import logging
logger = logging.getLogger(__name__)


class RiftcodexApiClient(BaseCardApiClient):
    BASE_URL = settings.RIFTBOUND_API_BASE_URL

    def _get(self, endpoint):
        response = requests.get(f"{self.BASE_URL}/{endpoint}")
        response.raise_for_status()
        return response.json()
    
    def get_cards(self, set_id=None) -> list[CardData]:
        page = 1
        cards = []
        
        while True:
            params = {"page": page, "size": 100}
            if set_id:
                params["set_id"] = set_id
            
            response = requests.get(f"{self.BASE_URL}/cards", params=params)
            response.raise_for_status()
            data = response.json()
            
            cards.extend([self._map_card(card_data) for card_data in data["items"]])
            
            if page >= data["pages"]:
                break
            
            page += 1
        
        logger.info(f"Fetched {len(cards)} cards from API")
        return cards
    
    def get_sets(self) -> list[SetData]:
        return [self._map_set(set_data) for set_data in self._get("sets")["items"]]
    
    def get_tags(self) -> list[str]:
        return self._get("index/tags")["values"]
    
    def get_types(self) -> list[str]:
        return self._get("index/card-types")["values"]
    
    def get_supertypes(self) -> list[str]:
        return self._get("index/card-supertypes")["values"]
    
    def get_rarities(self) -> list[str]:
        return self._get("index/rarities")["values"]
    
    def get_domains(self) -> list[str]:
        return self._get("index/domains")["values"]

    def get_keywords(self) -> list[str]:
        return self._get("index/keywords")["values"]

    @staticmethod
    def _map_set(data: dict) -> SetData:
        return SetData(
            set_id=data["set_id"],
            name=data["name"],
            release_date=data["published_on"],
            card_count=data["card_count"],
            tcgplayer_id=str(data.get("tcgplayer_id", "")),
        )

    @staticmethod
    def _map_card(data: dict) -> CardData:
        classification = data["classification"]
        attributes = data["attributes"]
        text = data["text"]
        media = data["media"]
        metadata = data["metadata"]

        return CardData(
            external_api_id=data["id"],
            name=data["name"],
            riftbound_id=data["riftbound_id"],
            tcgplayer_id=str(data.get("tcgplayer_id", "")),
            might=attributes.get("might", 0),
            energy_cost=attributes.get("energy", 0),
            power_cost=attributes.get("power", 0),
            body_text=text.get("plain", ""),
            flavour_text=text.get("flavour", "") or "",
            variant=RiftcodexApiClient._resolve_variant(metadata),
            artist=media.get("artist", ""),
            image_url=media.get("image_url", ""),
            type=classification["type"],
            supertype=classification.get("supertype"),
            rarity=classification["rarity"],
            set_id=data["set"]["set_id"],
            tags=data.get("tags", []),
            domains=classification.get("domain", []),
            keywords=RiftcodexApiClient._extract_keywords(text.get("plain", "")),
        )

    @staticmethod
    def _resolve_variant(metadata: dict):
        parts = []
        if metadata.get("alternate_art"):
            parts.append("Alternate Art")
        if metadata.get("overnumbered"):
            parts.append("Overnumbered")
        if metadata.get("signature"):
            parts.append("Signature")
        return " + ".join(parts) if parts else None
    
    @staticmethod
    def _extract_keywords(body_text: str) -> list[str]:
        found = re.findall(r'\[([^\]]+)\]', body_text)
        return [re.sub(r'\s*\d+$', '', kw).strip() for kw in found]
