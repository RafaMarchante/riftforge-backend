import re
from datetime import datetime

from packaging import tags
from apps.cards.models import Card, Set, Tag, Type, Rarity, Domain, Keyword
from .clients.riftcodex_client import RiftcodexApiClient

import logging
logger = logging.getLogger(__name__)


RARITY_ORDER = {
    'Common': 1,
    'Uncommon': 2,
    'Rare': 3,
    'Epic': 4,
    'Showcase': 5,
    'Promo': 6,
}


class CardSyncService:
    def __init__(self, api_client=None):
        self.api_client = api_client or RiftcodexApiClient()
        
    def sync_sets(self):
        sets_data = self.api_client.get_sets()
        
        for set_data in sets_data:
            Set.objects.update_or_create(
                set_id=set_data.set_id,
                defaults={
                    "name": set_data.name,
                    "release_date": datetime.fromisoformat(set_data.release_date).date(),
                    "card_count": set_data.card_count,
                    "tcgplayer_id": set_data.tcgplayer_id,
                }
            )
            
        logger.info(f"Synced {len(sets_data)} sets")
        
    def sync_tags(self):
        tags_data = self.api_client.get_tags()
        
        for tag_name in tags_data:
            Tag.objects.get_or_create(name=tag_name)
            
        logger.info(f"Synced {len(tags_data)} tags")
        
    def sync_types(self):
        types_data = self.api_client.get_types()
        supertypes_data = self.api_client.get_supertypes()
        
        for type_name in types_data:
            Type.objects.get_or_create(type=type_name, supertype=None)
        
        for type_name in types_data:
            for supertype_name in supertypes_data:
                Type.objects.get_or_create(type=type_name, supertype=supertype_name)
            
        logger.info(f"Synced {len(types_data)} types and {len(supertypes_data)} supertypes")
        
    def sync_rarities(self):
        rarities_data = self.api_client.get_rarities()
        
        for rarity_name in rarities_data:
            Rarity.objects.get_or_create(
                name=rarity_name,
                order=RARITY_ORDER.get(rarity_name, 999),
                )
            
        logger.info(f"Synced {len(rarities_data)} rarities")
        
    def sync_domains(self):
        domains_data = self.api_client.get_domains()
        
        for domain_name in domains_data:
            Domain.objects.get_or_create(name=domain_name)
            
        logger.info(f"Synced {len(domains_data)} domains")
        
    def sync_keywords(self):
        keywords_data = self.api_client.get_keywords()
        
        for keyword_name in keywords_data:
            if keyword_name.isdigit():
                logger.warning(f"Skipping invalid keyword: {keyword_name}")
                continue
            Keyword.objects.get_or_create(name=keyword_name.title())
            
        logger.info(f"Synced {len(keywords_data)} keywords")
    
    def sync_reference_data(self):
        logger.info("Starting reference data sync...")
        self.sync_sets()
        self.sync_tags()
        self.sync_types()
        self.sync_rarities()
        self.sync_domains()
        self.sync_keywords()
        logger.info("Reference data sync completed!")
        
    def sync_cards(self, set_id=None):
        cards_data = self.api_client.get_cards(set_id=set_id)
        
        # pre-fetch related data to minimize DB query hits
        sets = {s.set_id: s for s in Set.objects.all()}
        rarities = {r.name: r for r in Rarity.objects.all()}
        types = {(t.type, t.supertype): t for t in Type.objects.all()}
        tags = {t.name: t for t in Tag.objects.all()}
        domains = {d.name: d for d in Domain.objects.all()}
        keywords = {k.name: k for k in Keyword.objects.all()}
        
        created_count = 0
        updated_count = 0
        failed_count = 0
        
        for card_data in cards_data:
            try:
                created = self._sync_card(card_data, sets, rarities, types, tags, domains, keywords)
                if created:
                    created_count += 1
                else:
                    updated_count += 1
            except Exception as e:
                logger.error(f"Failed to sync card {card_data.name} (ID: {card_data.external_api_id}): {str(e)}")
                failed_count += 1
        
        logger.info(f"Cards sync completed! Created: {created_count}, Updated: {updated_count}, Failed: {failed_count}")
        return created_count, updated_count, failed_count
    
    def _sync_card(self, card_data, sets, rarities, types, tags, domains, keywords):
        card_set = sets[card_data.set_id]
        rarity = rarities[card_data.rarity]
        type_obj = types[(card_data.type, card_data.supertype)]

        card_tags = [tags[name] for name in card_data.tags if name in tags]
        card_domains = [domains[name] for name in card_data.domains if name in domains]
        card_keywords = [keywords[name] for name in card_data.keywords if name in keywords]
        
        card, created = Card.objects.update_or_create(
            external_api_id=card_data.external_api_id,
            defaults={
                "name": card_data.name,
                "riftbound_id": card_data.riftbound_id,
                "tcgplayer_id": card_data.tcgplayer_id,
                "might": card_data.might,
                "energy_cost": card_data.energy_cost,
                "power_cost": card_data.power_cost,
                "body_text": card_data.body_text,
                "flavour_text": card_data.flavour_text,
                "variant": card_data.variant,
                "artist": card_data.artist,
                "image_url": card_data.image_url,
                "type": type_obj,
                "rarity": rarity,
                "set": card_set,
            }
        )

        card.tags.set(card_tags)
        card.domains.set(card_domains)
        card.keywords.set(card_keywords)

        return created
    