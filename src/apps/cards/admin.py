from django.contrib import admin

from .models import Card, Type, Rarity, Set, Domain, Tag, Keyword


class CardAdmin(admin.ModelAdmin):
    list_display = ('name', 'riftbound_id', 'type', 'rarity', 'set')
    search_fields = ('name', 'riftbound_id')
    list_filter = ('type__type', 'type__supertype', 'rarity__name', 'set__name', 'domains__name', 'tags__name', 'keywords__name')
    

class TypeAdmin(admin.ModelAdmin):
    list_display = ('type', 'supertype')
    search_fields = ('type', 'supertype')
    list_filter = ('type', 'supertype')
    

class RarityAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
    search_fields = ('name',)
    ordering = ('order',)
    

class SetAdmin(admin.ModelAdmin):
    list_display = ('name', 'set_id', 'release_date')
    search_fields = ('name', 'set_id')
    ordering = ('release_date',)
    

class DomainAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)
    

class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)
    

class KeywordAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)
    

admin.site.register(Card, CardAdmin)
admin.site.register(Type, TypeAdmin)
admin.site.register(Rarity, RarityAdmin)
admin.site.register(Set, SetAdmin)
admin.site.register(Domain, DomainAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Keyword, KeywordAdmin)
