from django.urls import path
from .views import chat_view,inbox_view

urlpatterns = [
    path("inbox/", inbox_view, name="inbox"),
    path('<str:username>/', chat_view, name='chat_view'),
    
]
