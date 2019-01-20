import React, { Component, Fragment, createRef } from 'react'

// import { Link } from "react-router-dom"

import List from '@material-ui/core/List'
import ListItem from '@material-ui/core/ListItem'
import Grid from '@material-ui/core/Grid'
import Button from '@material-ui/core/Button'
import { withStyles } from '@material-ui/core/styles'

import Topbar from './topbar'
import { Toast } from './utils/components'


const messageStyle = {
  name: {
    fontSize: '0.5rem',
    marginBottom: 8,
  },
  bubble: {
    position: 'relative',
    margin: '0 8px',
    padding: '8px 10px',
    borderRadius: 5,
    background: '#f6f8fa',
    wordBreak: 'break-word',
    whiteSpace: 'pre-wrap',
    width: 'fit-content',
  },
  tail: {
    position: 'absolute',
    top: 11,
    borderWidth: 5,
    borderStyle: 'solid',
    borderColor: 'transparent',
  },
  left: {
    right: '100%',
    borderRightWidth: 8,
    borderLeftWidth: 0,
    borderRightColor: '#f6f8fa',
  },
  right: {
    left: '100%',
    borderLeftWidth: 8,
    borderRightWidth: 0,
    borderLeftColor: '#f6f8fa',
  },
}

class ChatMessage extends Component {
  render() {
    let { user, message, isSelf, classes } = this.props
    return (
      <ListItem>
        <Grid container direction='column' justify='flex-end' alignItems={isSelf ? 'flex-end' : 'flex-start'}>
          <div className={classes.name}>
            {user.username}
          </div>
          <div className={classes.bubble}>
            <i className={`${classes.tail} ${isSelf ? classes.right : classes.left}`} />
            {message}
          </div>
        </Grid>
      </ListItem>
    )
  }
}

ChatMessage = withStyles(messageStyle)(ChatMessage)

const fieldStyle = {
  form: {
    padding: 8,
    background: '#f5f5f5',
    width: 'calc(100% - 16px)',
    position: 'fixed',
    bottom: 0,
  },
  text: {
    padding: '4px 8px',
    margin: 'auto 8px auto 0',
    flex: 1,
    overflow: 'hidden',
    resize: 'none',
    borderRadius: 4,
    border: 'none',
    lineHeight: '18px',
    fontSize: '1rem',
    fontFamily: '"Roboto", Helvetica, "Lucida Sans", "Microsoft YaHei", Georgia, Arial, Sans-serif',
  },
  baseButton: {
    borderRadius: 4,
    padding: 0,
    minWidth: 48,
    height: 'fit-content',
  },
  enabledButton: {
    background: '#2196f3',
    color: 'white',
    '&:hover': {
      background: '#1976d2',
    }
  }
}

class MessageField extends Component {
  state = { value: '', rows: 1, formHeight: 42 }
  handleChange = (event) => {
    let textarea = event.target
    textarea.rows = 1
    let textRows = Math.ceil((textarea.scrollHeight - 8) / 18)
    if (textRows > 5) { textarea.rows = 5 }
    else { textarea.rows = textRows }
    this.setState({ value: textarea.value, rows: textarea.rows, formHeight: textarea.clientHeight + 16 })
  }
  submitMessage = (event) => {
    let value = this.textareaRef.current.value
    if (this.validate(value)) {
      this.props.sendMessage(value)
      let textarea = this.textareaRef.current
      textarea.value = ''
      textarea.rows = 1
      this.setState({ value: textarea.value, rows: textarea.rows, formHeight: textarea.clientHeight + 16 })
    }
  }
  validate(value) {
    let valid = value.length > 0 && value.length <= 500
    if (!valid) { return valid }
    valid = value.search('^[\\s\\f\\r\\t\\n]*$') < 0
    return valid
  }
  textareaRef = createRef()
  render() {
    let { classes } = this.props
    let { value, rows, formHeight } = this.state
    let valueIsValid = this.validate(value)
    let buttonProps = valueIsValid
      ? { disabled: false, className: classes.baseButton + ' ' + classes.enabledButton }
      : { disabled: true, className: classes.baseButton }
    return (
      <Fragment>
        <div style={{ height: formHeight }}></div>
        <form className={classes.form}>
          <Grid container alignItems={'center'}>
            <textarea className={classes.text} onChange={this.handleChange}
              required name='message' rows={rows} maxLength={500} ref={this.textareaRef} />
            <Button onClick={this.submitMessage} {...buttonProps}>确认</Button>
          </Grid>
        </form>
      </Fragment>
    )
  }
}

MessageField = withStyles(fieldStyle)(MessageField)


const roomStyle = {
}

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
    this.sendMessage = (message) => {
      chatSocket.send(JSON.stringify({
        'message': message
      }))
    }
    window.chatSocket = chatSocket
    window.send = this.sendMessage  //!!!!!!!!!!!!!
    chatSocket.onopen = () => { window.send('Hello!') }
    this.chatSocket = chatSocket
    this.disconnectRoom = () => {
      chatSocket.close()
    }
  }
  disconnectRoom() { }
  sendMessage() { }
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
      this.setState({ room: data.room, user: data.user })
    },
    JOIN_ROOM: 3,
    3: (data) => {
      let user = data.user
      if (user.id === this.state.user.id) { return }
      this.setState((state) => {
        state.room.onlineNumber = data.onlineNumber
        return { room: state.room }
      })
      this.toastRef.current.open(`${user.username} 进入房间`)
    },
    LEAVE_ROOM: 4,
    4: (data) => {
      let user = data.user
      if (user.id === this.state.user.id) { return }
      this.setState((state) => {
        state.room.onlineNumber = data.onlineNumber
        return { room: state.room }
      })
      this.toastRef.current.open(`${user.username} 离开房间`)
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
  render() {
    let { room, messages, user } = this.state
    let messageList = messages.map((data, index) => {
      return (
        <ChatMessage key={index} message={data.message}
          user={data.user} isSelf={data.user.id === user.id} />
      )
    })
    return (
      <Fragment>
        <Topbar>{`${room.name}   ${room.onlineNumber}/${room.maxNumber}`}</Topbar>
        <List>{messageList}</List>
        <MessageField sendMessage={this.sendMessage} />
        <Toast ref={this.toastRef}></Toast>
      </Fragment>
    )
  }
}


export default withStyles(roomStyle)(Room)
