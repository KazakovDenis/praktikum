from uuid import uuid4

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.fields import AutoCreatedField, AutoLastModifiedField

from .signals import *


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    birth_date = models.DateTimeField(blank=True)


class Genre(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False, db_index=True)
    name = models.CharField(_('название'), max_length=255)
    description = models.TextField(_('описание'), blank=True, null=True)
    created_at = AutoCreatedField(_('добавлено'))
    updated_at = AutoLastModifiedField(_('обновлено'))

    class Meta:
        managed = False
        db_table = 'content"."genre'
        verbose_name = _('жанр')
        verbose_name_plural = _('жанры')

    def __str__(self):
        return self.name


class Person(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False, db_index=True)
    full_name = models.CharField(_('полное имя'), max_length=255)
    birth_date = models.DateField(_('дата рождения'), blank=True, null=True)
    created_at = AutoCreatedField(_('добавлено'))
    updated_at = AutoLastModifiedField(_('обновлено'))

    class Meta:
        managed = False
        db_table = 'content"."person'
        verbose_name = _('персоналии')
        verbose_name_plural = _('персоналии')

    def __str__(self):
        return self.full_name


class FilmWorkType(models.TextChoices):
    MOVIE = 'movie', _('фильм')
    SERIES = 'series', _('сериал')
    TV_SHOW = 'tv_show', _('телешоу')


class FilmWork(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False, db_index=True)
    title = models.CharField(_('название'), max_length=255)
    description = models.TextField(_('описание'), blank=True)
    creation_date = models.DateField(_('дата создания фильма'), blank=True, null=True)
    certificate = models.TextField(_('сертификат'), blank=True, null=True)
    file_path = models.FileField(_('файл'), upload_to='film_works/', blank=True)
    rating = models.FloatField(_('рейтинг'), validators=[MinValueValidator(0)], blank=True, null=True)
    type = models.CharField(_('тип'), choices=FilmWorkType.choices, max_length=255)
    created_at = AutoCreatedField(_('добавлено'))
    updated_at = AutoLastModifiedField(_('обновлено'))

    class Meta:
        managed = False
        db_table = 'content"."film_work'
        # db_tablespace = 'content'
        verbose_name = _('кинопроизведение')
        verbose_name_plural = _('кинопроизведения')

    def __str__(self):
        return self.title


class GenreFilmWork(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False, db_index=True)
    film_work = models.ForeignKey(
        FilmWork,
        verbose_name=_('кинопроизведение'),
        related_name='genre_film_work',
        on_delete=models.CASCADE,
    )
    genre = models.ForeignKey(
        Genre,
        verbose_name=_('жанр'),
        related_name='genre_film_work',
        on_delete=models.CASCADE,
    )
    created_at = AutoCreatedField(_('добавлено'))

    class Meta:
        managed = False
        db_table = 'content"."genre_film_work'
        verbose_name = _('связь фильмов и жанров')
        verbose_name_plural = _('связи фильмов и жанров')
        unique_together = (('film_work_id', 'genre_id'),)

    def __str__(self):
        return f'[{self.genre.name}] {self.film_work.title}'


class RoleType(models.TextChoices):
    ACTOR = 'Actor', _('актёр')
    DIRECTOR = 'Director', _('режиссёр')
    WRITER = 'Writer', _('сценарист')


class PersonFilmWork(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False, db_index=True)
    film_work = models.ForeignKey(
        FilmWork,
        verbose_name=_('кинопроизведение'),
        related_name='person_film_work',
        on_delete=models.CASCADE,
    )
    person = models.ForeignKey(
        Person,
        verbose_name=_('персона'),
        related_name='person_film_work',
        on_delete=models.CASCADE,
    )
    role = models.CharField(_('роль'), choices=RoleType.choices, max_length=255)
    created_at = AutoCreatedField(_('добавлено'))

    class Meta:
        managed = False
        db_table = 'content"."person_film_work'
        verbose_name = _('связь фильмов и персоналий')
        verbose_name_plural = _('связи фильмов и персоналий')
        unique_together = (('film_work_id', 'person_id', 'role'),)

    def __str__(self):
        return f'{self.person.full_name} as {self.role} @ "{self.film_work.title}"'
