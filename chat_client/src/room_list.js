import React, { Component } from 'react'
import List from '@material-ui/core/List'
import ListItem from '@material-ui/core/ListItem'
import ListItemText from '@material-ui/core/ListItemText'
import { Link } from "react-router-dom"


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
        <ListItem key={room.id} button component={Link} to={`/chat/room/${room.id}`}>
          <ListItemText primary={room.name} secondary={`${room.onlineNumber}人在线`} />
        </ListItem>
      )
    })
    return (
      <List>
        {room_list}
      </List>
    )
  }
}


export default RoomList
