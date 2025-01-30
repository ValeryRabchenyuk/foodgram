from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

USERNAME_MAX_LENGTH = 150
EMAIL_MAX_LENGTH = 254


class User(AbstractUser):

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
        related_name='subscriptions',
        verbose_name='Подписчик')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Автор')

    class Meta:
        unique_together = ('subscriber', 'author')
        verbose_name = 'Подписки'
    
    def __str__(self):
        return f'Вы подписались на {self.author}'