import React, { Component, Fragment, createRef } from 'react'

// import { Link } from "react-router-dom"

import List from '@material-ui/core/List'
import ListItem from '@material-ui/core/ListItem'
import ListItemText from '@material-ui/core/ListItemText'
// import { withStyles } from '@material-ui/core/styles'

import Topbar from './topbar'
import { Toast } from './utils/components'


class Room extends Component {
  state = {
    room: {}, user: {}, messages: []
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
    let chatSocket = new WebSocket(`ws://127.0.0.1:8000/ws/chat/room/${url_room_id}/`)
    chatSocket.onclose = this.socketClose
    chatSocket.onmessage = this.socketMessage
    window.chatSocket = chatSocket
    window.send = (message) => {
      chatSocket.send(JSON.stringify({
        'message': message
      }))
    }
    this.chatSocket = chatSocket
    this.disconnectRoom = ()=>{
      chatSocket.close()
    }
  }
  disconnectRoom() {}
  msgHandles = {
    ERROR: 0,
    0: (data) => {
      let msg = `好像出了点问题: ${data.error}`
      this.toastRef.current.open(msg)
    },
    MESSAGE: 1,
    1: (data) => {
      if (data.message === undefined || data.user === undefined){
        return
      }
      this.setState((state) => {
        state.messages.push(data)
        return {
          messages: state.messages
        }
      })
    },
    USER_ROOM_INFO: 2,
    2: (data) => {
      this.setState({room: data.room, user: data.user})
    },
    JOIN_ROOM: 3,
    3: (data) => {
      let user = data.user
      if (user.id === this.state.user.id) { return }
      let username = this.getUsername(user)
      this.setState((state) => {
        state.room.onlineNumber = data.onlineNumber
        return {room: state.room}
      })
      let msg = `${username} 进入房间`
      this.toastRef.current.open(msg)
    },
    LEAVE_ROOM: 4,
    4: (data) => {
      let user = data.user
      if (user.id === this.state.user.id) { return }
      let username = this.getUsername(user)
      this.setState((state) => {
        state.room.onlineNumber = data.onlineNumber
        return {room: state.room}
      })
      let msg = `${username} 离开房间`
      this.toastRef.current.open(msg)
    },
  }
  close_codes = {
    ROOM_NOT_EXIST: 3000,
    ROOM_FULL: 3001,
  }
  socketMessage = (event) => {
    let data = JSON.parse(event.data)
    let handle = this.msgHandles[data.msg_type]
    if (handle !== undefined) {
      handle(data)
    }
  }
  socketClose = (event) => {
    console.log(event)
  }
  getUsername(user) {
    let username = user.username
    if (user.isAnonymous) {
      username = `游客(${user.id})`
    }
    return username
  }
  render() {
    let { room, messages } = this.state
    let messageList = messages.map((data, index) => {
      return (
        <ListItem key={index} button>
          <div>
            <ListItemText>{data.message}</ListItemText>
            <ListItemText>{JSON.stringify(data.user)}</ListItemText>
          </div>
        </ListItem>
      )
    })
    return (
      <Fragment>
        <Topbar>{`${room.name}   ${room.onlineNumber}/${room.maxNumber}`}</Topbar>
        <List>{messageList}</List>
        <Toast ref={this.toastRef}></Toast>
      </Fragment>
    )
  }
}


export default Room
