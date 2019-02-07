import React, { Component, Fragment } from 'react'

import { Link } from "react-router-dom"

import withStyles from '@material-ui/core/styles/withStyles'
import List from '@material-ui/core/List'
import ListItem from '@material-ui/core/ListItem'
import ListItemText from '@material-ui/core/ListItemText'

import Topbar from './topbar'
import { UserBar, API_HOST } from './utils'


const roomListStyle = {
  list: {
    minHeight: 'calc(100vh - 72px)',
    background: 'white',
  },
  item: {
    borderBottom: "1px solid #f4f5f7",
  },
}

class RoomList extends Component {
  state = { rooms: [], user: {} }
  componentDidMount() {
    this.fetchRooms()
    this.fetchUser()
  }
  fetchRooms = async () => {
    let url = `http://${API_HOST}/api/chat/rooms/`
    let rsp = await fetch(url)
    let data = await rsp.json()
    this.setState({
      rooms: data.rooms
    })
  }
  fetchUser = async () => {
    let url = `http://${API_HOST}/api/account/user/current/`
    let rsp = await fetch(url, {credentials: 'include'})
    let user = await rsp.json()
    this.setState({ user: user })
  }
  login = () => {
    let { history, location } = this.props
    history.push('/login?next=' + location.pathname)
  }
  logout = async () => {
    let url = `http://${API_HOST}/api/account/logout/`
    let rsp = await fetch(url, {credentials: 'include'})
    let data = await rsp.json()
    if (data.logout) {
      this.setState({ user: {} })
    }
  }
  render() {
    let { classes } = this.props
    let { rooms, user } = this.state
    let room_list = rooms.map((room) => {
      return (
        <ListItem key={room.id} button className={classes.item}
          component={Link} to={`/room/${room.id}`}>
          <ListItemText primary={room.name} secondary={`${room.onlineNumber}人在线`} />
        </ListItem>
      )
    })
    return (
      <Fragment>
        <Topbar height={56}>
          <UserBar user={user} login={this.login} logout={this.logout} />
        </Topbar>
        <List className={classes.list}>
          {room_list}
        </List>
      </Fragment>
    )
  }
}


export default withStyles(roomListStyle)(RoomList)
