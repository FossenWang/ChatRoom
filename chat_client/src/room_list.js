import React, { Component, Fragment } from 'react'

import { Link } from "react-router-dom"

import { withStyles } from '@material-ui/core/styles'
import List from '@material-ui/core/List'
import ListItem from '@material-ui/core/ListItem'
import ListItemText from '@material-ui/core/ListItemText'
import Button from '@material-ui/core/Button'
import Grid from '@material-ui/core/Grid'

import Topbar from './topbar'
import { UserAvatar } from './utils'


const roomListStyle = {
  item: {
    borderBottom: "1px solid #f4f5f7",
  },
  username: {
    padding: '6px 8px',
  },
  button: {
    minWidth: 'unset',
  },
}

class RoomList extends Component {
  state = { rooms: [], user: {} }
  componentDidMount() {
    this.fetchRooms()
    this.fetchUser()
  }
  fetchRooms = async () => {
    let url = 'http://127.0.0.1:8000/api/chat/rooms/'
    let rsp = await fetch(url)
    let data = await rsp.json()
    this.setState({
      rooms: data.rooms
    })
  }
  fetchUser = async () => {
    let url = 'http://127.0.0.1:8000/api/account/user/current/'
    let rsp = await fetch(url, {credentials: 'include'})
    let user = await rsp.json()
    this.setState({ user: user })
  }
  login = () => {
    let { history, location } = this.props
    history.push('/login?next=' + location.pathname)
  }
  logout = async () => {
    let url = 'http://127.0.0.1:8000/api/account/logout/'
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
        <Topbar>
          <Grid container alignItems='center'>
            <UserAvatar src={user.avatar} />
            {user.id ?
              <Fragment>
                <div className={classes.username}>{user.username}</div>
                <Button className={classes.button} onClick={this.logout}>注销</Button>
              </Fragment> :
              <Button onClick={this.login}>登录</Button> }
          </Grid>
        </Topbar>
        <List>
          {room_list}
        </List>
      </Fragment>
    )
  }
}


export default withStyles(roomListStyle)(RoomList)
