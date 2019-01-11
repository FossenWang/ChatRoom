from django.http import JsonResponse

from .consumers import room_manager
from .models import Room


def home(request):
    return JsonResponse('home', safe=False)


def chatroom_list(request):
    room_list = Room.objects.values()
    rooms = []
    for room in room_list:
        rooms.append({
            'id': room['id'],
            'name': room['name'],
            'onlineNumber': room_manager.get_online_number(room['id'])
        })
    return JsonResponse({'rooms': rooms})
