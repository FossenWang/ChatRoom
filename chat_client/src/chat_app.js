import React, { Component, Fragment } from 'react'

import { BrowserRouter as Router, Switch, Route } from "react-router-dom"

import { withStyles } from '@material-ui/core/styles'
import AppBar from '@material-ui/core/AppBar'
import Toolbar from '@material-ui/core/Toolbar'

import RoomList from './room_list'
import NoMatch from './no_match'


const appStyle = {
  '@global': {
    html: {
      fontSize: 16,
    },
    body: {
      margin: 0,
      fontFamily: '"Roboto", Helvetica, "Lucida Sans", "Microsoft YaHei", Georgia, Arial, Sans-serif',
    },
  },
  placeholder: {
    height: 56,
  }
}

class ChatApp extends Component {
  render() {
    return (
      <Router>
        <Fragment>
          <AppBar position="fixed" color="default">
            <Toolbar>Chat Room</Toolbar>
          </AppBar>
          <div className={this.props.classes.placeholder}></div>
          <Switch>
            <Route exact path='/' component={RoomList} />
            <Route component={NoMatch}/>
          </Switch>
        </Fragment>
      </Router>
    )
  }
}

ChatApp = withStyles(appStyle)(ChatApp)


export { ChatApp }
