from django.db.models import Avg, Prefetch, Count, Q
from django.shortcuts import redirect
from rest_framework import generics, status, filters, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from main.pagination import PaginationPublished
from main.serializers import *
from main.models import *
from users.models import Chat
from users.permissions import *


class PublishViewSet(viewsets.ReadOnlyModelViewSet, mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    """
    Удаление/обновление/вывод публикации и вывод публикаций,
    установка рейтинга к публикациям,
    добавление комментарие к публикациям
    """
    pagination_class = PaginationPublished
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'owner__username', 'slug']

    def get_serializer_class(self):
        if self.action == 'list':
            return PublishedSerializer
        if self.action == 'retrieve':
            return DetailPublishSerializer
        if self.action in ('update', 'partial_update'):
            return UpdatePublishedSerializer
        if self.action == 'add_rating':
            return RatingSerializer
        if self.action == 'add_comment':
            return CommentsAddSerializer

    def get_permissions(self):
        if self.action in ('update', 'partial_update', 'destroy'):
            permission_classes = [permissions.IsAuthenticated, IsOwnerPublished]
        elif self.action in ('add_rating', 'add_comment'):
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = []
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

    @action(methods=['post'], detail=True)
    def add_rating(self, request, *args, **kwargs):
        """Установка рейтинга к публикациям"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = Users.objects.get(username=request.user.username)
            serializer.save(ip=user.username, published=self.get_object())
            return Response(data='Success', status=status.HTTP_201_CREATED)
        else:
            return Response(data='Error', status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=True)
    def add_comment(self, request, *args, **kwargs):
        """Добавление комментарие к публикациям"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            Comments.objects.create(**serializer.validated_data,
                                    users_id=request.user.pk,
                                    published_id=self.get_object().id
                                    )
            return Response(data='Комментарий добавлен.', status=status.HTTP_201_CREATED)
        return Response(data='Ошибка создания', status=status.HTTP_404_NOT_FOUND)


class GroupsViewSet(viewsets.ModelViewSet):
    """Удаление/обновление/вывод группы и вывод групп. Подписаться на группу/отписаться от группы."""
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'slug']

    def get_serializer_class(self):
        if self.action == 'list':
            return MyGroupsSerializer
        if self.action == 'retrieve':
            return GroupDetailSerializer
        if self.action in ('update', 'partial_update', 'create'):
            return GroupCreateSerializer
        if self.action == 'add_published':
            return UpdatePublishedSerializer

    def get_permissions(self):
        if self.action in ('update', 'partial_update', 'destroy'):
            permission_classes = [permissions.IsAuthenticated, IsOwnerGroup]
        elif self.action == 'add_published':
            permission_classes = [CheckForSubsGroup, permissions.IsAuthenticated]
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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            Groups.objects.create(**serializer.validated_data, owner_id=request.user.pk)
            return Response(data='Группа создана', status=status.HTTP_201_CREATED)
        return Response(data='Ошибка создания', status=status.HTTP_404_NOT_FOUND)

    @action(detail=True)
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

    @action(methods=['post'], detail=True)
    def add_published(self, request, *args, **kwargs):
        """Создание публикации"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            Published.objects.create(**serializer.validated_data,
                                     owner_id=request.user.pk,
                                     group_id=self.get_object().id
                                     )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(data='Ошибка создания', status=status.HTTP_404_NOT_FOUND)


class UserViewSet(viewsets.ReadOnlyModelViewSet, mixins.UpdateModelMixin):
    """Обновление/вывод пользователя и вывод друзей пользователя, система друзей, проверка/создание чатов"""
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['username']

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

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ('friend_activity', 'create_dialog'):
            permission_classes = [permissions.IsAuthenticated, TrueIfNotOwner]
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

    @action(detail=True)
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

    @action(detail=True)
    def create_dialog(self, request, *args, **kwargs):
        """Создание чата/беседы(в будущем)"""
        user = self.get_object()
        chats = Chat.objects.filter(members__in=[self.request.user.id, user]).annotate(c=Count('members')).filter(c=2)
        if chats.count():
            chat = chats.first()
        else:
            chat = Chat.objects.create()
            chat.members.add(self.request.user.pk)
            chat.members.add(user)
        return redirect(chat)


class ChatViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
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
    """Вывод сообщений определенного чата пользователей и создание сообщений"""
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


class CommentViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin):
    """Вывод комментария, система лайков для комментариев"""
    serializer_class = CommentRetrieveSerializer
    queryset = Comments.objects.all()

    @action(detail=True)
    def add_like_comment(self, request, *args, **kwargs):
        """Лайки комментариев"""
        comment = self.get_object()
        user = Users.objects.get(username=request.user.username)
        if user in comment.like.all():
            comment.like.remove(user)
            return Response(data='Лайк убран', status=status.HTTP_200_OK)
        elif user not in comment.like.all():
            comment.like.add(user)
            return Response(data='Лайк добавлен', status=status.HTTP_200_OK)
        return Response(data='Error', status=status.HTTP_404_NOT_FOUND)
