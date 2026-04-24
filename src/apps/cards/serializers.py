from rest_framework import serializers
from .models import Card, Type, Rarity, Set, Domain, Tag, Keyword


class TypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Type
        fields = ['type']
        
        
class SupertypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Type
        fields = ['supertype']


class RaritySerializer(serializers.ModelSerializer):
    class Meta:
        model = Rarity
        fields = ['name']


class SetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Set
        fields = ['name', 'set_id', 'release_date', 'tcgplayer_id', 'card_count']


class DomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Domain
        fields = ['name']
        
        
class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['name']
        
        
class KeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Keyword
        fields = ['name']


class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = ['id', 'name', 'image_url']
        

class CardDetailSerializer(CardSerializer):
    type = TypeSerializer()
    rarity = RaritySerializer()
    set = SetSerializer()
    domains = serializers.StringRelatedField(many=True)
    tags = serializers.StringRelatedField(many=True)
    keywords = serializers.StringRelatedField(many=True)
    
    class Meta(CardSerializer.Meta):
        fields = [
            'id', 'name', 'riftbound_id', 'image_url',
            'might', 'energy_cost', 'power_cost',
            'body_text', 'flavour_text', 'artist',
            'variant', 'type', 'rarity', 'set',
            'domains', 'tags', 'keywords',
        ]
