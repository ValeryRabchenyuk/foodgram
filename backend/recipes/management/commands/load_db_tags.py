import json

from django.core.management.base import BaseCommand
from tqdm import tqdm

from recipes.models import Tag


class Command(BaseCommand):
    """Загружает списки ингредиентов и тегов из CSV файлов в базу данных."""
    help = 'Загрузка данных из CSV-файлов в базу данных'

    def handle(self, *args, **options):

        tags_file_path = os.path.join(
            settings.BASE_DIR, 'data', 'tags.csv'
        )
        with open(tags_file_path, encoding='utf-8') as csv_file:
            csv_reader = reader(csv_file)
            for row in csv_reader:
                Tag.objects.update_or_create(
                    name=row[0].strip(),
                    slug=row[1].strip()
                )
        self.stdout.write(self.style.SUCCESS('Список тегов загружен!'))


            def handle(self, *args, **options):

        with open(PATH_TO_INGREDIENTS, encoding='UTF-8') as ingrrdietnds_file:
            ingredients = json.load(ingrrdietnds_file)

            for ingridient in tqdm(ingredients):
                try:
                    Ingredient.objects.get_or_create(**ingridient)
                except CommandError as e:
                    raise CommandError(
                        f'Ошибка {e} при добавлении {ingridient}.')