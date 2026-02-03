from django import forms
from .models import Book, BookReview


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            'title', 'author', 'genre', 'short_description',
            'reading_reason', 'rating', 'price_rub', 'isbn',
            'publication_year', 'page_count', 'cover_image',
            'is_available'
        ]
        widgets = {
            'short_description': forms.Textarea(attrs={'rows': 3}),
            'reading_reason': forms.Textarea(attrs={'rows': 2}),
        }


class BookReviewForm(forms.ModelForm):
    class Meta:
        model = BookReview
        fields = ['reviewer_name', 'email', 'rating', 'text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4}),
        }


class BookFilterForm(forms.Form):
    search = forms.CharField(required=False)
    genre = forms.ChoiceField(choices=[], required=False)
    sort_by = forms.ChoiceField(
        choices=[
            ('-created_at', 'По дате (новые)'),
            ('title', 'По названию (А-Я)'),
            ('-title', 'По названию (Я-А)'),
            ('-rating', 'По рейтингу'),
            ('-price_rub', 'По цене (дорогие)'),
            ('price_rub', 'По цене (дешевые)'),
        ],
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['genre'].choices = [('', 'Все жанры')] + list(Book.GENRE_CHOICES)


class ContactForm(forms.Form):
    name = forms.CharField(
        label='Имя',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите ваше имя'})
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'})
    )
    subject = forms.CharField(
        label='Тема',
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Тема сообщения'})
    )
    message = forms.CharField(
        label='Сообщение',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Введите ваше сообщение...'})
    )
    agree_to_terms = forms.BooleanField(
        label='Я согласен с обработкой персональных данных',
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )