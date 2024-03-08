import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import HomePage from './components/HomePage';
import LandingPage from './components/LandingPage';
import AboutPage from './components/AboutPage';
import ContactPage from './components/ContactPage';
import NotFoundPage from './components/NotFoundPage';
import Header from './components/Header';
import Footer from './components/Footer';

function App() {
  return (
    <Router>
      <div className="App">
        <Header />
        <Switch>
          <Route exact path="/" component={HomePage} />
          <Route path="/about" component={AboutPage} />
          <Route path="/contact" component={ContactPage} />
          <Route component={NotFoundPage} />
        </Switch>
        <div className="App">
      <h1>Welcome to My App</h1>
      <CustomButton />
    </div>
        <Footer />
      </div>
    </Router>
  );
}



export default App;

