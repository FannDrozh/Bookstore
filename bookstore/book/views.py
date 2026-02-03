from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, FormView
from django.urls import reverse_lazy, reverse
from django.db.models import Q, Avg, Count, Min, Max, Sum, F, ExpressionWrapper, DecimalField
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from datetime import datetime, timedelta
import json
import csv
from io import StringIO

from .models import Book, BookReview
from .forms import BookForm, BookReviewForm, BookFilterForm, ContactForm


class BookListView(ListView):
    """Главная страница - список всех книг"""
    model = Book
    template_name = 'book/book_list.html'
    context_object_name = 'book'
    paginate_by = 15

    def get_queryset(self):
        queryset = Book.objects.all()

        # Параметры фильтрации
        search = self.request.GET.get('search', '')
        genre = self.request.GET.get('genre', '')
        price_range = self.request.GET.get('price_range', '')
        sort_by = self.request.GET.get('sort_by', '-created_at')
        only_available = self.request.GET.get('only_available', 'on') == 'on'

        if only_available:
            queryset = queryset.filter(is_available=True)

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(author__icontains=search) |
                Q(short_description__icontains=search)
            )

        if genre:
            queryset = queryset.filter(genre=genre)

        if price_range:
            if price_range == '0-300':
                queryset = queryset.filter(price_rub__lt=300)
            elif price_range == '300-700':
                queryset = queryset.filter(price_rub__gte=300, price_rub__lt=700)
            elif price_range == '700-1000':
                queryset = queryset.filter(price_rub__gte=700, price_rub__lt=1000)
            elif price_range == '1000-':
                queryset = queryset.filter(price_rub__gte=1000)

        # Сортировка
        if sort_by in ['title', '-title', 'rating', '-rating', 'price_rub', '-price_rub',
                       'publication_year', '-publication_year', 'created_at', '-created_at']:
            queryset = queryset.order_by(sort_by)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = BookFilterForm(self.request.GET or None)

        # Статистика для главной страницы
        queryset = self.get_queryset()
        context['total_books'] = queryset.count()
        context['recent_books'] = Book.objects.order_by('-created_at')[:5]
        context['top_rated'] = Book.objects.filter(rating__isnull=False).order_by('-rating')[:5]

        return context


class BookDetailView(DetailView):
    """Детальная страница книги"""
    model = Book
    template_name = 'book/book_detail.html'
    context_object_name = 'book'



