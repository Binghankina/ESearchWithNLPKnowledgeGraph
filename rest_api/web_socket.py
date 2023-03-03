# -*- coding:utf-8 -*-

from channels.auth import http_session_user
from rest_api.models import UserProfile
from rest_framework_jwt.serializers import VerifyJSONWebTokenSerializer
from channels import Group
from django.conf import settings
from touyantong.utilities import logger

ALL_SUBSCRIBE = settings.ALL_SUBSCRIBE


def get_subscribe_list(message):
    try:
        valid_data = VerifyJSONWebTokenSerializer().validate({
            'token': message.content["path"].split('/')[-2]
        })
        user_obj = valid_data['user']
    except:
        logger.error("[WS] error token")
        message.reply_channel.send({"text": '{"error": "error token", "code": 1024}'})
        return

    try:
        subscribe_list = UserProfile.objects.get(user=user_obj).subscribe_list
    except UserProfile.DoesNotExist:
        data = {"user": user_obj, "subscribe_list": [], "favorites_list": []}
        UserProfile.objects.create(**data)
        subscribe_list = UserProfile.objects.get(user=user_obj).subscribe_list

    return subscribe_list


@http_session_user
def ws_connect(message):
    subscribe_list = get_subscribe_list(message)
    message.reply_channel.send({"accept": True})
    if not subscribe_list:
        logger.info("[WS] empty category")
        return
    # 添加对应分组
    for subscribe in subscribe_list:
        Group(subscribe).add(message.reply_channel)
    logger.info("[WS] added %s to group" % ", ".join(subscribe_list))


@http_session_user
def ws_update_subscribe(message):
    subscribe_list = get_subscribe_list(message)

    if message.content['text'] == 'update_subscribe':
        # 在所有组中删除该用户
        for subscribe in ALL_SUBSCRIBE:
            Group(subscribe).discard(message.reply_channel)
        # 添加进新的组
        for subscribe in subscribe_list:
            Group(subscribe).add(message.reply_channel)
        logger.info("[WS] updated %s to group" % ", ".join(subscribe_list))
