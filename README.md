# [ChatRoom](http://chatdemo.fossen.cn/)
该项目基于websocket开发，实现了简单的多人即时通讯，项目的

* 后端基于[django](https://www.djangoproject.com/)和[channels](https://channels.readthedocs.io/en/latest/)开发，
使用[daphne](https://github.com/django/daphne/)做asgi服务器，
通过异步的websocket实现与前端的通信

* 前端基于[react](https://reactjs.org/)开发，
[material-ui](https://material-ui.com/)作为ui库，
使用了[jsx](https://reactjs.org/docs/introducing-jsx.html)和[jss](https://github.com/cssinjs/jss)技术，html与css统一用js编写，
页面路由通过[react-router](https://reacttraining.com/react-router/web/guides/quick-start)实现
