from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import exceptions, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Subscription
from .serializers import SubscribeSerializer, UserCustomSerializer
from api.pagination import CustomPagination
from djoser.views import UserViewSet

User = get_user_model()


class UserViewSet(UserViewSet):
    """Подписка на автора, с проверкой валидации и удаления подписки."""
    serializer_class = UserCustomSerializer
    queryset = User.objects.all()
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticated]

    @action(
        detail=False,
        methods=['GET'],
        serializer_class=SubscribeSerializer,
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        user = self.request.user
        user_subscriptions = user.follower.all()
        authors = [item.author.id for item in user_subscriptions]
        queryset = User.objects.filter(id__in=authors)
        paginated_queryset = self.paginate_queryset(queryset)
        serializer = self.get_serializer(paginated_queryset, many=True)
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        serializer_class=SubscribeSerializer
    )
    def subscribe(self, request, id):
        user = get_object_or_404(User, username=request.user.username)
        author = get_object_or_404(User, id=id)

        if self.request.method == 'POST':
            if user.id == author.id:
                raise exceptions.ValidationError(
                    'Нельзя подписаться на себя.')
            if Subscription.objects.filter(
                user=user,
                author=author
            ).exists():
                raise exceptions.ValidationError(
                    'Вы уже подписаны.')

            Subscription.objects.create(user=user, author=author)
            serializer = self.get_serializer(author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == 'DELETE':
            if not Subscription.objects.filter(
                user=user,
                author=author
            ).exists():
                raise exceptions.ValidationError(
                    'Вы не подписано, либо отписались.')

            subscription = get_object_or_404(
                Subscription,
                user=user,
                author=author
            )
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
