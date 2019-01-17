import React, { Fragment } from 'react'

import { withStyles } from '@material-ui/core/styles'
import AppBar from '@material-ui/core/AppBar'
import Toolbar from '@material-ui/core/Toolbar'


const topbarStyle = {
  placeholder: {
    height: 56,
  }
}

function Topbar(props) {
  return (
    <Fragment>
      <AppBar position="fixed" color="default">
        <Toolbar>{props.children}</Toolbar>
      </AppBar>
      <div className={props.classes.placeholder}></div>
    </Fragment>
  )
}


export default withStyles(topbarStyle)(Topbar)
