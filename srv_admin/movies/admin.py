from django.contrib import admin
from .models import *


class GenreFilmWorkInline(admin.TabularInline):
    model = GenreFilmWork
    extra = 0


class PersonFilmWorkInline(admin.TabularInline):
    model = PersonFilmWork
    extra = 0


@admin.register(FilmWork)
class FilmWorkAdmin(admin.ModelAdmin):
    # отображение полей в списке
    list_display = ('title', 'type', 'creation_date', 'rating')
    # порядок следования полей в форме создания/редактирования

    # фильтрация в списке
    list_filter = ('type',)

    # поиск по полям
    search_fields = ('title', 'description', 'id')

    fields = (
        'title', 'type', 'description', 'creation_date', 'certificate',
        'file_path', 'rating'
    )

    inlines = [
        GenreFilmWorkInline, PersonFilmWorkInline
    ]


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', )
    list_filter = ('name', 'description')
    search_fields = ('name', 'description')
    fields = ('name', 'description')

    inlines = [
        GenreFilmWorkInline
    ]


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('full_name', )
    list_filter = ('full_name', 'birth_date')
    search_fields = ('full_name', 'birth_date')
    fields = ('full_name', 'birth_date')

    inlines = [
        PersonFilmWorkInline
    ]
