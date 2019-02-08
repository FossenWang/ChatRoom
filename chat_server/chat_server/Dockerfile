FROM python:3.7

LABEL maintainer="Fossen"

EXPOSE 8080
VOLUME [ "/home/fossen/ChatRoom" ]
WORKDIR /home/fossen/ChatRoom/chat_server
CMD [ "/bin/bash", "pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/; daphne -b 0.0.0.0 -p 8080 chat_server.asgi:application" ]


# cd /home/fossen/ChatRoom
# sudo docker build -t chatdemo .
# sudo docker run -d --network host --restart=always --name chatdemo -v /home/fossen/ChatRoom:/home/fossen/ChatRoom fossensite
# sudo docker restart chatdemo
