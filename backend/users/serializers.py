from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from users.models import Subscription
from recipes.models import Recipe

User = get_user_model()


class UserCustomCreateSerializer(UserCreateSerializer):
    """Сериализатор регистрации User."""
    username = serializers.RegexField(
        regex=r"^[\w.@+-]+\Z", required=False, max_length=150)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name',
                  'email', 'password', 'id',)


class UserCustomSerializer(UserSerializer):
    """Сериализатор модели User."""
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes',)
        lookup_field = 'id'

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return (
            user.following.filter(author=obj).exists()
            if user.is_authenticated
            else False
        )

    def get_recipes(self, obj):
        queryset = Recipe.objects.filter(author=obj.id)
        return SubscribeRecipeSerializer(queryset, many=True).data


class SubscribeRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор модели рецепта в подписках."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор подписок."""
    is_subscribed = serializers.ReadOnlyField(default=True)
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count',)

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if not user:
            return False
        return Subscription.objects.filter(user=user, author=obj).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit_recipes = request.query_params.get('recipes_limit')
        if limit_recipes is not None:
            recipes = obj.recipes.all()[:(int(limit_recipes))]
        else:
            recipes = obj.recipes.all()
        context = {'request': request}
        return SubscribeRecipeSerializer(recipes, many=True,
                                         context=context).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()
