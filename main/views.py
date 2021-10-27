from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Prefetch, Count, Q
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic.base import View
from rest_framework import generics, permissions, status, filters, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from main.pagination import PaginationPublished
from main.serializers import *
from main.models import *
from users.models import Users, Chat
from users.permissions import IsOwnerOrReadOnly, CheckMembers, IsOwnerPublished, IsOwnerGroup


class PublishViewSet(viewsets.GenericViewSet,
                     mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin):
    """Удаление/обновление/вывод публикации и вывод публикаций"""
    pagination_class = PaginationPublished
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'owner__username']

    def get_serializer_class(self):
        if self.action == 'list':
            return PublishedSerializer
        if self.action == 'retrieve':
            return DetailPublishSerializer
        if self.action in ('update', 'partial_update'):
            return UpdatePublishedSerializer

    def get_permissions(self):
        if self.action in ('update', 'partial_update', 'destroy'):
            permission_classes = [permissions.IsAuthenticated, IsOwnerPublished]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]

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


class GroupsViewSet(viewsets.GenericViewSet,
                    mixins.ListModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin):
    """Удаление/обновление/вывод группы и вывод групп. Подписаться на группу/отписаться от группы."""

    def get_serializer_class(self):
        if self.action == 'list':
            return MyGroupsSerializer
        if self.action == 'retrieve':
            return GroupDetailSerializer
        if self.action in ('update', 'partial_update', 'create'):
            return GroupCreateSerializer

    def get_permissions(self):
        if self.action in ('update', 'partial_update', 'destroy'):
            permission_classes = [permissions.IsAuthenticated, IsOwnerGroup]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = Users.objects.get(id=self.request.user.pk)
        if self.action == 'list':
            queryset = Groups.objects.filter(users=user)
        else:
            queryset = Groups.objects.all()
        return queryset

    @action(detail=True, url_path='group_activity', url_name='group_activity')
    def group_activity(self, request, *args, **kwargs):
        """Подписаться на группу/отписаться от группы"""
        group = self.get_object()
        user = Users.objects.get(pk=request.user.pk)
        if user in group.users.all():
            group.users.remove(user)
            return Response(data={'status': 'Вы отписались от группы.'}, status=status.HTTP_200_OK)
        if user not in group.users.all():
            group.users.add(user)
            return Response(data={'status': 'Вы подписались от группы.'}, status=status.HTTP_200_OK)
        return Response(data={'status': 'Ошибка.'}, status=status.HTTP_404_NOT_FOUND)


class UserViewSet(viewsets.GenericViewSet,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin):
    """Обновление/вывод пользователя и вывод друзей пользователя. Система друзей"""
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'list':
            return FriendsSerializer
        if self.action == 'retrieve':
            user = self.get_object()
            if user.pk == self.request.user.pk:
                return UsersProfileFSerializer
            else:
                return UsersProfileNFSerializers
        if self.action in ('update', 'partial_update'):
            return HomeUpdateSerializer

    def get_permissions(self):  # Разрешения для friend_activity
        if self.action == 'list':
            permission_classes = [permissions.IsAuthenticated]
        # elif self.action == 'friend_activity':
        #     permission_classes = [permissions.IsAuthenticated, IsReadOnlyOrNotOwner]
        else:
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = Users.objects.filter(id=self.request.user.pk)
        if self.action == 'list':
            queryset = user
        else:
            queryset = Users.objects.all()
        return queryset

    @action(detail=True, url_path='user_activity', url_name='user_activity')
    def friend_activity(self, request, *args, **kwargs):
        """Система друзей"""
        user = self.get_object()
        you = Users.objects.get(pk=request.user.pk)
        try:
            subs = PostSubscribers.objects.get(
                Q(owner_id=user.id, user_id=you.pk) |
                Q(owner_id=you.id, user_id=user.pk)
            )
        except Exception:
            subs = ''
        if you in user.friends.all():
            you.friends.remove(user)
            PostSubscribers.objects.create(owner_id=you.id, user_id=user.id)
            return Response(data={'status': 'Пользователь удален из друзей.'}, status=status.HTTP_200_OK)
        elif not subs:
            PostSubscribers.objects.create(owner_id=user.id, user_id=you.id)
            return Response(data={'status': 'Заявка на дружбу отправлена.'}, status=status.HTTP_200_OK)
        elif subs.owner == you:
            you.friends.add(user)
            PostSubscribers.objects.filter(owner_id=you.id, user_id=user.id).delete()
            return Response(data={'status': 'Пользователь добавлен в друзья.'}, status=status.HTTP_200_OK)
        elif subs.owner == user:
            PostSubscribers.objects.filter(owner_id=user.id, user_id=you.id).delete()
            return Response(data={'status': 'Заявку на дружбу отменена.'}, status=status.HTTP_200_OK)
        return Response(data={'status': 'Ошибка.'}, status=status.HTTP_404_NOT_FOUND)






class MessagesView(generics.ListAPIView):
    """Вывод чатов пользователя"""
    serializer_class = MessagesSerializer
    permission_classes = [permissions.IsAuthenticated]
    # filter_backends = [filters.SearchFilter]
    # search_fields = ['id']

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
        return Response(data='Ошибка создания', status=status.HTTP_404_NOT_FOUND)


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


class AddGroupView(generics.CreateAPIView):
    """Создание группы"""
    serializer_class = GroupCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            Groups.objects.create(**serializer.validated_data, owner_id=request.user.pk)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(data='Ошибка создания', status=status.HTTP_404_NOT_FOUND)


class AddPublishedView(generics.CreateAPIView):
    """Создание публикации"""
    queryset = Groups.objects.all()
    serializer_class = UpdatePublishedSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            Published.objects.create(**serializer.validated_data,
                                     owner_id=request.user.pk,
                                     group_id=self.get_object().id
                                     )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(data='Ошибка создания', status=status.HTTP_404_NOT_FOUND)


class AddCommentView(generics.CreateAPIView):
    """Создание комментария"""
    queryset = Published.objects.all()
    serializer_class = CommentsAddSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            Comments.objects.create(**serializer.validated_data,
                                    users_id=request.user.pk,
                                    published_id=self.get_object().id
                                    )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(data='Ошибка создания', status=status.HTTP_404_NOT_FOUND)


# Logic
class AddStarRating(generics.CreateAPIView):
    """Звездный рейтинг"""
    queryset = Published.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = Users.objects.get(username=request.user.username)
            serializer.save(ip=user.username, published=self.get_object())
            return Response(data='Success', status=status.HTTP_201_CREATED)
        else:
            return Response(data='Error', status=status.HTTP_400_BAD_REQUEST)


@login_required(login_url='/users/login/')
def like_view(request, com_id):
    """Лайки комментариев"""
    comment = Comments.objects.prefetch_related('like').get(id=com_id)
    user = Users.objects.get(username=request.user.username)
    if user in comment.like.all():
        comment.like.remove(user)
    else:
        comment.like.add(user)
    return redirect(comment)
