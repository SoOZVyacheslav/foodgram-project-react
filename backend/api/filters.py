from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter

from recipes.models import Recipe, Tag


class IngredientFilter(SearchFilter):
    """Фильтр для выбора ингредиентов."""
    search_param = 'name'


class RecipeFilter(filters.FilterSet):
    """Фильтр сортировки рецептов."""
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
    )
    author = filters.CharFilter(lookup_expr='exact')
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='is_in_shopping_cart', method='filter'
    )
    is_favorited = filters.BooleanFilter(
        field_name='is_favorited', method='filter'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_in_shopping_cart', 'is_favorited',)

    def filter(self, queryset, name, value):
        if name == 'is_in_shopping_cart' and value:
            queryset = queryset.filter(
                cart__user=self.request.user
            )
        if name == 'is_favorited' and value:
            queryset = queryset.filter(
                favorite__user=self.request.user
            )
        return queryset
