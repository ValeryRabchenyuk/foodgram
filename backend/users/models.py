from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from .constants import EMAIL_MAX_LENGTH, USERNAME_MAX_LENGTH


class User(AbstractUser):

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name', 'password')

    username = models.CharField(
        max_length=USERNAME_MAX_LENGTH,
        unique=True,
        blank=False,
        verbose_name='Имя пользователя',
        validators=[RegexValidator(
            regex=r'^[\w.@+-]+$',
            message='Имя пользователя содержит недопустимый символ')])

    email = models.EmailField(
        max_length=EMAIL_MAX_LENGTH,
        unique=True,
        blank=False,
        verbose_name='Адрес электронной почты')

    first_name = models.CharField(
        max_length=USERNAME_MAX_LENGTH,
        blank=True,
        verbose_name='Имя')

    last_name = models.CharField(
        max_length=USERNAME_MAX_LENGTH,
        blank=True,
        verbose_name='Фамилия')

    password = models.CharField(
        max_length=USERNAME_MAX_LENGTH,
        blank=False,
        null=False,
        verbose_name='Пароль')

    avatar = models.ImageField(
        verbose_name='Аватарка',
        upload_to='users/avatars/',
        null=True,
        default=None)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username


class Subscription(models.Model):

    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик')

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор')

    class Meta:
        unique_together = ('subscriber', 'author')      # UniqueConstraint у нормальных людей
        verbose_name = 'Подписки'
        default_related_name = 'subscription'

    def __str__(self):
        return f'Вы подписались на {self.author}'
