from django.urls import path

from .. import views


urlpatterns = [
    path('movies/', views.MoviesApi.as_view()),
    path('movies/<uuid:pk>', views.MovieDetailsApi.as_view()),
]
