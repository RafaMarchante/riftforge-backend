from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from services.deck_service import DeckService
from .serializers import DeckListSerializer, DeckDetailSerializer, DeckWriteSerializer
from .pagination import DeckPagination

import logging
logger = logging.getLogger(__name__)


@method_decorator(ratelimit(key='ip', rate='10/m', method='GET', block=True), name='get')
@method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True), name='post')
class DeckListView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = DeckPagination
    
    def get(self, request):
        try:
            decks = DeckService.list_user_decks(request.user)
            paginator = self.pagination_class()
            deck_page = paginator.paginate_queryset(decks, request)
            serializer = DeckListSerializer(deck_page, many=True)
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            logger.error(f"Error ocurred: {e}")
            return Response({"error": "Failed to retrieve user decks"}, status=500)
        
    def post(self, request):
        try:
            deck = DeckService.create_deck(request.user, request.data)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)
        except Exception as e:
            logger.error(f"Error ocurred: {e}")
            return Response({"error": "Failed to create deck"}, status=500)
        serializer = DeckDetailSerializer(deck)
        return Response(serializer.data, status=201)
    
    
@method_decorator(ratelimit(key='ip', rate='10/m', method='GET', block=True), name='get')
@method_decorator(ratelimit(key='ip', rate='5/m', method='PATCH', block=True), name='patch')
@method_decorator(ratelimit(key='ip', rate='5/m', method='DELETE', block=True), name='delete')
class DeckDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, deck_id):
        try:
            deck = DeckService.get_deck(deck_id, request.user)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)
        except Exception as e:
            logger.error(f"Error occurred: {e}")
            return Response({"error": "Failed to retrieve deck"}, status=500)
        serializer = DeckDetailSerializer(deck)
        return Response(serializer.data)

    def post(self, request, deck_id):
        try:
            deck = DeckService.update_deck(deck_id, request.user)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)
        except Exception as e:
            logger.error(f"Error occurred: {e}")
            return Response({"error": "Failed to update deck"}, status=500)
        serializer = DeckDetailSerializer(deck)
        return Response(serializer.data)
        
    def delete(self, request, deck_id):
        try:
            DeckService.delete_deck(deck_id, request.user)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)
        except Exception as e:
            logger.error(f"Error occurred: {e}")
            return Response({"error": "Failed to delete deck"}, status=500)
        return Response(status=204)


@method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True), name='post')
class LikeDeckView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, deck_id):
        try:
            liked = DeckService.toggle_like(deck_id, request.user)
        except Exception as e:
            logger.error(f"Error occurred: {e}")
            return Response({"error": "Failed to like deck"}, status=500)
        return Response({"liked": liked})
    

@method_decorator(ratelimit(key='ip', rate='10/m', method='POST', block=True), name='post')
class ViewDeckView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, deck_id):
        try:
            DeckService.register_view(deck_id, request.user)
        except Exception as e:
            logger.error(f"Error occurred: {e}")
            return Response({"error": "Failed to like deck"}, status=500)
        return Response(status=204)


@method_decorator(ratelimit(key='ip', rate='10/m', method='GET', block=True), name='get')
class PublicDeckListView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = DeckPagination

    def get(self, request):
        try:
            decks = DeckService.list_public_decks()
            paginator = self.pagination_class()
            deck_page = paginator.paginate_queryset(decks, request)
            serializer = DeckListSerializer(deck_page, many=True)
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            logger.error(f"Error occurred: {e}")
            return Response({"error": "Failed to retrieve public decks"}, status=500)
