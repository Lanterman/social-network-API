from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Prefetch, Count, Q
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic.base import View
from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from main.pagination import PaginationPublished
from main.serializers import *
from main.models import *
from users.models import Users, Chat
from users.permissions import IsOwnerOrReadOnly, IsOwnerOrClose, CheckMembers, IsOwnerPublished, IsOwnerGroup


class PublishedListView(generics.ListAPIView):
    """Вывод списка публикаций в зависимости от авторизации"""
    serializer_class = PublishedSerializer
    pagination_class = PaginationPublished
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'owner__username']

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
        return Response(data='Ошибка создания', status=status.HTTP_404_NOT_FOUND)


class DetailGroupView(generics.RetrieveAPIView):
    """Детальная информация группы"""
    queryset = Groups.objects.all()
    serializer_class = GroupDetailSerializer
    permission_classes = [permissions.IsAuthenticated]


class AddPublishedView(generics.CreateAPIView):
    """Создание публикации"""
    queryset = Groups.objects.all()
    serializer_class = AddPublishedSerializer
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


class DetailPublishView(generics.RetrieveAPIView):
    """Детальная информация публикации и комментариев под записью"""
    queryset = Published.objects.all().select_related('owner').annotate(rat=Avg('rating__star__value')).order_by('-date')
    serializer_class = DetailPublishSerializer


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
def del_group(request, group_slug):
    Groups.objects.get(slug=group_slug).delete()
    return redirect(reverse('groups', kwargs={'pk': request.user.pk}))


def del_pub_group(request, pub_slug, group_slug):
    group = Groups.objects.get(slug=group_slug)
    Published.objects.get(slug=pub_slug).delete()
    return redirect(group)


def del_published(request, pub_slug):
    user = Users.objects.get(pk=request.user.pk)
    Published.objects.get(slug=pub_slug).delete()
    return redirect(user)


class UpdateGroup(generics.UpdateAPIView):
    queryset = Groups.objects.all()
    serializer_class = GroupCreateSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerGroup]


class UpdatePublished(generics.UpdateAPIView):
    queryset = Published.objects.all()
    serializer_class = AddPublishedSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerPublished]


def friend_activity(request, user_pk):
    q = Users.objects.get(pk=user_pk)
    user = Users.objects.get(pk=request.user.pk)
    try:
        subs = PostSubscribers.objects.select_related('user').get(
            Q(owner=user.username, user_id=q.pk) |
            Q(owner=q.username, user_id=user.pk)
        )
    except Exception:
        subs = ''
    if q in user.friends.all():
        q.friends.remove(request.user)
        PostSubscribers.objects.create(owner=user.username, user_id=q.id)
    elif not subs:
        PostSubscribers.objects.create(owner=q.username, user_id=user.id)
    elif subs.owner != q.username:
        user.friends.add(q)
        PostSubscribers.objects.filter(owner=user.username, user_id=q.id).delete()
    elif subs.owner == q.username:
        PostSubscribers.objects.filter(owner=q.username, user_id=user.id).delete()
    return redirect(q)


def friend_hide(request, user_pk):
    q = Users.objects.get(pk=user_pk)
    user = Users.objects.get(pk=request.user.pk)
    PostSubscribers.objects.filter(owner=user.username, user_id=q.id).update(escape=True)
    return redirect(user)


def friend_accept(request, user_pk):
    q = Users.objects.get(pk=user_pk)
    user = Users.objects.get(pk=request.user.pk)
    user.friends.add(q)
    PostSubscribers.objects.filter(owner=user.username, user_id=q.id).delete()
    return redirect(user)


def friend_del_primary(request, user_pk):
    q = Users.objects.get(pk=user_pk)
    user = Users.objects.get(pk=request.user.pk)
    user.friends.remove(q)
    PostSubscribers.objects.create(owner=user.username, user_id=q.id)
    return redirect(reverse('friends', kwargs={'pk': user.pk}))


def group_activity(request, group_slug):
    q = Groups.objects.prefetch_related('users').get(slug=group_slug)
    user = Users.objects.get(pk=request.user.pk)
    if user in q.users.all():
        q.users.remove(request.user)
    else:
        q.users.add(user)
    return redirect(q)


def group_quit_primary(request, group_slug):
    q = Groups.objects.get(slug=group_slug)
    q.users.remove(request.user)
    return redirect(reverse('groups', kwargs={'pk': request.user.pk}))


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
