from django.http import JsonResponse
from .consumers import ChatRoom


def home(request):
    return JsonResponse('home', safe=False)


def chatroom_list(request):
    chatrooms = []
    for room in ChatRoom.rooms.values():
        chatrooms.append({
            'room': room.room_name,
            'count': room.get_online_number()
        })
    return JsonResponse({'chatrooms': chatrooms})
