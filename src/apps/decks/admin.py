from django.contrib import admin

from .models import Deck, DeckCard, DeckLike, DeckView


class DeckAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'user')
    search_fields = ('name', 'user')
    ordering = ('name',)
    
    
class DeckCardAdmin(admin.ModelAdmin):
    list_display = ('deck', 'card', 'quantity')
    search_fields = ('deck__name', 'card__name')
    ordering = ('deck__name', 'card__name')
    
    
class DeckLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'deck', 'created_at')
    search_fields = ('user__email', 'deck__name')
    ordering = ('-created_at',)
    
    
class DeckViewAdmin(admin.ModelAdmin):
    list_display = ('user', 'deck', 'created_at')
    search_fields = ('user__email', 'deck__name')
    ordering = ('-created_at',)
    

admin.site.register(Deck, DeckAdmin)
admin.site.register(DeckCard, DeckCardAdmin)
admin.site.register(DeckLike, DeckLikeAdmin)
admin.site.register(DeckView, DeckViewAdmin)
