from drf_base64.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from users.models import User
from users.serializers import UserCustomSerializer

from recipes.models import (
    Favorite, Ingredient, IngredientRecipe, Recipe, ShoppingCart, Tag,
)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов в рецепте."""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientRecipe
        fields = (
            'id', 'name', 'measurement_unit', 'amount',)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""

    class Meta:
        model = Tag
        fields = '__all__'


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для списка избранного."""
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = Favorite
        fields = ('user', 'recipe',)


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для списка покупок."""
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe',)


class IngredientEditSerializer(serializers.ModelSerializer):
    """Сериализатор для редактирование ингредиентов в рецепте."""
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')

    def validate_amount(self, value):
        if value < 1:
            raise serializers.ValidationError(
                'Количество ингредиента должно быть больше 1!'
            )
        return value


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор модели рецепта."""
    tags = TagSerializer(many=True)
    author = UserCustomSerializer()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    ingredients = IngredientRecipeSerializer(
        many=True,
        required=True,
        source='ingredient_recipes'
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Favorite.objects.filter(recipe=obj, user=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(recipe=obj,
                                           user=request.user).exists()


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для добавление рецепта."""
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all())
    ingredients = IngredientEditSerializer(many=True)
    author = UserCustomSerializer(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'name', 'image',
                  'text', 'ingredients', 'cooking_time',)

    def to_representation(self, instance):
        serializer = RecipeSerializer(instance, context=self.context)
        return serializer.data

    def add_ingredients(self, recipe, ingredients):
        IngredientRecipe.objects.bulk_create([
            IngredientRecipe(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount')
            ) for ingredient in ingredients])

    def validate_ingredient(self, data):
        ingredients = data['ingredients']
        if not ingredients:
            raise ValidationError(
                'Необходим хотя бы 1 ингредиент.')
        unique_ingredients = []
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            if ingredient_id not in unique_ingredients:
                unique_ingredients.append(ingredient_id)
            else:
                raise ValidationError(
                    'Такой ингредиент уже есть.')
        return data

    def validate_time(self, data):
        cooking_time = data['cooking_time']
        if int(cooking_time) <= 1:
            raise ValidationError(
                'Время приготовления должно быть больше 1.')
        return data

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        cooking_time = validated_data.pop('cooking_time')
        author = self.context['request'].user
        new_recipe = Recipe.objects.create(
            author=author,
            cooking_time=cooking_time,
            **validated_data
        )
        new_recipe.tags.set(tags)
        self.add_ingredients(new_recipe, ingredients)
        return new_recipe

    def update(self, recipe, validated_data):
        if validated_data['ingredients']:
            ingredients = validated_data.pop('ingredients')
            recipe.ingredient_recipes.all().delete()
            self.add_ingredients(recipe, ingredients)
        tags = validated_data.pop('tags')
        recipe.tags.set(tags)
        return super().update(recipe, validated_data)


class RecipeListSerializer(serializers.ModelSerializer):
    """Сериализатор просмотра рецептов."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)
