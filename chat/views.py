from django.shortcuts import render
from django.contrib.auth.models import User

from .models import Message
from django.contrib.auth.models import User
from django.db.models import Q

def chat_view(request, username):
    other_user = User.objects.get(username=username)
    current_user = request.user

    messages = Message.objects.filter(
        Q(sender=current_user, receiver=other_user) |
        Q(sender=other_user, receiver=current_user)
    ).order_by('timestamp')

    return render(request, 'chatroom.html', {
        'other_user': other_user,
        'messages': messages
    })


def inbox_view(request):
    current_user = request.user

    # All users who have ever sent/received messages to/from this user
    chat_users = User.objects.filter(
        Q(sent_messages__receiver=current_user) |
        Q(received_messages__sender=current_user)
    ).distinct().exclude(id=current_user.id)

    return render(request, 'inbox.html', {
        'chat_users': chat_users
    })