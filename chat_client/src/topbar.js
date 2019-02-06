import React, { Fragment } from 'react'

import AppBar from '@material-ui/core/AppBar'
import Toolbar from '@material-ui/core/Toolbar'


function Topbar(props) {
  return (
    <Fragment>
      <AppBar position="fixed" style={{background: '#417690'}}>
        <Toolbar>{props.children}</Toolbar>
      </AppBar>
      <div style={{height: props.height}} ></div>
    </Fragment>
  )
}


export default Topbar
