import logo from './logo.svg';
import './App.css';
import LandingPage from './components/LandingPage';

import MonacoEditorComponent from "./components/Monaco_editor";
import CustomizedTreeView from "./components/CustomizedTreeView";
function App() {
  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <dir>
         <CustomizedTreeView />
        </dir>
        <dir>
         <MonacoEditorComponent />
        </dir>
        <p>
          Edit <code>src/App.js</code> and save to reload.
        </p>
        <a
          className="App-link"
          href="https://reactjs.org"
          target="_blank"
          rel="noopener noreferrer"
        >
          Learn React
        </a>
      </header>
    </div>
  );
}

export default App;
