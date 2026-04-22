import requests
from django.conf import settings

import logging
logger = logging.getLogger(__name__)


class RiftboundApiClient:
    BASE_URL = settings.RIFTBOUND_API_BASE_URL

    @classmethod
    def _get(cls, endpoint):
        response = requests.get(f"{cls.BASE_URL}/{endpoint}")
        response.raise_for_status()
        return response.json()
    
    @classmethod
    def get_cards(cls, set_id=None):
        page = 1
        cards = []
        
        while True:
            params = {"page": page, "size": 100}
            if set_id:
                params["set_id"] = set_id
            
            response = requests.get(f"{cls.BASE_URL}/cards", params=params)
            response.raise_for_status()
            data = response.json()
            
            cards.extend(data["items"])
            
            if page >= data["pages"]:
                break
            
            page += 1
        
        logger.info(f"Fetched {len(cards)} cards from API")
        return cards
    
    @classmethod
    def get_sets(cls):
        return cls._get("sets")["items"]
    
    @classmethod
    def get_tags(cls):
        return cls._get("index/tags")["values"]
    
    @classmethod
    def get_types(cls):
        return cls._get("index/card-types")["values"]
    
    @classmethod
    def get_supertypes(cls):
        return cls._get("index/card-supertypes")["values"]
    
    @classmethod
    def get_rarities(cls):
        return cls._get("index/rarities")["values"]
    
    @classmethod
    def get_domains(cls):
        return cls._get("index/domains")["values"]

    @classmethod
    def get_keywords(cls):
        return cls._get("index/keywords")["values"]
