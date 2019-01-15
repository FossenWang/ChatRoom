import React from 'react'

import { withStyles } from '@material-ui/core/styles'
import Grid from '@material-ui/core/Grid'


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


export default NoMatch
