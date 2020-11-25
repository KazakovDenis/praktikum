from django.contrib.postgres.aggregates import ArrayAgg
from django.core.paginator import InvalidPage
from django.db.models import Q, QuerySet
from django.http import JsonResponse, Http404
from django.utils.translation import gettext_lazy as _
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView

from ..models import FilmWork, RoleType


class MoviesApiMixin:
    model = FilmWork
    queryset = None
    http_method_names = ['get']

    def get_queryset(self) -> dict:
        """Return movies"""

        def persons_list(role):
            return ArrayAgg(
                'person_film_work__person__full_name',
                distinct=True,
                filter=Q(person_film_work__role=role)
            )

        queryset = self.model._default_manager.prefetch_related(
            'genre_film_work__genre',
            'person_film_work__person'
        ).annotate(
            genres=ArrayAgg('genre_film_work__genre__name', distinct=True),
            actors=persons_list(RoleType.ACTOR),
            directors=persons_list(RoleType.DIRECTOR),
            writers=persons_list(RoleType.WRITER),
        )

        return queryset.values()

    @staticmethod
    def render_to_response(context):
        """Convert data to json"""
        json_params = {
            'ensure_ascii': False,
            'indent': 2,
            'sort_keys': True
        }
        return JsonResponse(context, json_dumps_params=json_params)


class MoviesApi(MoviesApiMixin, BaseListView):
    """Endpoint to work with movies list"""

    paginate_by = 50

    def get_context_data(self, *, object_list=None, **kwargs) -> dict:
        """Get data for the request."""
        context = {}
        queryset = object_list or self.get_queryset()
        page_size = self.get_paginate_by(queryset)
        pagination = self.paginate_queryset(queryset, page_size)
        context.update(pagination)
        return context

    def paginate_queryset(self, queryset: QuerySet, page_size: int) -> dict:
        """Paginate the queryset, if needed."""
        paginator = self.get_paginator(
            queryset.values(),
            page_size,
            orphans=self.get_paginate_orphans(),
            allow_empty_first_page=self.get_allow_empty()
        )
        pkw = self.page_kwarg
        page = self.kwargs.get(pkw) or self.request.GET.get(pkw) or 1

        try:
            page_number = int(page)
        except ValueError:
            if page == 'last':
                page_number = paginator.num_pages
            else:
                raise Http404(_('Page is not “last”, nor can it be converted to an int.'))

        try:
            page = paginator.page(page_number)
        except InvalidPage as e:
            raise Http404(_(f'Invalid page {page_number}: {e}'))

        result = {
            'count': paginator.count,
            'total_pages': paginator.num_pages,
            'prev': None,
            'next': None,
            'results': list(page.object_list),
        }
        if page.has_previous():
            result['prev'] = page.previous_page_number()
        if page.has_next():
            result['next'] = page.next_page_number()

        return result


class MovieDetailsApi(MoviesApiMixin, BaseDetailView):
    """Endpoint to work with movie details"""

    def get_context_data(self, **kwargs) -> dict:
        """Insert the single object into the context dict."""
        movie = kwargs.get('object')

        if not movie:
            movie_id = self.kwargs.get('pk')
            raise Http404(_(f'Movie not found: {movie_id}'))

        return movie
