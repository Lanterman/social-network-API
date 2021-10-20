from django.db.models import Avg, Prefetch
from rest_framework import generics, permissions
from rest_framework.response import Response

from main.models import Published, Groups
from main.pagination import PaginationPublished
from main.serializers import *
from users.models import Users, Chat


class PublishedListView(generics.ListAPIView):
    """Вывод списка публикаций в зависимости от авторизации"""
    serializer_class = PublishedSerializer
    pagination_class = PaginationPublished

    def get_queryset(self):
        if self.request.user.is_authenticated:
            groups = Groups.objects.filter(users__username=self.request.user.username)
            if groups:
                published = Published.objects.filter(group_id__in=[group.id for group in groups]).select_related(
                    'owner').annotate(rat=Avg('rating__star_id')).order_by('-date')
            else:
                published = ''
        else:
            published = Published.objects.all().select_related('owner').annotate(rat=Avg(
                'rating__star_id')).order_by('-date')
        return published


class HomeView(generics.RetrieveAPIView):
    """Вывод информации пользователя"""
    queryset = Users.objects.all()
    serializer_class = UsersProfileSerializer
    permission_classes = [permissions.IsAuthenticated]


class HomeUpdateView(generics.UpdateAPIView):
    """Изменение аватарки пользователя"""
    queryset = Users.objects.all()
    serializer_class = HomeUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]


class MessagesView(generics.ListAPIView):
    """Вывод чатов пользователя"""
    serializer_class = MessagesSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        chats = Chat.objects.filter(members=self.request.user.id).prefetch_related(
            'members',
            Prefetch(
                'message_set',
                queryset=Message.objects.filter(chat__members=self.request.user.id),
                to_attr='set_mes'
            )
        )
        chats = [chat.set_mes[0] for chat in chats]
        return chats


class ChatDetailView(generics.RetrieveAPIView):  # Доделать
    """Вывод сообщений определенного чата пользователя"""
    queryset = Chat
    serializer_class = ChatSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = Users.objects.get(pk=self.request.user.pk)
        chat = self.get_object()
        messages = Message.objects.filter(chat=chat).select_related('author')
        if user in chat.members.all():
            messages.filter(is_readed=False).exclude(author=user).update(is_readed=True)
        else:
            chat = None
        serializer = self.get_serializer(chat)
        return Response(serializer.data)





class PublishedDetailView(generics.RetrieveAPIView):
    queryset = Published.objects.all()
    serializer_class = PublishedSerializer


class GroupsView(generics.ListAPIView):
    queryset = Groups.objects.all()
    serializer_class = GroupsSerializer


class GroupDetailView(generics.RetrieveAPIView):
    queryset = Groups.objects.all()
    serializer_class = GroupsSerializer


class AddGroupView(generics.CreateAPIView):
    serializer_class = GroupsSerializer


class AddPublished(generics.CreateAPIView):
    serializer_class = PublishedAddSerializer
