from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models.aggregates import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from api_yamdb.settings import EMAIL_YAMDB
from reviews.models import Category, Genre, Review, Title, User
from .filters import TitleFilter
from .permissions import IsAdmin, IsAdminOrAuthorOrReadOnly, IsAdminOrReadOnly
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer, SignUpSerializer,
                          TitleCreateSerializer, TitlesSerializer,
                          TokenSerializer, UserSerializer)

SEND_CODE_MESSAGE = 'Код подтверждения'


class CreateListDestroyViewSet(mixins.CreateModelMixin,
                               mixins.ListModelMixin,
                               mixins.DestroyModelMixin,
                               viewsets.GenericViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    pass


class GenreViewSet(CreateListDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class CategoryViewSet(CreateListDestroyViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


def send_confirmation_code(user):
    confirmation_code = default_token_generator.make_token(user)
    user_mail = [user.email]
    site_email = EMAIL_YAMDB
    message = SEND_CODE_MESSAGE
    return send_mail(message, confirmation_code,
                     site_email, user_mail, fail_silently=False)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().annotate(rating=Avg('reviews__score'))
    serializer_class = TitlesSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method not in permissions.SAFE_METHODS:
            return TitleCreateSerializer
        return TitlesSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated, IsAdmin)
    serializer_class = UserSerializer
    lookup_field = 'username'
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', ]

    @action(
        detail=False,
        methods=('get', 'patch'),
        permission_classes=(IsAuthenticated,),
        url_path='me', url_name='me'
    )
    def me(self, request, *args, **kwargs):
        instance = self.request.user
        serializer = self.get_serializer(instance)
        if self.request.method in permissions.SAFE_METHODS:
            return Response(serializer.data)
        serializer = self.get_serializer(
            instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(role=instance.role, partial=True)
        return Response(serializer.data)


class SignUpVeiw(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.filter(
            email=serializer.validated_data['email'],
            username=serializer.validated_data['username'],
        ).first()
        if not user:
            if User.objects.filter(
                email=serializer.validated_data['email'],
            ).exists() or User.objects.filter(
                username=serializer.validated_data['username']
            ).exists():
                return Response(serializer.errors,
                                status=status.HTTP_400_BAD_REQUEST)
            user = User.objects.create(
                email=serializer.validated_data['email'],
                username=serializer.validated_data['username'],
                is_active=False
            )
        if not user.is_active:
            send_confirmation_code(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)


class TokenView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        confirmation_code = serializer.validated_data['confirmation_code']
        user = get_object_or_404(User, username=username)
        if not default_token_generator.check_token(user, confirmation_code):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        token = RefreshToken.for_user(user)
        user.is_active = True
        user.save()
        return Response({'token': str(token.access_token)},
                        status=status.HTTP_200_OK)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,
                          IsAdminOrAuthorOrReadOnly)

    def get_title(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        return title

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            title=self.get_title()
        )


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,
                          IsAdminOrAuthorOrReadOnly)

    def get_review(self):
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'))
        return review

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())
