from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect

from djoser.views import UserViewSet as DjoserUserViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.reverse import reverse

from recipes.models import (Favorite,
                            Ingredient,
                            Recipe,
                            RecipeIngredient,
                            ShoppingList,
                            Tag)
from users.models import Subscription

from api.serializers import (SignUpSerializer,
                             UserSerializer,
                             AvatarSerializer,
                             ReadSubscriptionSerializer,
                             SubscriptionSerializer,
                             TagSerializer,
                             IngredientSerializer,
                             RecipeWriteSerializer,
                             FavoriteSerializer,
                             ShoppingListSerializer)

from api.filters import IngredientFilter, RecipeFilter
from api.pagination import CustomPagination
from api.permissions import IsAuthorOrReadOnly

User = get_user_model()


class UserViewSet(DjoserUserViewSet):

    queryset = User.objects.all()
    serializer_class = SignUpSerializer
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if (
            self.action == 'list'
            or self.action == 'retrieve'
            or self.action == 'me'
        ):
            return UserSerializer
        return super().get_serializer_class()

    @action(
        methods=['GET'],
        url_path='me',
        permission_classes=(IsAuthenticated,),
        detail=False,
    )
    def me(self, request):
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['PUT', 'DELETE'],
        url_path='me/avatar',
        permission_classes=(IsAuthenticated,),
        detail=False,
    )
    def avatar(self, request):
        user = get_object_or_404(User, username=request.user.username)
        if request.method == 'PUT':
            serializer = AvatarSerializer(user, data=request.data,)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        request.user.avatar.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['GET'],
        url_path='subscriptions',
        permission_classes=(IsAuthenticated,),
        detail=False,
    )
    def get_subscribtions(self, request):
        user = get_object_or_404(User, username=request.user.username)
        limit = request.query_params.get('limit')
        following_users = User.objects.filter(following__subscriber=user)
        if limit:
            following_users = following_users[:int(limit)]
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(following_users, request)
        serializer = ReadSubscriptionSerializer(
            result_page,
            many=True,
            context={'request': request})
        return paginator.get_paginated_response(serializer.data)

    @action(
        methods=['POST', 'DELETE'],
        url_path='subscribe',
        permission_classes=(IsAuthenticated,),
        detail=True,
    )
    def subscribe(self, request, id):
        user = get_object_or_404(User, username=request.user.username)
        following = get_object_or_404(User, pk=id)
        if request.method == 'POST':
            serializer = SubscriptionSerializer(
                data={'subscriber': user.id, 'author': following.id},
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        follow = Subscription.objects.filter(
            user=user.id,
            following=following.id
        )
        if follow:
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class TagViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class RecipesViewSet(viewsets.ModelViewSet):

    queryset = Recipe.objects.all()
    serializer_class = RecipeWriteSerializer
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        methods=['POST', 'DELETE'],
        url_path='favorite',
        detail=True,
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk):
        return self.add_to_favorite_or_shopping_list(
            serializer=FavoriteSerializer,
            model=Favorite,
            id=pk,
            request=request)

    @action(
        methods=['POST', 'DELETE'],
        url_path='shopping_cart',
        detail=True,
        permission_classes=[IsAuthenticated],
    )
    def shopping_list(self, request, pk):
        return self.add_to_favorite_or_shopping_list(
            serializer=ShoppingListSerializer,
            model=ShoppingList,
            id=pk,
            request=request)

    @action(
        methods=['GET'],
        url_path='download_shopping_cart',
        detail=False,
        permission_classes=[IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        shopping_cart_ingredients = (
            RecipeIngredient.objects.filter(
                recipe__cart_recipes__user=request.user
            ).values(
                'ingredient__name',
                'ingredient__measurement_unit'
            ).annotate(total_amount=Sum('amount')).order_by('ingredient__name')
        )
        shopping_list = self.prepsre_recipes_to_dl(shopping_cart_ingredients)
        return self.dl_shopping_list(shopping_list)

    def prepsre_recipes_to_dl(self, ingredients):
        shopping_list = []
        for item in ingredients:
            name = item['ingredient__name']
            unit = item['ingredient__measurement_unit']
            total_amount = item['total_amount']
            shopping_list.append(f"{name} ({unit}) — {total_amount}")
        shopping_list_text = "\n".join(shopping_list)
        return shopping_list_text

    def dl_shopping_list(self, shopping_list_text):
        response = HttpResponse(shopping_list_text, content_type='text/plain')
        response[
            'Content-Disposition'
        ] = 'attachment; filename="shopping_list.txt"'

        return response

    def add_to_favorite_or_shopping_list(
            self, serializer, model, id, request,
    ):
        recipe = get_object_or_404(Recipe, id=id)
        if request.method == 'POST':
            serializer = serializer(data={
                'recipe': recipe.id,
                'user': request.user.id,
                'context': {'request': request}})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        recipe = model.objects.filter(user=request.user, recipe=recipe)
        if not recipe:
            return Response(
                {'error': 'Рецепт не найден'},
                status=status.HTTP_400_BAD_REQUEST)
        recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_short_link(self, request, pk):
        """Возвращает короткую ссылку на рецепт."""
        recipe = get_object_or_404(Recipe, pk=pk)
        rev_link = reverse('short_url', args=[recipe.pk])
        return Response(
            {'short-link': request.build_absolute_uri(rev_link)},
            status=status.HTTP_200_OK)


def short_url(request, short_link):

    link = request.build_absolute_uri()
    recipe = get_object_or_404(Recipe, short_link=link)
    return redirect('api:recipe-detail', pk=recipe.id)
