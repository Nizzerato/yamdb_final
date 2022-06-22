from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    email = models.EmailField(max_length=254, blank=False, unique=True)
    username = models.CharField(max_length=150, blank=False, unique=True)
    first_name = models.CharField(blank=True, max_length=150)
    last_name = models.CharField(blank=True, max_length=150)

    class Roles:
        USER = 'user'
        ADMIN = 'admin'
        MODERATOR = 'moderator'
        CHOICES = (
            (USER, 'user'),
            (ADMIN, 'admin'),
            (MODERATOR, 'moderator'),
        )

    role = models.CharField(
        max_length=max(len(role) for role, _ in Roles.CHOICES),
        choices=Roles.CHOICES,
        default=Roles.USER,
    )
    bio = models.TextField(default='')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username',)

    @property
    def is_admin(self):
        return (self.role == self.Roles.ADMIN or self.is_staff)

    @property
    def is_moderator(self):
        return (self.is_admin or self.role == self.Roles.MODERATOR)

    def get_payload(self):
        return {
            'user_id': self.id,
            'username': self.username,
            'email': self.email,
        }

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return (self.username, self.email)


class Category(models.Model):
    slug = models.SlugField(unique=True, max_length=50)
    name = models.CharField(max_length=256)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Genre(models.Model):
    slug = models.SlugField(unique=True, max_length=50)
    name = models.CharField(max_length=256)

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.TextField(blank=False)
    genre = models.ManyToManyField(Genre, through='GenreTitle',
                                   related_name='titles')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL,
                                 null=True, blank=True,
                                 related_name='titles')
    year = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(timezone.now().year)
        ]
    )
    description = models.TextField(
        blank=True, null=True
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.genre} {self.title}'


class Review(models.Model):
    title = models.ForeignKey(Title, on_delete=models.CASCADE,
                              related_name='reviews')
    text = models.TextField('Текст Отзыва', blank=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='reviews')
    pub_date = models.DateTimeField('Дата Публикации Отзыва',
                                    auto_now_add=True)
    score = models.IntegerField('Рейтинг',
                                validators=[MinValueValidator(1),
                                            MaxValueValidator(10)])

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_object'
            ),
        ]

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='comments')
    review = models.ForeignKey(Review, on_delete=models.CASCADE,
                               related_name='comments')
    text = models.TextField('Текст Комментария', blank=False)
    pub_date = models.DateTimeField('Дата Публикации Комментария',
                                    auto_now_add=True)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('-pub_date',)