class BookCreateView(LoginRequiredMixin, CreateView):
    """Создание новой книги"""
    model = Book
    form_class = BookForm
    template_name = 'book/book_form.html'
    success_url = reverse_lazy('book_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Книга успешно добавлена!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавить новую книгу'
        context['submit_text'] = 'Добавить книгу'
        return context


class BookUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование книги"""
    model = Book
    form_class = BookForm
    template_name = 'book/book_form.html'

    def form_valid(self, form):
        messages.success(self.request, 'Книга успешно обновлена!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('book:book_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Редактировать: {self.object.title}'
        context['submit_text'] = 'Сохранить изменения'
        return context


class BookDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление книги"""
    model = Book
    template_name = 'book/book_confirm_delete.html'
    success_url = reverse_lazy('book:book_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Книга успешно удалена!')
        return super().delete(request, *args, **kwargs)


class BookReviewCreateView(CreateView):
    """Добавление отзыва к книге"""
    model = BookReview
    form_class = BookReviewForm

    def form_valid(self, form):
        book = get_object_or_404(Book, pk=self.kwargs['book_id'])
        form.instance.book = book
        messages.success(self.request, 'Спасибо за ваш отзыв!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('book_detail', kwargs={'pk': self.kwargs['book_id']})


class SearchResultsView(ListView):
    """Расширенный поиск по книгам"""
    model = Book
    template_name = 'book/search_results.html'
    context_object_name = 'book'
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get('q', '')

        if query:
            # Расширенный поиск по всем полям
            return Book.objects.filter(
                Q(title__icontains=query) |
                Q(author__icontains=query) |
                Q(short_description__icontains=query) |
                Q(reading_reason__icontains=query) |
                Q(isbn__icontains=query)
            ).distinct()

        return Book.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        context['results_count'] = self.get_queryset().count()
        return context


class StatisticsView(TemplateView):
    """Страница расширенной статистики"""
    template_name = 'book/statistics.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Общая статистика
        total_books = Book.objects.count()
        available_books = Book.objects.filter(is_available=True).count()
        books_with_reviews = Book.objects.filter(reviews__isnull=False).distinct().count()

        # Статистика по ценам
        price_stats = Book.objects.aggregate(
            avg_price=Avg('price_rub'),
            min_price=Min('price_rub'),
            max_price=Max('price_rub'),
            total_value=Sum('price_rub')
        )

        # Статистика по жанрам
        genre_stats = []
        for genre_code, genre_name in Book.GENRE_CHOICES:
            count = Book.objects.filter(genre=genre_code).count()
            if count > 0:
                avg_price = Book.objects.filter(genre=genre_code).aggregate(
                    Avg('price_rub')
                )['price_rub__avg'] or 0
                genre_stats.append({
                    'name': genre_name,
                    'count': count,
                    'percentage': (count / total_books * 100) if total_books > 0 else 0,
                    'avg_price': avg_price
                })

        # Книги по годам
        current_year = timezone.now().year
        year_groups = {}
        for year in range(2000, current_year + 1, 5):
            next_year = year + 4 if year + 4 <= current_year else current_year
            count = Book.objects.filter(
                publication_year__gte=year,
                publication_year__lte=next_year
            ).count()
            if count > 0:
                year_groups[f'{year}-{next_year}'] = count

        # Топ авторов
        from django.db.models import Count
        top_authors = Book.objects.values('author').annotate(
            book_count=Count('id'),
            avg_rating=Avg('rating')
        ).order_by('-book_count')[:10]

        context.update({
            'total_books': total_books,
            'available_books': available_books,
            'books_with_reviews': books_with_reviews,
            'price_stats': price_stats,
            'genre_stats': sorted(genre_stats, key=lambda x: x['count'], reverse=True),
            'year_groups': year_groups,
            'top_authors': top_authors,
            'recent_month': Book.objects.filter(
                created_at__gte=timezone.now() - timedelta(days=30)
            ).count(),
        })

        return context


class AboutView(TemplateView):
    """Страница "О проекте" """
    template_name = 'book/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['features'] = [
            '📚 Каталог более 1000 книг различных жанров',
            '🔍 Расширенный поиск и фильтрация',
            '⭐ Система рейтингов и отзывов',
            '📊 Детальная статистика и аналитика',
            '🛒 Удобный интерфейс для управления',
            '📱 Адаптивный дизайн для всех устройств',
        ]
        return context


class ContactView(FormView):
    """Страница контактов с формой обратной связи"""
    template_name = 'book/contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('book:contact')

    def form_valid(self, form):
        messages.success(self.request, 'Сообщение отправлено! Мы свяжемся с вами в ближайшее время.')
        return super().form_valid(form)


class ExportBooksView(LoginRequiredMixin, View):
    """Экспорт книг в CSV"""

    def get(self, request):
        response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
        response['Content-Disposition'] = 'attachment; filename="books_export.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Название', 'Автор', 'Жанр', 'Цена (₽)', 'Рейтинг',
            'Год издания', 'Страниц', 'ISBN', 'В наличии', 'Дата добавления'
        ])

        books = Book.objects.all().order_by('id')
        for book in books:
            writer.writerow([
                book.id,
                book.title,
                book.author,
                book.get_genre_display(),
                book.price_rub,
                book.rating or '',
                book.publication_year or '',
                book.page_count or '',
                book.isbn or '',
                'Да' if book.is_available else 'Нет',
                book.created_at.strftime('%d.%m.%Y %H:%M')
            ])

        return response


class GenreBooksView(ListView):
    """Страница книг определенного жанра"""
    model = Book
    template_name = 'book/genre_books.html'
    context_object_name = 'book'
    paginate_by = 12

    def get_queryset(self):
        self.genre = self.kwargs['genre']
        return Book.objects.filter(genre=self.genre, is_available=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['genre_name'] = dict(Book.GENRE_CHOICES).get(self.genre, 'Неизвестный жанр')
        context['books_count'] = self.get_queryset().count()
        return context


class AuthorBooksView(ListView):
    """Страница книг определенного автора"""
    model = Book
    template_name = 'book/author_books.html'
    context_object_name = 'book'
    paginate_by = 12

    def get_queryset(self):
        self.author = self.kwargs['author']
        return Book.objects.filter(author=self.author, is_available=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['author_name'] = self.author
        context['books_count'] = self.get_queryset().count()

        # Статистика по автору
        if self.get_queryset().exists():
            stats = self.get_queryset().aggregate(
                avg_rating=Avg('rating'),
                avg_price=Avg('price_rub'),
                total_pages=Sum('page_count')
            )
            context['author_stats'] = stats

        return context