import React, { Fragment } from 'react'

import AppBar from '@material-ui/core/AppBar'
import Toolbar from '@material-ui/core/Toolbar'


function Topbar(props) {
  return (
    <Fragment>
      <AppBar position="fixed" color="default">
        <Toolbar>{props.children}</Toolbar>
      </AppBar>
      <div style={{height: 64}} ></div>
    </Fragment>
  )
}


export default Topbar
