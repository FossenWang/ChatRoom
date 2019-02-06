import React, { Component, Fragment } from 'react'

import { withStyles } from '@material-ui/core/styles'
import Grid from '@material-ui/core/Grid'
import Snackbar from '@material-ui/core/Snackbar'
import Avatar from '@material-ui/core/Avatar'
import Button from '@material-ui/core/Button'


const noMatchStyle = {
  item: {
    fontSize: 32,
    margin: '32px 0',
  }
}

let NoMatch = (props) => {
  return (
    <Grid container justify="center">
      <Grid item className={props.classes.item} >
        404
      </Grid>
    </Grid>
  )
}

NoMatch = withStyles(noMatchStyle)(NoMatch)


class Toast extends Component {
  state = {
    open: false,
    message: '',
    anchorOrigin: { vertical: 'top', horizontal: 'center' }
  }
  close = () => {
    this.setState({ open: false })
  }
  open = (msg, anchor) => {
    let change = { open: true, message: msg }
    if (anchor) {
      change.anchorOrigin = anchor
    }
    this.setState(change)
  }
  render() {
    return (
      <Snackbar
        anchorOrigin={this.state.anchorOrigin}
        open={this.state.open}
        onClose={this.close}
        autoHideDuration={2000}
        message={this.state.message} />
    )
  }
}


const userAvatarStyle = {
  img: {
    height: 36, width: 36
  }
}

let UserAvatar = (props) => {
  let { className, classes, src } = props
  if (className) {
    className = classes.img + ' ' + className
  } else {
    className = classes.img
  }
  return <Avatar
    src={src ? src : '/default_avatar.png'}
    className={className}  />
}
UserAvatar = withStyles(userAvatarStyle)(UserAvatar)


const userBarStyle = {
  username: {
    padding: '6px 8px',
  },
  button: {
    minWidth: 'unset',
    color: 'white',
  },
  avatar: {
    marginRight: 8,
  },
}

let UserBar = (props) => {
  let { user, classes } = props
  let rootProps = Object.assign({}, props)
  delete rootProps.user
  return (
    <Grid container alignItems='center' {...rootProps}>
      <UserAvatar src={user.avatar} className={classes.avatar} />
      {user.id ?
        <Fragment>
          <div className={classes.username}>
            {user.username}
          </div>
          <Button className={classes.button} onClick={props.logout}>
            注销
          </Button>
        </Fragment> :
        <Button className={classes.button} onClick={props.login}>
          登录
        </Button> }
    </Grid>
  )
}
UserBar = withStyles(userBarStyle)(UserBar)


export { NoMatch, Toast, UserAvatar, UserBar }
