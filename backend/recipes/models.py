from django.db import models
from django.core.validators import RegexValidator

from .constants import TAG_MAX_LENGTH


class Tag(models.Model):        # какое-то "id" должно быть

    name = models.CharField(
        max_length=TAG_MAX_LENGTH,
        unique=True,
        verbose_name='Название')

    slug = models.SlugField(
        max_length=TAG_MAX_LENGTH,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[-a-zA-Z0-9_]+$',
                message='Поле содержите недопустимый символ')])

    class Meta:
        verbose_name = 'Тег'

    def __str__(self):
        return self.name




                                   