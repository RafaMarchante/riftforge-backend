from django.contrib.auth import get_user_model
from django.db.models import OuterRef, Subquery
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView, RetrieveAPIView

from .models import Card, Type, Rarity, Set, Domain, Tag, Keyword
from .serializers import (
    CardSerializer,
    CardDetailSerializer,
    TypeSerializer,
    SupertypeSerializer,
    RaritySerializer,
    SetSerializer,
    DomainSerializer,
    TagSerializer,
    KeywordSerializer)
from .filters import CardFilter
from .pagination import CardPagination

import logging
logger = logging.getLogger(__name__)


@method_decorator(ratelimit(key='ip', rate='5/m', method='GET', block=True), name='get')
class CardListView(ListAPIView):
    serializer_class = CardSerializer
    pagination_class = CardPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = CardFilter
    ordering = ['riftbound_id']

    def get_queryset(self):
        requested_domains = self.request.query_params.getlist('domains')
        
        domains_qs = Domain.objects.filter(cards=OuterRef('pk'))
        if requested_domains:
            domains_qs = domains_qs.filter(name__in=requested_domains)
        
        domain = domains_qs.order_by('name').values('name')[:1]
        
        return Card.objects.only('id', 'name', 'image_url').annotate(domain=Subquery(domain))


@method_decorator(ratelimit(key='ip', rate='10/m', method='GET', block=True), name='get')
class CardDetailView(RetrieveAPIView):
    serializer_class = CardDetailSerializer

    def get_queryset(self):
        return Card.objects.select_related(
            'type', 'rarity', 'set'
        ).prefetch_related(
            'domains', 'tags', 'keywords'
        )


@method_decorator(ratelimit(key='ip', rate='5/m', method='GET', block=True), name='get')
class CardTypesView(ListAPIView):
    serializer_class = TypeSerializer
    queryset = Type.objects.order_by('type').distinct('type')
    
    
@method_decorator(ratelimit(key='ip', rate='5/m', method='GET', block=True), name='get')
class CardSupertypesView(ListAPIView):
    serializer_class = SupertypeSerializer
    queryset = Type.objects.order_by('supertype').distinct('supertype').exclude(supertype__isnull=True)


@method_decorator(ratelimit(key='ip', rate='5/m', method='GET', block=True), name='get')
class CardRaritiesView(ListAPIView):
    serializer_class = RaritySerializer
    queryset = Rarity.objects.all()
    

@method_decorator(ratelimit(key='ip', rate='5/m', method='GET', block=True), name='get')
class CardSetsView(ListAPIView):
    serializer_class = SetSerializer
    queryset = Set.objects.all()
    
    
@method_decorator(ratelimit(key='ip', rate='5/m', method='GET', block=True), name='get')
class CardDomainsView(ListAPIView):
    serializer_class = DomainSerializer
    queryset = Domain.objects.all().exclude(name__exact='Colorless') # Colorless is not a real domain, it's just a catch-all for cards that don't fit into any other domain. We don't want to show it as an option in the filter dropdown.
    
    
@method_decorator(ratelimit(key='ip', rate='5/m', method='GET', block=True), name='get')
class CardTagsView(ListAPIView):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    
    
@method_decorator(ratelimit(key='ip', rate='5/m', method='GET', block=True), name='get')
class CardKeywordsView(ListAPIView):
    serializer_class = KeywordSerializer
    queryset = Keyword.objects.all()
