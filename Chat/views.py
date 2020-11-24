from django.shortcuts import render
from django.utils.safestring import mark_safe
import json
from django.contrib.auth.decorators import login_required
from .models import Chat


@login_required(login_url="login")
def index(request):
    user = request.user
    
    chat_rooms = Chat.objects.filter(members = user)
    print(chat_rooms)
    context={
        
        
        
        'chat_rooms' : chat_rooms
    }
    
    
    
    return render(request, 'chat/index.html', context)

@login_required(login_url="login")
def room(request, room_name):
    
    user = request.user
    
    chat_model = Chat.objects.filter(roomname=room_name)
    
    
    
    if not chat_model.exists():
        chat = Chat.objects.create(roomname=room_name)
        chat.members.add(user)
    else:
        chat_model[0].members.add(user)
    
    
    
    username = request.user.username
    
    context = {

        'room_name': room_name,
        'username': mark_safe(json.dumps(username))
    }

    return render(request, "chat/room.html",context)
