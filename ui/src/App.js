import React, { Component } from 'react';
/*import logo from './logo.svg';*/
import './App.css';
import API from './API';

var appletRegistry = {};

class Applet extends Component {
  constructor(props) {
    super(props);
    this.state = {
      api: new API('http://localhost:8000/')
    };
  }

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
          <button onClick={this.onPlayClicked.bind(this)}>Play</button>
          <button onClick={this.onStopClicked.bind(this)}>Stop</button>
        </div>
      } />
    );
  }

  onPlayClicked(proxy, e) {
    this.state.api.post('music/play')
    .then((resp) => {});
  }

  onStopClicked(proxy, e) {
    this.state.api.post('music/stop')
    .then((resp) => {});
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
