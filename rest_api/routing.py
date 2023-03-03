# -*-coding:utf-8 -*-

from channels.routing import route
from rest_api.web_socket import ws_connect, ws_update_subscribe

channel_routing = [
    route("websocket.connect", ws_connect),
    route("websocket.receive", ws_update_subscribe),
]