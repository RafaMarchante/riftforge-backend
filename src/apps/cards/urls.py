from django.urls import path
from .views import (
    CardListView,
    CardDetailView,
    CardTypesView,
    CardSupertypesView,
    CardRaritiesView,
    CardSetsView,
    CardDomainsView,
    CardTagsView,
    CardKeywordsView)


urlpatterns = [
    path('', CardListView.as_view(), name='card_list'),
    path('/<uuid:pk>', CardDetailView.as_view(), name='card_detail'),
    path('/types', CardTypesView.as_view(), name='card_types'),
    path('/supertypes', CardSupertypesView.as_view(), name='card_supertypes'),
    path('/rarities', CardRaritiesView.as_view(), name='card_rarities'),
    path('/sets', CardSetsView.as_view(), name='card_sets'),
    path('/domains', CardDomainsView.as_view(), name='card_domains'),
    path('/tags', CardTagsView.as_view(), name='card_tags'),
    path('/keywords', CardKeywordsView.as_view(), name='card_keywords'),
]
