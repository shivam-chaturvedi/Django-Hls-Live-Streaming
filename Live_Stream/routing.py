from django.urls import path
from .consumers import LiveStreamConsumer

ws_urlpatterns=[
path('ws/send/blob',LiveStreamConsumer.as_asgi()),
]