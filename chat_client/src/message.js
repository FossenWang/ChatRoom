import React, { Component } from 'react'

import ListItem from '@material-ui/core/ListItem'
import Grid from '@material-ui/core/Grid'
import withStyles from '@material-ui/core/styles/withStyles'

import { UserAvatar } from './utils'


const messageStyle = {
  name: {
    fontSize: '0.85rem',
    marginBottom: 8,
    overflow: 'hidden',
    maxWidth: '100%',
    whiteSpace: 'nowrap',
  },
  bubble: {
    position: 'relative',
    margin: '0 12px',
    padding: '8px 10px',
    borderRadius: 5,
    background: 'white',
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
    borderRightColor: 'white',
  },
  right: {
    left: '100%',
    borderLeftWidth: 8,
    borderRightWidth: 0,
    borderLeftColor: 'white',
  },
  alignTop: {
    display: 'flex',
    alignItems: 'flex-start',
  },
}

class ChatMessage extends Component {
  getTimeString() {
    let time = new Date(this.props.time * 1000)
    let hour = time.getHours()
    let min = time.getMinutes()
    if (!hour || !min) { return }
    if (min < 10) { min = `0${min}` }
    time = `${hour}:${min}`
    return time
  }
  rightLayout() {
    let { user, message, classes } = this.props
    let time = this.getTimeString()
    return (
      <ListItem alignItems='flex-start'>
        <Grid container direction='column' justify='flex-end'
          alignItems='flex-end'>
          <div className={classes.name}>
            {time}&emsp;{user.username}
          </div>
          <div className={classes.alignTop}>
            <div className={classes.bubble}>
              <i className={`${classes.tail} ${classes.right}`} />
              {message}
            </div>
            <UserAvatar src={user.avatar}/>
          </div>
        </Grid>
      </ListItem>
    )
  }
  leftLayout() {
    let { user, message, classes } = this.props
    let time = this.getTimeString()
    return (
      <ListItem>
        <Grid container direction='column' justify='flex-end'
          alignItems='flex-start'>
          <div className={classes.name}>
            {user.username}&emsp;{time}
          </div>
          <div className={classes.alignTop}>
            <UserAvatar src={user.avatar}/>
            <div className={classes.bubble}>
              <i className={`${classes.tail} ${classes.left}`} />
              {message}
            </div>
          </div>
        </Grid>
      </ListItem>
    )
  }
  render() {
    return (this.props.isSelf ? this.rightLayout(): this.leftLayout())
  }
}


export default withStyles(messageStyle)(ChatMessage)
