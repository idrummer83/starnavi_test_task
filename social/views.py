from django.http import JsonResponse, HttpResponse

from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .serializers import PostSerializer, LikeSerializer, DislikeSerializer, UserSerializer, UserActivitySerializer

from .models import Post, Like, Dislike, StarnaviUser

import json

# Create your views here.

from rest_framework import permissions
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)
from rest_framework.authtoken.models import Token


class IndexView(TemplateView):
    template_name = 'index.html'

    permission_classes = [permissions.IsAuthenticated]


class UserCreateView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]

    queryset = StarnaviUser.objects.all()
    serializer_class = UserSerializer

    @receiver(post_save, sender=settings.AUTH_USER_MODEL)
    def create_auth_token(sender, instance=None, created=False, **kwargs):
        if created:
            Token.objects.create(user=instance)


class PostCreateView(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    queryset = Post.objects.all()
    serializer_class = PostSerializer


class PostListView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    queryset = Post.objects.all()
    serializer_class = PostSerializer


class PostLikeView(generics.CreateAPIView):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer


class PostDislikeView(generics.CreateAPIView):
    queryset = Dislike.objects.all()
    serializer_class = DislikeSerializer


class PostAnaliticsLikesView(generics.ListAPIView):
    serializer_class = LikeSerializer

    def get(self, request, *args, **kwargs):
        likes_analitic = Like.objects.filter(like_published__range=[kwargs['date_from'], kwargs['date_to']])
        if len(likes_analitic) > 0:
            mimetype = 'application/json'
            return HttpResponse(json.dumps({'likes by period': len(likes_analitic)}), mimetype)
        else:
            return self.list(request, *args, [{}])


class ActivityUserView(generics.RetrieveAPIView):
    queryset = StarnaviUser.objects.all()
    serializer_class = UserActivitySerializer


@csrf_exempt
@api_view(["POST"])
@permission_classes((permissions.AllowAny,))
def login(request):
    username = request.data.get("username")
    password = request.data.get("password")

    if username is None or password is None:
        return Response({'error': 'Please provide both username and password'},
                        status=HTTP_400_BAD_REQUEST)

    # user = authenticate(username=username, password=password)
    user = StarnaviUser.objects.get(username=username, password=password)
    if request.user.is_authenticated:
        print("user is authenticated")
    else:
        print("User is not authenticated")
    if not user:
        return Response({'error': 'Invalid Credentials'},
                        status=HTTP_404_NOT_FOUND)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({'token': token.key},
                    status=HTTP_200_OK)


import requests
import random


def start_bot(request):

    with open('./social/bot_rules.json', 'r') as read_file:
        bot = json.load(read_file)

    def bot_user_create():
        url_user = 'http://127.0.0.1:8000/create_user/'
        user_data = {
            "username": 'bot-{}'.format(''.join(['{}'.format(random.randrange(0, 101, 1)) for _ in range(5)])),
            "password": ''.join(['{}'.format(random.randrange(0, 101, 1)) for _ in range(8)]),
            "first_name": 'bot_username'
        }
        usr = requests.post(url_user, data=user_data)
        print('r', usr)

    def bot_post_create(last_user, headers):
        url = 'http://127.0.0.1:8000/post_create/'
        postdata = {
            "post_text": "post text by robot",
            "post_user": last_user.id
        }
        r = requests.post(url, headers=headers, data=postdata)
        print('r', r)

    def bot_like_create(last_user, headers):
        all_posts = Post.objects.all()
        rndm_post_id = random.choice([i.id for i in all_posts])
        url_like = 'http://127.0.0.1:8000/post/{}/{}/like/'.format(rndm_post_id, last_user.id)
        like_data = {
            "like_user": last_user.id,
            "like_post": rndm_post_id,
            "like": 1
        }
        l = requests.post(url_like, headers=headers, data=like_data)
        print('r', l)

    for _ in range(bot['number_of_users']):
        bot_user_create()
        last_user = StarnaviUser.objects.all().last()
        headers = {'Authorization': 'Token {}'.format(last_user.auth_token.key)}
        for _ in range(bot['max_posts_per_user']):
            bot_post_create(last_user, headers)
        for _ in range(bot['max_likes_per_user']):
            bot_like_create(last_user, headers)

    return JsonResponse(bot, safe=True)


