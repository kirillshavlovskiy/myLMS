import logo from './logo.svg';
import './App.css';
import LandingPage from './components/LandingPage';
import CodeMirror from "@uiw/react-codemirror";
import Editor from "@monaco-editor/react";

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <dir>
         <Editor
              height="500px"
              width="700px"
              language="python"
              theme="vs-dark"
              value=""
            />
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
