import React, { Component } from 'react'

// import { Link } from "react-router-dom"

import Topbar from './topbar'


class Room extends Component {
  state = {
    room: {}, user: {}, messages: {}
  }
  componentDidMount() {
    this.connectRoom()
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
  }
  msgHandles = {
    0: (data) => {
      console.log(data)
    },
    1: (data) => {
      console.log(data)
    },
    2: (data) => {
      console.log(data)
    },
    3: (data) => {
      console.log(data)
    },
    4: (data) => {
      console.log(data)
    },
    ERROR: 0,
    MESSAGE: 1,
    USER_ROOM_INFO: 2,
    JOIN_ROOM: 3,
    LEAVE_ROOM: 4,
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
  render() {
    return (
      <Topbar>{this.state.room.name}</Topbar>
    )
  }
}


export default Room
