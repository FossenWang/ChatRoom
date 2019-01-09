from django.http import JsonResponse
from .consumers import ChatRoom


def home(request):
    return JsonResponse('home', safe=False)


def chatroom_list(request):
    chatrooms = []
    for room_name in ChatRoom.rooms:
        chatrooms.append({
            'room': room_name,
            'count': len(ChatRoom.rooms[room_name]['channels'])
        })
    return JsonResponse({'chatrooms': chatrooms})
