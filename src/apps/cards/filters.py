import django_filters
from .models import Card, Type, Rarity, Set, Domain, Tag, Keyword


class CardFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    type = django_filters.ModelMultipleChoiceFilter(field_name='type__type', to_field_name='type', queryset=Type.objects.all())
    supertype = django_filters.ModelMultipleChoiceFilter(field_name='type__supertype', to_field_name='supertype', queryset=Type.objects.all())
    rarity = django_filters.ModelMultipleChoiceFilter(field_name='rarity__name', to_field_name='name', queryset=Rarity.objects.all())
    set = django_filters.ModelMultipleChoiceFilter(field_name='set__set_id', to_field_name='set_id', queryset=Set.objects.all())
    domains = django_filters.ModelMultipleChoiceFilter(field_name='domains__name', to_field_name='name', queryset=Domain.objects.all())
    tags = django_filters.ModelMultipleChoiceFilter(field_name='tags__name', to_field_name='name', queryset=Tag.objects.all())
    keywords = django_filters.ModelMultipleChoiceFilter(field_name='keywords__name', to_field_name='name', queryset=Keyword.objects.all())

    might_min = django_filters.NumberFilter(field_name='might', lookup_expr='gte')
    might_max = django_filters.NumberFilter(field_name='might', lookup_expr='lte')
    energy_min = django_filters.NumberFilter(field_name='energy_cost', lookup_expr='gte')
    energy_max = django_filters.NumberFilter(field_name='energy_cost', lookup_expr='lte')
    power_min = django_filters.NumberFilter(field_name='power_cost', lookup_expr='gte')
    power_max = django_filters.NumberFilter(field_name='power_cost', lookup_expr='lte')

    class Meta:
        model = Card
        fields = [
            'name', 'rarity', 'type', 'set', 'domains', 'tags', 'keywords',
            'might_min', 'might_max', 'energy_min', 'energy_max', 'power_min', 'power_max',
        ]
