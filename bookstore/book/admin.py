from django.contrib import admin
from django.utils.html import format_html
from .models import Book, BookReview


class BookReviewInline(admin.TabularInline):
    """Inline для отображения отзывов"""
    model = BookReview
    extra = 0
    readonly_fields = ['created_at']
    fields = ['reviewer_name', 'email', 'rating', 'text', 'is_approved', 'created_at']
    classes = ['collapse']


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """Админ-панель для книг"""

    # Отображение в списке
    list_display = [
        'title', 'author', 'genre_display',
        'price_display', 'rating_display',
        'is_available_display', 'created_at_short'
    ]

    # Фильтры
    list_filter = [
        'genre',
        'is_available',
        'created_at',
        'publication_year'
    ]

    # Поиск
    search_fields = [
        'title', 'author', 'isbn', 'short_description'
    ]

    # Редактирование (убрали поля, которых нет в модели)
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'author', 'genre')
        }),
        ('Детали', {
            'fields': ('isbn', 'publication_year', 'page_count')
        }),
        ('Описание и рейтинг', {
            'fields': ('short_description', 'reading_reason', 'rating')
        }),
        ('Цена и наличие', {
            'fields': ('price_rub', 'is_available')
        }),
        ('Обложка', {
            'fields': ('cover_image',),
            'classes': ('collapse',)
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at']

    # Inline
    inlines = [BookReviewInline]

    # Действия
    actions = ['make_available', 'make_unavailable']

    # Кастомные методы отображения
    def genre_display(self, obj):
        return obj.get_genre_display()

    genre_display.short_description = 'Жанр'

    def price_display(self, obj):
        return f"{obj.price_rub} ₽"

    price_display.short_description = 'Цена'

    def rating_display(self, obj):
        if obj.rating:
            return f"{obj.rating}/10"
        return '-'

    rating_display.short_description = 'Рейтинг'

    def is_available_display(self, obj):
        if obj.is_available:
            return format_html('<span style="color: green;">✓</span>')
        return format_html('<span style="color: red;">✗</span>')

    is_available_display.short_description = 'В наличии'

    def created_at_short(self, obj):
        return obj.created_at.strftime('%d.%m.%Y')

    created_at_short.short_description = 'Добавлена'

    # Кастомные действия
    def make_available(self, request, queryset):
        updated = queryset.update(is_available=True)
        self.message_user(request, f'{updated} книг помечены как доступные')

    make_available.short_description = 'Сделать доступными'

    def make_unavailable(self, request, queryset):
        updated = queryset.update(is_available=False)
        self.message_user(request, f'{updated} книг помечены как недоступные')

    make_unavailable.short_description = 'Сделать недоступными'


@admin.register(BookReview)
class BookReviewAdmin(admin.ModelAdmin):
    list_display = ['book', 'reviewer_name', 'rating_display', 'is_approved', 'created_at_short']
    list_filter = ['rating', 'is_approved', 'created_at']
    search_fields = ['book__title', 'reviewer_name', 'text']
    list_editable = ['is_approved']
    readonly_fields = ['created_at']

    def rating_display(self, obj):
        return f"{obj.rating}/10"

    rating_display.short_description = 'Оценка'

    def created_at_short(self, obj):
        return obj.created_at.strftime('%d.%m.%Y %H:%M')

    created_at_short.short_description = 'Дата'