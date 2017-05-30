import React, { Component } from 'react';
import './App.css';
import API from './API';

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
  constructor(props) {
    super(props);
    this.state = {
      musicData: {}
    }
  }

  render () {
    return (
      <Applet name='music' content={
        <div>
          <ul>
          {
            Object.keys(this.state.musicData).map((k) => {
              var v = this.state.musicData[k];
              return <li key={k}>{k}: {v}</li>
            })
          }
          </ul>
          <input ref="query" type="text"></input>
          <button onClick={this.onPlayClicked.bind(this)}>Play</button>
          <button onClick={this.onStopClicked.bind(this)}>Stop</button>
        </div>
      } />
    );
  }

  componentDidMount() {
    this.props.api.get('music')
    .then((data) => {
      this.setState((prev, props) => {
        return {
          musicData: data
        }
      })
    });
  }

  onPlayClicked(proxy, e) {
    var query = this.refs.query.value;
    var params = {}
    if (query) {
      params['query'] = query;
    }

    this.props.api.post('music/play', params)
    .then((resp) => {});
  }

  onStopClicked(proxy, e) {
    this.props.api.post('music/stop')
    .then((resp) => {});
  }


}
appletRegistry['music'] = Music;


class App extends Component { 
  constructor(props) {
    super(props);
    this.state = {
      cards: [],
      api: new API('http://localhost:8000/')
    };
  }

  render() {
    return (
      <div className="App">
        <div className="App-header">
          <h2>Welcome to Housekeeper</h2>
        </div>
        <p className="App-intro">
          To get started, edit <code>src/App.js</code> and save to reload.
        </p>
        <div className="Container">
        {
          this.state.cards
          .map((x) => {
            var type = appletRegistry[x];
            return React.createElement(type, {key: x, api: this.state.api});
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
        var cardNames = Object.keys(data)
        .filter((x) => {
            return x.indexOf('/') === -1;
        })
        .filter((x) => {
            return x in appletRegistry;
        })

        this.setState((prevState, props) => {
          return {
            'api': prevState.api,
            'cards': cardNames
          }
        });
    });
  }

}

export default App;
