import re
from datetime import datetime
from apps.cards.models import Card, Set, Tag, Type, Rarity, Domain, Keyword
from .api_client import RiftboundApiClient

import logging
logger = logging.getLogger(__name__)


class CardSyncService:
    @classmethod
    def sync_sets(cls):
        sets_data = RiftboundApiClient.get_sets()
        
        for set_data in sets_data:
            Set.objects.update_or_create(
                set_id=set_data["set_id"],
                defaults={
                    "name": set_data["name"],
                    "release_date": datetime.fromisoformat(set_data["published_on"]).date(),
                    "card_count": set_data["card_count"],
                    "tcgplayer_id": set_data["tcgplayer_id"],
                }
            )
            
        logger.info(f"Synced {len(sets_data)} sets")
        
    @classmethod
    def sync_tags(cls):
        tags_data = RiftboundApiClient.get_tags()
        
        for tag_name in tags_data:
            Tag.objects.get_or_create(name=tag_name)
            
        logger.info(f"Synced {len(tags_data)} tags")
        
    @classmethod
    def sync_types(cls):
        types_data = RiftboundApiClient.get_types()
        supertypes_data = RiftboundApiClient.get_supertypes()
        
        for type_name in types_data:
            Type.objects.get_or_create(type=type_name, supertype=None)
        
        for type_name in types_data:
            for supertype_name in supertypes_data:
                Type.objects.get_or_create(type=type_name, supertype=supertype_name)
            
        logger.info(f"Synced {len(types_data)} types and {len(supertypes_data)} supertypes")
        
    @classmethod
    def sync_rarities(cls):
        rarities_data = RiftboundApiClient.get_rarities()
        
        for rarity_name in rarities_data:
            Rarity.objects.get_or_create(name=rarity_name)
            
        logger.info(f"Synced {len(rarities_data)} rarities")
        
    @classmethod
    def sync_domains(cls):
        domains_data = RiftboundApiClient.get_domains()
        
        for domain_name in domains_data:
            Domain.objects.get_or_create(name=domain_name)
            
        logger.info(f"Synced {len(domains_data)} domains")
        
    @classmethod
    def sync_keywords(cls):
        keywords_data = RiftboundApiClient.get_keywords()
        
        for keyword_name in keywords_data:
            if keyword_name.isdigit():
                logger.warning(f"Skipping invalid keyword: {keyword_name}")
                continue
            Keyword.objects.get_or_create(name=keyword_name.title())
            
        logger.info(f"Synced {len(keywords_data)} keywords")
    
    @classmethod
    def sync_reference_data(cls):
        logger.info("Starting reference data sync...")
        cls.sync_sets()
        cls.sync_tags()
        cls.sync_types()
        cls.sync_rarities()
        cls.sync_domains()
        cls.sync_keywords()
        logger.info("Reference data sync completed!")
        
    @classmethod
    def sync_cards(cls, set_id=None):
        cards_data = RiftboundApiClient.get_cards(set_id=set_id)
        
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
                created = cls._sync_card(card_data, sets, rarities, types, tags, domains, keywords)
                if created:
                    created_count += 1
                else:
                    updated_count += 1
            except Exception as e:
                logger.error(f"Failed to sync card {card_data['name']} (ID: {card_data['id']}): {str(e)}")
                failed_count += 1
        
        logger.info(f"Cards sync completed! Created: {created_count}, Updated: {updated_count}, Failed: {failed_count}")
        return created_count, updated_count, failed_count
    
    @classmethod
    def _sync_card(cls, data, sets, rarities, types, tags, domains, keywords):
        classification = data["classification"]
        attributes = data["attributes"]
        text = data["text"]
        media = data["media"]
        set_data = data["set"]
        metadata = data["metadata"]

        card_set = sets[set_data["set_id"]]
        rarity = rarities[classification["rarity"]]
        type_obj = types[(classification["type"], classification.get("supertype"))]

        card_tags = [tags[name] for name in data.get("tags", []) if name in tags]
        card_domains = [domains[name] for name in classification.get("domain", []) if name in domains]
        
        extracted_keywords = cls._extract_keywords(text.get("plain", ""), keywords)        

        card, created = Card.objects.update_or_create(
            external_api_id=data["id"],
            defaults={
                "name": data["name"],
                "riftbound_id": data["riftbound_id"],
                "tcgplayer_id": data["tcgplayer_id"],
                "might": attributes.get("might", 0),
                "energy_cost": attributes.get("energy", 0),
                "power_cost": attributes.get("power", 0),
                "body_text": text.get("plain", ""),
                "flavour_text": text.get("flavour", "") or "",
                "variant": cls._resolve_variant(metadata),
                "artist": media.get("artist", ""),
                "image_url": media.get("image_url", ""),
                "type": type_obj,
                "rarity": rarity,
                "set": card_set,
            }
        )

        card.tags.set(card_tags)
        card.domains.set(card_domains)
        card.keywords.set(extracted_keywords)

        return created
    
    @staticmethod
    def _resolve_variant(metadata):
        parts = []
        if metadata.get("alternate_art"):
            parts.append("Alternate Art")
        if metadata.get("overnumbered"):
            parts.append("Overnumbered")
        if metadata.get("signature"):
            parts.append("Signature")
        return " + ".join(parts) if parts else None
    
    @staticmethod
    def _extract_keywords(body_text, keywords):
        found_keywords = re.findall(r'\[([^\]]+)\]', body_text)
        result_keywords = []
        for kw in found_keywords:
            normalized_keyword = re.sub(r'\s*\d+$', ' ', kw).strip()
            if normalized_keyword in keywords:
                result_keywords.append(keywords[normalized_keyword])
        return result_keywords
