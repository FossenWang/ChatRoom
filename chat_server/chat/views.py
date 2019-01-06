from django.http import JsonResponse
from channels.layers import get_channel_layer


channel_layer = get_channel_layer()


def home(request):
    return JsonResponse('home', safe=False)


# import channels.layers.InMemoryChannelLayer
def chatroom_list(request):
    chatrooms = []
    for group in channel_layer.groups:
        if group.startswith('chat_'):
            room = group.replace('chat_', '', 1)
        chatrooms.append({
            'room': room,
            'count': len(channel_layer.groups[group])
        })
    return JsonResponse({'chatrooms': chatrooms})
