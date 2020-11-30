from channels.generic.websocket import WebsocketConsumer
import json
from asgiref.sync import async_to_sync
from .serializers import MessageSerializer
from .models import Message, Chat
from rest_framework.renderers import JSONRenderer
from django.contrib.auth import get_user_model


user = get_user_model()


class ChatConsumer(WebsocketConsumer):
    
    def new_message(self, data):
        message = data['message']
        author = data['username']
        roomname = data['roomname']
        self.notif(data)
        chat_model = Chat.objects.get(roomname=roomname)
        user_model = user.objects.filter(username=author).first()
        message_model = Message.objects.create(author=user_model , content=message, related_chat=chat_model)
        result = eval(self.message_serializer(message_model))
        self.send_to_chat_message(result)
    
    def notif(self, data):

        message_roomname = data['roomname']
        chat_room_qs = Chat.objects.filter(roomname=message_roomname)
        print(chat_room_qs[0].members.all())
        members_list = []
        for _ in chat_room_qs[0].members.all():
            members_list.append(_.username)

        async_to_sync(self.channel_layer.group_send)(
        'chat_listener',
        {
            'type': 'chat_message',
            'content': data['message'],
            '__str__' : data['username'],
            'roomname' : message_roomname,
            'members_list' : members_list
        
        }
        )    




    
    def fetch_message(self, data):
        roomname = data['roomname']
        qs = Message.last_message(self, roomname)
        message_json = self.message_serializer(qs)
        content = {
            
            "message" : eval(message_json),
            'command' : "fetch_message"
            
        }
        self.chat_message(content)


    def image(self, data):
       self.send_to_chat_message(data)


    def message_serializer(self, qs):
    
        serialized = MessageSerializer(qs, many=(lambda qs : True if (qs.__class__.__name__ == 'QuerySet') else False)(qs))
        content = JSONRenderer().render(serialized.data)
        return content
        
    
    
    
    
    
    
    
    def connect(self):
        
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )    
        self.accept()

    commands = {
        
        "new_message": new_message,
        "fetch_message": fetch_message,
        'img': image
    
    }
    
    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(

            self.room_group_name,
            self.channel_name
            
        )
    
    def receive(self, text_data):
        text_data_dict = json.loads(text_data)
        command = text_data_dict['command']
        
        self.commands[command](self, text_data_dict)
        
        
        
    def send_to_chat_message(self, message):
        
        command = message.get("command", None)
            
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'content': message['content'],
                'command':(lambda command : "img" if( command == "img") else "new_message")(command),
                '__str__' : message['__str__']
                
                
                
            }
            
            
        )

    
    def chat_message(self, event):
       
        self.send(text_data=json.dumps(event))