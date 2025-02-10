import json

from django.core.management.base import BaseCommand, CommandError
from tqdm import tqdm

from api_foodgram.settings import PATH_TO_TAGS
from recipes.models import Tag


class Command(BaseCommand):
    """Заполнение базы тегами."""

    def handle(self, *args, **options):

        with open(PATH_TO_TAGS, encoding='UTF-8') as tag_file:
            tags = json.load(tag_file)

            for tag in tqdm(tags):
                try:
                    Tag.objects.get_or_create(**tag)
                except CommandError as e:
                    raise CommandError(
                        f'Ошибка {e} при добавлении {tag}.')
