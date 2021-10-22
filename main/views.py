from django.db.models import Avg, Prefetch, Count
from django.shortcuts import redirect
from django.views.generic.base import View
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from main.models import Published, Groups
from main.pagination import PaginationPublished
from main.serializers import *
from users.models import Users, Chat
from users.permissions import IsOwnerOrReadOnly, IsOwnerOrClose, CheckMembers


class PublishedListView(generics.ListAPIView):
    """Вывод списка публикаций в зависимости от авторизации"""
    serializer_class = PublishedSerializer
    pagination_class = PaginationPublished

    def get_queryset(self):
        if self.request.user.is_authenticated:
            groups = Groups.objects.filter(users__username=self.request.user.username)
            if groups:
                published = Published.objects.filter(group_id__in=[group.id for group in groups]).select_related(
                    'owner').annotate(rat=Avg('rating__star__value')).order_by('-date')
            else:
                published = ''
        else:
            published = Published.objects.all().select_related('owner').annotate(rat=Avg(
                'rating__star_id')).order_by('-date')
        return published


class HomeView(generics.RetrieveAPIView, generics.UpdateAPIView):
    """Вывод информации пользователя"""
    queryset = Users.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    serializer_class = HomeUpdateSerializer

    def get(self, request, *args, **kwargs):
        user = self.get_object()
        if user.pk == request.user.pk:
            serializer = UsersProfileFSerializer(user, context={'request': request})
        else:
            serializer = UsersProfileNFSerializers(user, context={'request': request})
        return Response(serializer.data)


class MessagesView(generics.ListAPIView):
    """Вывод чатов пользователя"""
    serializer_class = MessagesSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        chats = Chat.objects.filter(members=self.request.user.id).prefetch_related(
            'members',
            Prefetch(
                'message_all',
                queryset=Message.objects.filter(chat__members=self.request.user.id),
                to_attr='set_mes'
            )
        )
        chats = [chat.set_mes[0] for chat in chats]
        return chats


class ChatDetailView(generics.RetrieveAPIView, generics.CreateAPIView):
    """Вывод сообщений определенного чата пользователя и создание сообщения"""
    queryset = Chat.objects.all()
    permission_classes = [permissions.IsAuthenticated, CheckMembers]
    serializer_class = MessageCreateSerializer

    def get(self, request, *args, **kwargs):
        user = Users.objects.get(pk=self.request.user.pk)
        chat = self.get_object()
        messages = Message.objects.filter(chat=chat).select_related('author')
        messages.filter(is_readed=False).exclude(author=user).update(is_readed=True)
        serializer = ChatMessagesSerializer(chat.message_all, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.POST)
        chat = self.get_object()
        if serializer.is_valid():
            Message.objects.create(**serializer.validated_data, chat_id=chat.id, author_id=request.user.pk)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CreateDialogView(View):
    """Создание чата/беседы(в будущем)"""
    def get(self, request, user_id):
        chats = Chat.objects.filter(members__in=[request.user.id, user_id]).annotate(c=Count('members')).filter(c=2)
        if chats.count():
            chat = chats.first()
        else:
            chat = Chat.objects.create()
            chat.members.add(request.user.pk)
            chat.members.add(user_id)
        return redirect(chat)


class FriendsView(generics.RetrieveAPIView):
    """Список друзей"""
    queryset = Users.objects.all()
    serializer_class = FriendsSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrClose]


class GroupsView(generics.RetrieveAPIView):
    """Список групп"""
    queryset = Users.objects.all()
    serializer_class = GroupsSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrClose]


class AddGroupView(generics.CreateAPIView):
    """Создание группы"""
    serializer_class = GroupCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            Groups.objects.create(**serializer.validated_data, owner_id=request.user.pk)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DetailGroupView(generics.RetrieveAPIView):
    queryset = Groups.objects.all()
    serializer_class = GroupDetailSerializer
    permission_classes = [permissions.IsAuthenticated]







class PublishedDetailView(generics.RetrieveAPIView):
    queryset = Published.objects.all()
    serializer_class = PublishedSerializer








class AddPublished(generics.CreateAPIView):
    serializer_class = PublishedAddSerializer
