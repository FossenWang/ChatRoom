import React, { Component, Fragment, createRef } from 'react'

import Grid from '@material-ui/core/Grid'
import Button from '@material-ui/core/Button'
import { withStyles } from '@material-ui/core/styles'


const formStyle = {
  form: {
    padding: 8,
    borderTop: 'solid 1px #e0e0e0',
    background: '#f5f5f5',
    width: 'calc(100% - 16px)',
    position: 'fixed',
    bottom: 0,
  },
  text: {
    padding: '4px 8px',
    margin: 'auto 8px auto 0',
    flex: 1,
    overflow: 'hidden',
    resize: 'none',
    borderRadius: 4,
    border: 'none',
    lineHeight: '18px',
    fontSize: '1rem',
    fontFamily: '"Roboto", Helvetica, "Lucida Sans", "Microsoft YaHei", Georgia, Arial, Sans-serif',
  },
  baseButton: {
    borderRadius: 4,
    padding: 0,
    minWidth: 48,
    height: 'fit-content',
  },
  enabledButton: {
    background: '#2196f3',
    color: 'white',
    '&:hover': {
      background: '#1976d2',
    }
  }
}

class MessageForm extends Component {
  state = { value: '', textareaHeight: 18, formHeight: 42 }
  textareaRef = createRef()
  handleChange = (event) => {
    let textarea = event.target
    textarea.style.height = ''
    let textareaHeight = textarea.scrollHeight - 8
    if (textareaHeight > 90) { textareaHeight = 90 }
    textarea.style.height = `${textareaHeight}px`
    this.setState({
      value: textarea.value,
      textareaHeight: textareaHeight,
      formHeight: textareaHeight + 16
    })
  }
  submitMessage = (event) => {
    let value = this.textareaRef.current.value
    if (this.validate(value)) {
      this.props.sendMessage(value)
      // reset form value
      let textarea = this.textareaRef.current
      textarea.value = ''
      textarea.style.height = ''
      this.setState({ value: '', textareaHeight: 18, formHeight: 42 })
    }
  }
  validate(value) {
    let valid = value.length > 0 && value.length <= 500
    if (!valid) { return valid }
    valid = value.search('^[\\s\\f\\r\\t\\n]*$') < 0
    return valid
  }
  render() {
    window.textarea = this.textareaRef
    let { classes } = this.props
    let { value, textareaHeight, formHeight } = this.state
    let valueIsValid = this.validate(value)
    let buttonProps = valueIsValid
      ? { disabled: false, className: classes.baseButton + ' ' + classes.enabledButton }
      : { disabled: true, className: classes.baseButton }
    return (
      <Fragment>
        <div style={{ height: formHeight }}></div>
        <form className={classes.form}>
          <Grid container alignItems={'center'}>
            <textarea className={classes.text} onChange={this.handleChange}
              required name='message' maxLength={500} ref={this.textareaRef} rows={1}
              style={{height: textareaHeight}} />
            <Button onClick={this.submitMessage} {...buttonProps}>确认</Button>
          </Grid>
        </form>
      </Fragment>
    )
  }
}


export default withStyles(formStyle)(MessageForm)
