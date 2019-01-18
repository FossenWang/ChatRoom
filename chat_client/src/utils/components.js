import React, { Component } from 'react'

import { withStyles } from '@material-ui/core/styles'
import Grid from '@material-ui/core/Grid'
import Snackbar from '@material-ui/core/Snackbar'


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


export { NoMatch, Toast }
