import React, { Component, Fragment } from 'react'

import { BrowserRouter as Router, Switch, Route } from "react-router-dom"

import { withStyles } from '@material-ui/core/styles'

import RoomList from './room_list'
import Room from './room'
import LoginPage from './login'
import { NoMatch } from './utils'


const appStyle = {
  '@global': {
    html: {
      fontSize: 16,
    },
    body: {
      background: '#f8f8f8',
      margin: 0,
      fontFamily: '"Roboto", Helvetica, "Lucida Sans", "Microsoft YaHei", Georgia, Arial, Sans-serif',
    },
  },
}

class ChatApp extends Component {
  render() {
    return (
      <Router>
        <Fragment>
          <Switch>
            <Route exact path='/' component={RoomList} />
            <Route exact path='/room/:id(\d+)' component={Room} />
            <Route exact path='/login' component={LoginPage} />
            <Route component={NoMatch}/>
          </Switch>
        </Fragment>
      </Router>
    )
  }
}

ChatApp = withStyles(appStyle)(ChatApp)


export { ChatApp }
