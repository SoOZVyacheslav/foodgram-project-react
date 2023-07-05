import pandas as pd
from django.core.management.base import BaseCommand

from recipes.models import Ingredient, Tag


class Command(BaseCommand):

    def handle(self, *args, **options):
        ings_data = pd.read_csv('./data/ingredients.csv', sep=",")
        row_iter = ings_data.iterrows()
        ingredients = [
            Ingredient(
                name=row['name'],
                measurement_unit=row['measurement_unit']
            )
            for index, row in row_iter
        ]
        Ingredient.objects.bulk_create(ingredients)

        tag_data = pd.read_csv('./data/tags.csv', sep=",")
        row_iter = tag_data.iterrows()
        tags = [
            Tag(
                name=row['name'],
                color=row['color'],
                slug=row['slug'],
            )
            for index, row in row_iter
        ]
        Tag.objects.bulk_create(tags)

    print('Данные успешно импортированы!')
