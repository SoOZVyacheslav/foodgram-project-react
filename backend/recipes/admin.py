from django.contrib import admin

from .models import (
    Favorite, Ingredient, IngredientRecipe, Recipe, ShoppingCart, Tag,
)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug',)
    list_filter = ('recipes',)
    prepopulated_fields = {'slug': ('name',)}


class IngredientRecipeInline(admin.TabularInline):
    model = IngredientRecipe


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_filter = ('author', 'tags')
    list_display = ('name', 'author', 'is_favorited',
                    'pub_date')
    search_fields = ('author', 'name', 'tags')
    inlines = [IngredientRecipeInline]

    def is_favorited(self, obj):
        return obj.favorite.count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    search_fields = ('name',)
    list_filter = ('measurement_unit',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
