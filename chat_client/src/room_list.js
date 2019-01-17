import React, { Component, Fragment } from 'react'

import { Link } from "react-router-dom"

import List from '@material-ui/core/List'
import ListItem from '@material-ui/core/ListItem'
import ListItemText from '@material-ui/core/ListItemText'
import { withStyles } from '@material-ui/core/styles'

import Topbar from './topbar'


const roomListStyle = {
  item: {
    borderBottom: "1px solid #f4f5f7",
  }
}

class RoomList extends Component {
  state = { rooms: [] }
  componentDidMount() {
    this.fetchRooms()
  }
  fetchRooms = async () => {
    let url = 'http://127.0.0.1:8000/api/chat/rooms/'
    let rsp = await fetch(url)
    let data = await rsp.json()
    this.setState({
      rooms: data.rooms
    })
  }
  render() {
    let room_list = this.state.rooms.map((room) => {
      return (
        <ListItem key={room.id} button className={this.props.classes.item}
          component={Link} to={`/room/${room.id}`}>
          <ListItemText primary={room.name} secondary={`${room.onlineNumber}人在线`} />
        </ListItem>
      )
    })
    return (
      <Fragment>
        <Topbar>Chat Room</Topbar>
        <List>
          {room_list}
        </List>
      </Fragment>
    )
  }
}


export default withStyles(roomListStyle)(RoomList)
