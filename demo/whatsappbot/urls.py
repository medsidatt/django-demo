from django.urls import path
from .views import whatsapp_webhook, message_status_callback, whatsapp_message_receive, hugging_face_test

urlpatterns = [
    path('webhook/', whatsapp_webhook, name='whatsapp_webhook'),
    path('hugging/', hugging_face_test, name='hugging_face_test'),
    path('message/receive', whatsapp_message_receive, name='whatsapp_message_receive'),
    path('status/', message_status_callback, name='message_status')

]
