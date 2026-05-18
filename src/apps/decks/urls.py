from django.urls import path

from .views import DeckListView, DeckDetailView, LikeDeckView, ViewDeckView, DeckValidateView, PublicDeckListView


url_patterns = [
    path('/decks/', DeckListView.as_view(), name='deck_list'),
    path('/decks/', DeckListView.as_view(), name='create_deck'),
    path('/decks/<deck_id>/', DeckDetailView.as_view(), name='deck_detail'),
    path('/decks/<deck_id>/', DeckDetailView.as_view(), name='update_deck'),
    path('/decks/<deck_id>/', DeckDetailView.as_view(), name='delete_deck'),
    path('/decks/<deck_id>/like/', LikeDeckView.as_view(), name='like_deck'),
    path('/decks/<deck_id>/view/', ViewDeckView.as_view(), name='view_deck'),
    path('/decks/validate/', DeckValidateView.as_view(), name='validate_deck'),
    path('/decks/public/', PublicDeckListView.as_view(), name='public_deck_list'),
]