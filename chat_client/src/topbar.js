import React, { Fragment } from 'react'

import AppBar from '@material-ui/core/AppBar'
import Toolbar from '@material-ui/core/Toolbar'
import withStyles from '@material-ui/core/styles/withStyles'


const style = {
  header: {
    background: '#417690',
    right: 'auto',
    '@media (min-width: 720px)': {
      maxWidth: 720,
      margin: '0px auto',
    },
  }
}

function Topbar(props) {
  return (
    <Fragment>
      <AppBar position="fixed" className={props.classes.header}>
        <Toolbar>{props.children}</Toolbar>
      </AppBar>
      <div style={{height: props.height}} ></div>
    </Fragment>
  )
}


export default withStyles(style)(Topbar)
