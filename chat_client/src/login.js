import React, { Component, createRef } from 'react'

import { withStyles } from '@material-ui/core/styles'
import Grid from '@material-ui/core/Grid'

import { Toast } from './utils'


const loginStyle = {
  container: {
    background: '#fff',
    margin: '100px auto',
    maxWidth: 360,
    border: '1px solid #eaeaea',
    borderRadius: 4,
    overflow: 'hidden',
  },
  header: {
    padding: 10,
    background: '#417690',
    color: 'white',
    textAlign: 'center',
    fontSize: 18,
  },
  form: {
    padding: 16,
  },
  label: {
    fontSize: 14,
    color: '#333',
    marginBottom: 4,
  },
  input: {
    padding: 8,
    marginBottom: 16,
    flex: 1,
    overflow: 'hidden',
    borderRadius: 4,
    border: '1px solid #eaeaea',
    fontSize: '1rem',
    fontFamily: '"Roboto", Helvetica, "Lucida Sans", "Microsoft YaHei", Georgia, Arial, Sans-serif',
  },
  submit: {
    cursor: 'pointer',
    borderRadius: 4,
    padding: '8px 16px',
    margin: 0,
    border: 0,
    background: '#417690',
    color: 'white',
    '&:hover': {
      background: '#1976d2',
    }
  }
}

class LoginPage extends Component {
  toastRef = createRef()
  onSubmit = (event) => {
    event.preventDefault()
    let username = event.target.username.value
    let password = event.target.password.value
    this.login(username, password)
  }
  login = async (username, password) => {
    let login = false
    try {
      let rsp = await fetch(
        'http://127.0.0.1:8000/api/csrf/',
        { credentials: 'include' }
      )
      let { csrftoken } = await rsp.json()
      let formData = new FormData()
      formData.append('username', username)
      formData.append('password', password)
      let url = 'http://127.0.0.1:8000/api/account/login/'
      rsp = await fetch(url, {
        method: 'POST',
        credentials: 'include',
        body: formData,
        headers: { 'x-csrftoken': csrftoken },
      })
      let data = await rsp.json()
      login = data.login
    } catch (error) {
      console.log(error)
    }
    if (login) {
      let { history, location } = this.props
      let next = location.search.replace('?next=', '')
      if (next.length === 0) {
        next = '/'
      }
      history.replace(next)
    } else {
      this.toastRef.current.open('登录失败~')
    }
  }
  render() {
    console.log(this.props.location)
    let { classes } = this.props
    return (
      <div className={classes.container}>
        <div className={classes.header}>
          登录
        </div>
        <Grid component='form' container direction='column'
          className={classes.form} onSubmit={this.onSubmit}>
          <div className={classes.label}>用户名:</div>
          <input className={classes.input}
            type="text" name="username" maxLength={150} required id="username" />
          <div className={classes.label}>密码:</div>
          <input className={classes.input}
            type="password" name="password" maxLength={128} required id="password" />
          <Grid container justify='center'>
            <input className={classes.submit} type='submit' value='登录' />
          </Grid>
        </Grid>
        <Toast ref={this.toastRef}></Toast>
      </div>
    )
  }
}


export default withStyles(loginStyle)(LoginPage)
