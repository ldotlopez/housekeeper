import React, { Component } from 'react';
import logo from './logo.svg';
import './App.css';

var appletRegistry = {};

class Applet extends Component {
  render() {
    return (
      <div className={this.props.name}>
        <div className="Applet-title">{this.props.name}</div>
        <div className="Applet-content">{this.props.content}</div>
      </div>
    );
  }
}

class Music extends Applet {
  render () {
    return (
      <Applet name='music' content={
        <div>
          <input type="text"></input>
          <button onClick={this.onPlayClicked}>Play</button>
          <button onClick={this.onStopClicked}>Stop</button>
        </div>
      } />
    );
  }

  onPlayClicked(proxy, e) {
    fetch('http://localhost:8000/music/play', {
      method: 'POST',
      body: JSON.stringify({}),
      headers: new Headers({
        'Content-Type': 'application/json'
      })
    })
    .then((resp) => { return resp.json()})
    .then((data) => {});
  }

  onStopClicked(proxy, e) {
    fetch('http://localhost:8000/music/stop', {
      method: 'POST',
      body: JSON.stringify({}),
      headers: new Headers({
        'Content-Type': 'application/json'
      })
    })
    .then((resp) => { return resp.json()})
    .then((data) => {});
  }


}
appletRegistry['music'] = Music;


class App extends Component { 
  constructor(props) {
    super(props);
    this.state = {
      cards: []
    };
  }

  render() {
    return (
      <div className="App">
        <div className="App-header">
{/*          <!-- <img src={logo} className="App-logo" alt="logo" /> -->
*/}          <h2>Welcome to Housekeeper</h2>
        </div>
        <p className="App-intro">
          To get started, edit <code>src/App.js</code> and save to reload.
        </p>
        <div className="Container">
        {
          this.state.cards.map(function(x) {
            var type = appletRegistry[x];
            return React.createElement(type, {key: x});
          })
        }
        </div>
      </div>
    );
  }

  componentDidMount() {
    this.loadApplets();
  }

  loadApplets() {
    fetch('http://localhost:8000/_/')
    .then((resp) => {
        return resp.json()
    })
    .then((data) => {
        var cardNames = Object.keys(data);
        cardNames = cardNames.filter(function(x) {
            return x.indexOf('/') === -1;
        });
        this.setState((prevState, props) => {
          return {'cards': cardNames}
        });
    });
  }

}

export default App;
