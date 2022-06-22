from django.core.validators import MaxValueValidator, MinValueValidator
from rest_framework import serializers
from django.utils import timezone

from reviews.models import Category, Comment, Genre, Review, Title, User

CREATE_DIFFERENT_NAME = 'Создайте другое имя'
SCORE_OUT_OF_RANGE = 'Оценка должна быть между 1 и 10'
ONE_REVIEW_ALLOWED = 'Разрешен только один отзыв на одно произведение'


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('slug', 'name')


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitlesSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = serializers.IntegerField()

    class Meta:
        model = Title
        fields = ('name', 'year', 'category',
                  'genre', 'id', 'description', 'rating')
        read_only_fields = ('name', 'year', 'category', 'genre',
                            'id', 'description', 'rating')

    def get_score(self, obj):
        pass


class TitleCreateSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(), slug_field='slug', many=True
    )
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(), slug_field='slug'
    )
    year = serializers.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(timezone.now().year)
        ]
    )

    class Meta:
        model = Title
        fields = ('name', 'year', 'category', 'genre', 'id', 'description')


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        fields = (
            'username',
            'email',
            'role',
            'first_name',
            'last_name',
            'bio',
        )
        model = User


class TokenSerializer(serializers.Serializer):
    confirmation_code = serializers.CharField(required=True)
    username = serializers.CharField(required=True)


class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True)

    def validate_username(self, name):
        if name == 'me':
            raise serializers.ValidationError(CREATE_DIFFERENT_NAME)
        return name


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        many=False,
        default=serializers.CurrentUserDefault()
    )
    score = serializers.IntegerField(validators=[MinValueValidator(1),
                                                 MaxValueValidator(10)])

    class Meta:
        fields = '__all__'
        read_only_fields = ('title',)
        model = Review

    def validate(self, data):
        if self.context['request'].method != 'POST':
            return data
        author = self.context['request'].user
        title_id = self.context['view'].kwargs.get('title_id')
        if Review.objects.filter(
            title=title_id, author=author
        ).exists():
            raise serializers.ValidationError(ONE_REVIEW_ALLOWED)
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        fields = '__all__'
        read_only_fields = ('review',)
        model = Comment
