import React, { Component, Fragment, createRef } from 'react'

import List from '@material-ui/core/List'
import withStyles from '@material-ui/core/styles/withStyles'

import Topbar from './topbar'
import ChatMessage from './message'
import MessageForm from './message_form'
import { Toast, API_HOST } from './utils'


const roomStyle = {
  list: {
    minHeight: 'calc(100vh - 115px)',
    background: '#efefef',
  },
  fullWidth: { width: '100%' },
  roomName: { textAlign: 'center' },
  onlineNumber: {
    textAlign: 'center',
    fontSize: 12,
    color: '#f5f5f5'
  },
}

class Room extends Component {
  state = {
    room: {}, user: {}, messages: [],
    webSocketOpen: false, title: ''
  }
  toastRef = createRef()
  componentDidMount() {
    this.connectRoom()
  }
  componentWillUnmount() {
    this.disconnectRoom()
  }
  connectRoom = async () => {
    let url_room_id = this.props.match.params.id
    let chatSocket = new WebSocket(`ws://${API_HOST}/ws/chat/room/${url_room_id}/`)
    chatSocket.onclose = this.socketClose
    chatSocket.onmessage = this.socketMessage
    chatSocket.onopen = () => {
      this.sendMessage('Hello!')
      this.setState({webSocketOpen: true})
    }
    this.sendMessage = (message) => {
      chatSocket.send(JSON.stringify({
        'message': message
      }))
    }
    this.disconnectRoom = () => {
      chatSocket.close()
    }
  }
  disconnectRoom() { }
  sendMessage() { }
  socketMessage = (event) => {
    let data = JSON.parse(event.data)
    let handle = this.msgHandles[data.msg_type]
    if (handle !== undefined) {
      handle(data)
    }
  }
  msgHandles = {
    ERROR: 0,
    0: (data) => {
      let msg = `好像出了点问题: ${data.error}`
      this.toastRef.current.open(msg)
    },
    MESSAGE: 1,
    1: (data) => {
      if (data.message === undefined || data.user === undefined) {
        return
      }
      this.setState((state) => {
        state.messages.push(data)
        return { messages: state.messages }
      }, () => { window.scrollTo(0, document.documentElement.scrollHeight) })
    },
    USER_ROOM_INFO: 2,
    2: (data) => {
      let title = this.getRoomTitle(data.room)
      this.setState({ room: data.room, user: data.user, title: title})
    },
    JOIN_ROOM: 3,
    3: (data) => {
      let user = data.user
      if (user.id === this.state.user.id) { return }
      this.setState((state) => {
        state.room.onlineNumber = data.onlineNumber
        return { room: state.room, title: this.getRoomTitle(state.room) }
      })
      this.toastRef.current.open(`${user.username} 进入房间`)
    },
    LEAVE_ROOM: 4,
    4: (data) => {
      let user = data.user
      if (user.id === this.state.user.id) { return }
      this.setState((state) => {
        state.room.onlineNumber = data.onlineNumber
        return { room: state.room, title: this.getRoomTitle(state.room) }
      })
      this.toastRef.current.open(`${user.username} 离开房间`)
    },
  }
  socketClose = (event) => {
    let title
    if (event.code === this.close_codes.ROOM_NOT_EXIST) {
      title = '房间不存在'
    } else if (event.code === this.close_codes.ROOM_FULL) {
      title = '房间已满'
    } else if (event.code === this.close_codes.NOT_LOGIN) {
      title = '未登录'
      let { history, location } = this.props
      history.replace('/login?next=' + location.pathname)
      return
    } else if (event.code === this.close_codes.OTHER_LOGIN) {
      title = '在其他页面登录了聊天室'
    } else if (event.code === 1000) {
      return
    } else {
      title = '好像出了点问题~'
    }
    console.log(event, event.code)
    this.setState({webSocketOpen: false, title: title})
  }
  close_codes = {
    ROOM_NOT_EXIST: 3000,
    ROOM_FULL: 3001,
    NOT_LOGIN: 3002,
    OTHER_LOGIN: 3003,
  }
  getRoomTitle(room) {
    let { classes } = this.props
    return (
      <div className={classes.fullWidth}>
        <div className={classes.roomName}>
          {room.name}
        </div>
        <div className={classes.onlineNumber}>
          {`${room.onlineNumber}人在线${
          room.onlineNumber === room.maxNumber ? '(已满)' : ''}`}
        </div>
      </div>
    )
  }
  render() {
    let { messages, user, webSocketOpen, title } = this.state
    let messageList = messages.map((data, index) => {
      return (
        <ChatMessage key={index} message={data.message} time={data.time}
          user={data.user} isSelf={data.user.id === user.id} />
      )
    })
    return (
      <Fragment>
        <Topbar height={56}>
          {title}
        </Topbar>
        <List className={this.props.classes.list}>
          {messageList}
        </List>
        {webSocketOpen ? <MessageForm sendMessage={this.sendMessage} /> : null}
        <Toast ref={this.toastRef} />
      </Fragment>
    )
  }
}


export default withStyles(roomStyle)(Room)
