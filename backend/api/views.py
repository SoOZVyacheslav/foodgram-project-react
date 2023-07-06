from datetime import date

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .filters import IngredientFilter, RecipeFilter
from .pagination import CustomPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    FavoriteSerializer, IngredientSerializer, RecipeCreateSerializer,
    RecipeListSerializer, TagSerializer,
)
from recipes.models import (
    Favorite, Ingredient, IngredientRecipe, Recipe, ShoppingCart, Tag,
)


class TagViewSet(ReadOnlyModelViewSet):
    """Вьюсет тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(ModelViewSet):
    """Вьюсет ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = [IsAuthorOrReadOnly]
    filter_backends = (IngredientFilter,)
    search_fields = ('^name',)


class RecipeViewSet(ModelViewSet):
    """Вьюсет рецептов."""
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filter_class = RecipeFilter
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action == 'favorite' or self.action == 'cart':
            return FavoriteSerializer
        return RecipeCreateSerializer

    def get_queryset(self):
        queryset = Recipe.objects.all()
        author = self.request.user
        if self.request.GET.get('is_favorited'):
            favorite_recipes_ids = Favorite.objects.filter(
                user=author).values('recipe_id')

            return queryset.filter(pk__in=favorite_recipes_ids)

        if self.request.GET.get('is_in_shopping_cart'):
            cart_recipes_ids = ShoppingCart.objects.filter(
                user=author).values('recipe_id')
            return queryset.filter(pk__in=cart_recipes_ids)
        return queryset

    def post_list(self, model, user, pk):
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response(
                {'errors': f'Рецепт уже добавлен в {model.__name__}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        recipe = get_object_or_404(Recipe, pk=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = RecipeListSerializer(recipe)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED)

    def delete_list(self, model, user, pk):
        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': f'Рецепт не добавлен в {model.__name__}'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(methods=['post', 'delete'], detail=True,
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk=None):
        if request.method == 'POST':
            return self.post_list(Favorite, request.user, pk)
        return self.delete_list(Favorite, request.user, pk)

    @action(methods=['post', 'delete'], detail=True,
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk=None):
        if request.method == 'POST':
            return self.post_list(ShoppingCart, request.user, pk)
        return self.delete_list(ShoppingCart, request.user, pk)

    @action(
        detail=False,
        permission_classes=[permissions.IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        user = request.user
        if not user.cart.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        ingredients = IngredientRecipe.objects.filter(
            recipe__cart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))

        shopping_list = (
            f'Список покупок для: {user.get_full_name()}\n\n'
            f'Дата: {date.today()}\n\n'
        )
        shopping_list += '\n'.join([
            f'- {ingredient["ingredient__name"]} '
            f'({ingredient["ingredient__measurement_unit"]})'
            f' - {ingredient["amount"]}'
            for ingredient in ingredients
        ])

        filename = 'shopping_list'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
