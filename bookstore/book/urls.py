from django.urls import path
from . import views

app_name = 'book'

urlpatterns = [
    # Основные страницы
    path('', views.BookListView.as_view(), name='book_list'),  # ← name='book_list'
    path('about/', views.AboutView.as_view(), name='about'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('statistics/', views.StatisticsView.as_view(), name='statistics'),

    # Детальные страницы книг
    path('book/<int:pk>/', views.BookDetailView.as_view(), name='book_detail'),

    # CRUD операции с книгами
    path('book/create/', views.BookCreateView.as_view(), name='book_create'),
    path('book/<int:pk>/edit/', views.BookUpdateView.as_view(), name='book_update'),
    path('book/<int:pk>/delete/', views.BookDeleteView.as_view(), name='book_delete'),

    # Отзывы
    path('book/<int:book_id>/review/', views.BookReviewCreateView.as_view(), name='review_create'),

    # Поиск и фильтрация
    path('search/', views.SearchResultsView.as_view(), name='search'),
    path('genre/<str:genre>/', views.GenreBooksView.as_view(), name='genre_books'),
    path('author/<str:author>/', views.AuthorBooksView.as_view(), name='author_books'),

    # Экспорт
    path('export/book/', views.ExportBooksView.as_view(), name='export_books'),
]