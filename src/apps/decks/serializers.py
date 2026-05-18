from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Deck, DeckCard
from apps.cards.models import Card

User = get_user_model()


class DeckCardSerializer(serializers.ModelSerializer):
    card_id = serializers.UUIDField()

    class Meta:
        model = DeckCard
        fields = ['card_id', 'quantity']


class DeckListSerializer(serializers.ModelSerializer):
    likes_count = serializers.IntegerField(read_only=True)
    views_count = serializers.IntegerField(read_only=True)
    card_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Deck
        fields = ['id', 'name', 'description', 'is_public', 'likes_count', 'views_count', 'card_count', 'created_at', 'updated_at']


class DeckDetailSerializer(serializers.ModelSerializer):
    likes_count = serializers.IntegerField(read_only=True)
    views_count = serializers.IntegerField(read_only=True)
    cards = DeckCardSerializer(source='deck_cards', many=True, read_only=True)

    class Meta:
        model = Deck
        fields = ['id', 'name', 'description', 'is_public', 'likes_count', 'views_count', 'cards', 'created_at', 'updated_at']


class DeckWriteSerializer(serializers.ModelSerializer):
    cards = DeckCardSerializer(many=True)

    class Meta:
        model = Deck
        fields = ['name', 'description', 'is_public', 'cards']

    def validate_cards(self, cards):
        card_ids = [c['card_id'] for c in cards]

        existing_card_number = Card.objects.filter(id__in=card_ids).count()
        if existing_card_number != len(card_ids):
            raise serializers.ValidationError("One or more cards do not exist")

        if len(card_ids) != len(set(card_ids)):
            raise serializers.ValidationError("Duplicate cards are not allowed")

        return cards

    def create(self, validated_data):
        cards_data = validated_data.pop('cards')
        deck = Deck.objects.create(**validated_data)
        self._set_cards(deck, cards_data)
        return deck

    def update(self, instance, validated_data):
        cards_data = validated_data.pop('cards', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if cards_data is not None:
            instance.deck_cards.all().delete()
            self._set_cards(instance, cards_data)
        return instance

    @staticmethod
    def _set_cards(deck, cards_data):
        DeckCard.objects.bulk_create([
            DeckCard(
                deck=deck,
                card_id=card_data['card_id'],
                quantity=card_data['quantity'],
            )
            for card_data in cards_data
        ])
