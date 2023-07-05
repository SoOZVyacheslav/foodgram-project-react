from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint

User = get_user_model()


class Ingredient(models.Model):
    """Модель ингредиентов."""
    name = models.CharField(
        max_length=254,
        db_index=True,
        blank=False,
        verbose_name='Название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=254,
        blank=False,
        verbose_name='Единицы измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    """Модель тегов."""
    name = models.CharField(
        max_length=254,
        unique=True,
        blank=False,
        verbose_name='Название тега',
    )
    color = models.CharField(
        max_length=7,
        unique=True,
        verbose_name='Цвет тега HEX',
    )
    slug = models.SlugField(
        max_length=254,
        unique=True,
        db_index=True,
        verbose_name='Слаг URL'
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта."""
    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта',
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Aвтор',
    )
    image = models.ImageField(
        upload_to='recipes/',
        help_text='Фото рецепта',
        verbose_name='Фото',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(1), ],
        verbose_name='Время приготовления',
        help_text='минут'
    )
    tags = models.ManyToManyField(
        Tag,
        blank=False,
        related_name='recipes',
        verbose_name='Теги'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe')

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)
        constraints = [
            UniqueConstraint(fields=['name', 'author'],
                             name='unique_recipes')
        ]

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    """Модель количества ингредиентов в рецепте."""
    recipe = models.ForeignKey(
        Recipe,
        null=True,
        on_delete=models.CASCADE,
        related_name='ingredient_recipes'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        null=True,
        on_delete=models.SET_NULL,
        related_name='ingredient_recipes'
    )
    amount = models.PositiveIntegerField(
        validators=[MinValueValidator(1), ],
        blank=False,
        null=False,
        verbose_name='Количество'
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        constraints = [
            UniqueConstraint(fields=['ingredient', 'recipe'],
                             name='unique_ingredient_recipe')
        ]


class Favorite(models.Model):
    """Модель избранное."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Рецепт в избранном',
        help_text='Рецепт в избранном',
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            UniqueConstraint(fields=['user', 'recipe'],
                             name='unique_favorite')
        ]


class ShoppingCart(models.Model):
    """Модель список покупок/корзина."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cart'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='cart'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        constraints = [
            UniqueConstraint(fields=['user', 'recipe'],
                             name='unique_cart')
        ]
