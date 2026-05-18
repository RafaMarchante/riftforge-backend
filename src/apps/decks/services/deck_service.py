from django.db.models import Count, F, FloatField, ExpressionWrapper
from django.db.models.functions import Extract
from django.shortcuts import get_object_or_404
from django.utils import timezone

from apps.decks.models import Deck, DeckLike, DeckView
from apps.decks.serializers import DeckWriteSerializer, DeckDetailSerializer, DeckListSerializer

import logging
logger = logging.getLogger(__name__)


class DeckService:
    @staticmethod
    def list_user_decks(user):
        return Deck.objects.filter(user=user).annotate(
            likes_count=Count('likes'),
            views_count=Count('views'),
            card_count=Count('deck_cards'),
        )
        
    @staticmethod
    def list_public_decks():
        now = timezone.now()
        return Deck.objects.filter(is_public=True).annotate(
            likes_count=Count('likes', distinct=True),
            views_count=Count('views', distinct=True),
            card_count=Count('deck_cards', distinct=True),
            age_hours=ExpressionWrapper(
                Extract(now - F('created_at'), 'epoch') / 3600,
                output_field=FloatField()
            ),
        ).annotate(
            trending_score=ExpressionWrapper(
                (F('likes_count') * 3.0 + F('views_count')) / (F('age_hours') + 2.0),
                output_field=FloatField()
            )
        ).order_by('-trending_score')
        
    @staticmethod
    def get_deck(deck_id, user=None):
        queryset = Deck.objects.annotate(
            likes_count=Count('likes', distinct=True),
            views_count=Count('views', distinct=True)
        ).select_related('user').prefetch_related('deck_cards__card')
        
        deck = get_object_or_404(queryset, id=deck_id)
        
        if not deck.is_public and deck.user != user:
            raise PermissionError("You do not have permission to view this deck.")
        return deck

    @staticmethod
    def create_deck(user, data):
        serializer = DeckWriteSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        deck = serializer.save(user=user)
        return deck
    
    @staticmethod
    def update_deck(deck_id, user, data):
        deck = get_object_or_404(Deck, id=deck_id, user=user)
        if not deck.is_public and deck.user != user:
            raise PermissionError("You do not have permission to update this deck.")
        
        serializer = DeckWriteSerializer(deck, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_deck = serializer.save()
        return updated_deck
    
    @staticmethod
    def delete_deck(deck_id, user):
        deck = get_object_or_404(Deck, id=deck_id, user=user)
        if not deck.is_public and deck.user != user:
            raise PermissionError("You do not have permission to delete this deck.")
        
        deck.delete()

    @staticmethod
    def toggle_like(deck_id, user):
        deck = get_object_or_404(Deck, id=deck_id, is_public=True)
        like, created = DeckLike.objects.get_or_create(user=user, deck=deck)
        if not created:
            like.delete()
            return False
        return True
    
    @staticmethod
    def register_view(deck_id, user):
        deck = get_object_or_404(Deck, id=deck_id, is_public=True)
        DeckView.objects.get_or_create(user=user, deck=deck)
