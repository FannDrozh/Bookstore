from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.urls import reverse


class Book(models.Model):
    """Основная модель книги"""

    GENRE_CHOICES = [
        ('FICTION', 'Художественная литература'),
        ('SCIFI', 'Научная фантастика'),
        ('FANTASY', 'Фэнтези'),
        ('CLASSIC', 'Классика'),
        ('DETECTIVE', 'Детектив'),
        ('ROMANCE', 'Роман'),
        ('HISTORY', 'Историческая'),
        ('PSYCHOLOGY', 'Психология'),
        ('PHILOSOPHY', 'Философия'),
        ('CHILDREN', 'Детская'),
        ('OTHER', 'Другое'),
    ]

    title = models.CharField(
        verbose_name='Название',
        max_length=255
    )

    author = models.CharField(
        verbose_name='Автор',
        max_length=255
    )

    genre = models.CharField(
        verbose_name='Жанр',
        max_length=50,
        choices=GENRE_CHOICES,
        default='FICTION'
    )

    short_description = models.TextField(
        verbose_name='Краткое описание',
        blank=True
    )

    reading_reason = models.TextField(
        verbose_name='Почему стоит прочитать',
        blank=True
    )

    rating = models.DecimalField(
        verbose_name='Рейтинг',
        max_digits=3,
        decimal_places=1,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
        null=True,
        blank=True
    )

    price_rub = models.DecimalField(
        verbose_name='Цена (₽)',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.0)],
        default=0.00
    )

    # ДОБАВЛЕННЫЕ ПОЛЯ:
    isbn = models.CharField(
        verbose_name='ISBN',
        max_length=13,
        blank=True,
        null=True,
        help_text='Международный стандартный книжный номер'
    )

    publication_year = models.PositiveIntegerField(
        verbose_name='Год издания',
        null=True,
        blank=True,
        validators=[MinValueValidator(1800), MaxValueValidator(2100)],
        help_text='Год первой публикации'
    )

    page_count = models.PositiveIntegerField(
        verbose_name='Количество страниц',
        null=True,
        blank=True,
        help_text='Объем книги в страницах'
    )

    cover_image = models.ImageField(
        verbose_name='Обложка книги',
        upload_to='book/covers/',
        null=True,
        blank=True,
        help_text='Изображение обложки'
    )

    is_available = models.BooleanField(
        verbose_name='В наличии',
        default=True
    )

    created_at = models.DateTimeField(
        verbose_name='Дата добавления',
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        verbose_name='Дата обновления',
        auto_now=True
    )

    class Meta:
        verbose_name = 'Книга'
        verbose_name_plural = 'Книги'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.author}"

    def get_absolute_url(self):
        return reverse('book_detail', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        """Автоматическая обработка перед сохранением"""
        if self.rating is not None:
            # Округление рейтинга
            self.rating = round(float(self.rating), 1)
        super().save(*args, **kwargs)

    @property
    def price_category(self):
        """Категория цены"""
        if self.price_rub < 300:
            return 'Бюджетная'
        elif self.price_rub < 700:
            return 'Средняя'
        elif self.price_rub < 1000:
            return 'Премиум'
        else:
            return 'Элитная'

    @property
    def rating_stars(self):
        """Рейтинг в виде звезд"""
        if self.rating:
            stars = int(self.rating)
            half = self.rating - stars >= 0.5
            return '★' * stars + ('½' if half else '') + '☆' * (5 - stars - (1 if half else 0))
        return '☆☆☆☆☆'


class BookReview(models.Model):
    """Модель отзыва о книге"""
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Книга'
    )

    reviewer_name = models.CharField(
        verbose_name='Имя',
        max_length=100
    )

    email = models.EmailField(
        verbose_name='Email',
        blank=True,
        null=True
    )

    rating = models.PositiveSmallIntegerField(
        verbose_name='Оценка',
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )

    text = models.TextField(
        verbose_name='Текст отзыва'
    )

    is_approved = models.BooleanField(
        verbose_name='Одобрен',
        default=True
    )

    created_at = models.DateTimeField(
        verbose_name='Дата отзыва',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']

    def __str__(self):
        return f"Отзыв на {self.book.title} от {self.reviewer_name}"

    @property
    def rating_stars(self):
        """Оценка в виде звезд"""
        return '★' * self.rating + '☆' * (10 - self.rating)